FROM python:3.10-slim

# Paquets système utiles pour compiler des wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dépendances Python
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Code de l'app
COPY . .

# (Optionnel) Entraînement du modèle au build
RUN rasa train

EXPOSE 5005
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
