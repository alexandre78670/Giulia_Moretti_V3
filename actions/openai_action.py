import os
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType


def _get_openai_client():
    # Lazy import to keep action server light if OpenAI isn't needed during tests
    try:
        from openai import OpenAI  # type: ignore
    except Exception as import_error:  # pragma: no cover
        raise RuntimeError(
            "OpenAI SDK is not installed. Please add 'openai' to your action server dependencies."
        ) from import_error

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")

    return OpenAI(api_key=api_key)


def _build_conversation_history(tracker: Tracker, max_turns: int = 6) -> List[Dict[str, str]]:
    # Collect recent user and bot messages for short-term memory
    events = tracker.events
    messages: List[Dict[str, str]] = []
    for e in events:
        if e.get("event") == "user" and e.get("text"):
            messages.append({"role": "user", "content": e["text"]})
        elif e.get("event") == "bot" and e.get("text"):
            messages.append({"role": "assistant", "content": e["text"]})

    # Keep only the last max_turns*2 messages (user+assistant pairs)
    if len(messages) > max_turns * 2:
        messages = messages[-max_turns * 2 :]
    return messages


class ActionOpenAIResponse(Action):
    def name(self) -> Text:
        return "action_openai_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        user_message = tracker.latest_message.get("text", "")

        system_prompt = (
            "Tu es Giulia, une assistante IA conversationnelle. Réponds de façon naturelle, concise, "
            "utile et contextuelle, sans réponses scriptées. Pose des questions pertinentes si nécessaire, "
            "et garde un ton empathique et professionnel."
        )

        history = _build_conversation_history(tracker)
        messages = [{"role": "system", "content": system_prompt}] + history
        if user_message:
            messages.append({"role": "user", "content": user_message})

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        try:
            client = _get_openai_client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "500")),
            )
            text = response.choices[0].message.content.strip() if response.choices else ""
            if not text:
                text = (
                    "Désolé, je n'ai pas pu générer de réponse pour le moment. Peux-tu reformuler ?"
                )
        except Exception as e:  # pragma: no cover
            text = (
                "Un souci est survenu avec la génération de réponse. On réessaie ? (détail: "
                f"{type(e).__name__})"
            )

        dispatcher.utter_message(text=text)
        return []


