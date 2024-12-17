from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions
import requests

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Route pour afficher le fichier index.html
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Configuration Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string("<connection_string>")
blob_container_name = "files"

# Configuration Azure Cosmos DB
cosmos_connection_string = "<cosmos_connection_string>"
cosmos_client = CosmosClient.from_connection_string(cosmos_connection_string)
cosmos_database_name = "nutriai"
cosmos_container_name = "userdata"

cosmos_database = cosmos_client.get_database_client(cosmos_database_name)
cosmos_container = cosmos_database.get_container_client(cosmos_container_name)

# Configuration Azure Translator
translator_endpoint = "https://api.cognitive.microsofttranslator.com/translate"
translator_key = "<translator_key>"
translator_region = "westeurope"

# Configuration Azure Custom Vision
custom_vision_url = "https://nutriaivision-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/<project_id>/classify/iterations/<iteration_id>/image"
custom_vision_key = "<custom_vision_key>"

# Route pour tester la connexion avec le backend
@app.route("/test", methods=["GET"])
def test_backend():
    return jsonify({"message": "Backend connecté avec succès !"})

# Route pour sauvegarder les données utilisateur dans Cosmos DB
@app.route("/saveuserdata", methods=["POST"])
def save_user_data():
    user_data = request.get_json()

    # Préparer les données à sauvegarder
    data_to_save = {
        "id": user_data.get("goal", "default-id"),  # Utiliser un objectif unique comme ID
        "goal": user_data["goal"],
        "allergies": user_data["allergies"],
        "preferences": user_data["preferences"]
    }

    try:
        # Sauvegarder dans Cosmos DB
        cosmos_container.create_item(body=data_to_save)
        return jsonify({"message": "Données sauvegardées avec succès dans Cosmos DB !"})
    except exceptions.CosmosResourceExistsError:
        return jsonify({"error": "Données déjà existantes avec cet ID."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour uploader un fichier dans Blob Storage
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files['file']
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=file.filename)

    try:
        # Uploader le fichier
        blob_client.upload_blob(file, overwrite=True)
        return jsonify({"message": f"Fichier '{file.filename}' uploadé avec succès dans Azure Blob Storage !"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour générer un résumé basé sur les données utilisateur
@app.route("/getsummary", methods=["POST"])
def get_summary():
    user_data = request.get_json()

    # Générer un résumé simple
    goal = user_data.get("goal", "Aucun objectif spécifié")
    allergies = user_data.get("allergies", "Aucune allergie spécifiée")
    preferences = user_data.get("preferences", "Aucune préférence spécifiée")

    summary = (
        f"Objectif : {goal}. Allergies : {allergies}. "
        f"Préférences alimentaires : {preferences}."
    )

    return jsonify({"summary": summary})

# Route pour traduire le résumé via Azure Translator
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text_to_translate = data.get("text", "Aucun texte fourni.")
    target_language = data.get("language", "en")

    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        "Ocp-Apim-Subscription-Region": translator_region,
        "Content-Type": "application/json",
    }
    params = {
        "api-version": "3.0",
        "to": target_language,
    }
    body = [{"text": text_to_translate}]

    try:
        # Appeler l'API Translator
        response = requests.post(translator_endpoint, headers=headers, params=params, json=body)
        response.raise_for_status()
        translated_text = response.json()[0]["translations"][0]["text"]

        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour analyser une image via Azure Custom Vision
@app.route("/analyzeimage", methods=["POST"])
def analyze_image():
    file = request.files['file']  # Récupérer l'image uploadée
    headers = {
        'Prediction-Key': custom_vision_key,
        'Content-Type': 'application/octet-stream'
    }

    try:
        # Envoyer l'image à l'API Custom Vision
        response = requests.post(custom_vision_url, headers=headers, data=file.read())
        response.raise_for_status()
        results = response.json()

        # Debug : Afficher toutes les prédictions dans le terminal
        print("Debug - Résultats API :", results)

        # Extraire les aliments reconnus avec une probabilité > 0.7
        recognized_items = [
            prediction["tagName"]
            for prediction in results["predictions"]
            if prediction["probability"] > 0.7
        ]

        return jsonify({"recognized_items": recognized_items})
    except Exception as e:
        # Debug : Afficher les erreurs dans le terminal
        print("Debug - Erreur :", str(e))
        return jsonify({"error": str(e)}), 500


# Route pour générer des conseils nutritionnels
@app.route("/nutritionadvice", methods=["POST"])
def nutrition_advice():
    data = request.get_json()
    recognized_items = data.get("recognized_items", [])
    print("Debug - Aliments reçus :", recognized_items)  # Debug pour afficher les aliments reçus
    advice = []

    # Logique de conseils nutritionnels
    if "Healthy food" in recognized_items:
        advice.append("Healthy food : Mangez des aliments riches en nutriments pour maintenir une bonne santé.")
    if "Healthy dishes" in recognized_items:
        advice.append("Healthy dishes : Privilégiez les plats équilibrés riches en légumes et en protéines maigres.")
    if "pomme" in recognized_items:
        advice.append("Les pommes sont riches en fibres et idéales pour un en-cas sain.")

    # Message par défaut si aucun aliment n'est reconnu
    if not advice:
        advice.append("Veuillez ajouter une image contenant un aliment reconnaissable pour recevoir des conseils.")

    return jsonify({"advice": advice})


# Lancer l'application Flask
if __name__ == "__main__":
    app.run(debug=True)
