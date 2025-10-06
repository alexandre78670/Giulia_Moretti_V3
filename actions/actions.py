# Ce fichier contient vos actions personnalisées pour exécuter du code Python.
#
# Consultez ce guide pour implémenter des actions :
# https://rasa.com/docs/rasa/custom-actions


# Exemple simple d'une action personnalisée qui dit « Bonjour ! »

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionDireBonjour(Action):
#
#     def name(self) -> Text:
#         return "action_dire_bonjour"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Bonjour !")
#
#         return []
