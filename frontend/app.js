// Bouton de test pour vérifier la connexion avec le backend
const testButton = document.getElementById('testButton');
const responseElement = document.getElementById('response');

testButton.addEventListener('click', async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/test');
        const data = await response.json();
        responseElement.textContent = data.message;
    } catch (error) {
        responseElement.textContent = 'Erreur de communication avec le backend.';
        console.error(error);
    }
});

// Gestion du formulaire des informations utilisateur
const userForm = document.getElementById('userForm');
const formResponseElement = document.getElementById('formResponse');

userForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Empêche le rechargement de la page
    const formData = new FormData(userForm);
    const userData = Object.fromEntries(formData.entries()); // Convertir FormData en objet

    try {
        const response = await fetch('http://127.0.0.1:5000/saveuserdata', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        const result = await response.json();
        formResponseElement.textContent = result.message || 'Données reçues avec succès !';
    } catch (error) {
        formResponseElement.textContent = 'Erreur lors de l\'envoi des données.';
        console.error(error);
    }
});

// Gestion de l'upload de fichiers
const uploadForm = document.getElementById('uploadForm');
const uploadResponseElement = document.getElementById('uploadResponse');

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Empêche le rechargement de la page
    const formData = new FormData(uploadForm);

    try {
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        uploadResponseElement.textContent = result.message || result.error || 'Upload réussi !';
    } catch (error) {
        uploadResponseElement.textContent = 'Erreur lors de l\'upload.';
        console.error(error);
    }
});

// Gestion du bouton pour générer le résumé
const summaryButton = document.getElementById('summaryButton');
const summaryResponseElement = document.getElementById('summaryResponse');

summaryButton.addEventListener('click', async () => {
    try {
        const userData = {
            goal: document.getElementById('goal').value,
            allergies: document.getElementById('allergies').value,
            preferences: document.getElementById('preferences').value
        };

        const response = await fetch('http://127.0.0.1:5000/getsummary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        const result = await response.json();
        summaryResponseElement.textContent = result.summary || 'Erreur lors de la génération du résumé.';
    } catch (error) {
        summaryResponseElement.textContent = 'Erreur lors de la communication avec le service de résumé.';
        console.error(error);
    }
});

// Gestion du bouton pour traduire le résumé
const translateButton = document.getElementById('translateButton');
const translationResponseElement = document.getElementById('translationResponse');

translateButton.addEventListener('click', async () => {
    const language = document.getElementById('language').value;
    const textToTranslate = document.getElementById('summaryResponse').textContent; // Texte du résumé généré

    try {
        const response = await fetch('http://127.0.0.1:5000/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: textToTranslate, language: language }),
        });

        const result = await response.json();
        translationResponseElement.textContent = result.translated_text || 'Erreur lors de la traduction.';
    } catch (error) {
        translationResponseElement.textContent = 'Erreur lors de la communication avec le service de traduction.';
        console.error(error);
    }
});

// Gestion du formulaire pour analyser une image
const analyzeForm = document.getElementById('analyzeForm');
const analyzeResponseElement = document.getElementById('analyzeResponse');

analyzeForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Empêche le rechargement de la page
    const formData = new FormData(analyzeForm);

    try {
        const response = await fetch('http://127.0.0.1:5000/analyzeimage', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        analyzeResponseElement.textContent = result.recognized_items
            ? `Aliments reconnus : ${result.recognized_items.join(', ')}`
            : 'Aucun aliment reconnu.';
    } catch (error) {
        analyzeResponseElement.textContent = 'Erreur lors de l\'analyse de l\'image.';
        console.error(error);
    }
});

// Gestion du bouton pour obtenir des conseils nutritionnels
const adviceButton = document.getElementById('adviceButton');
const adviceResponseElement = document.getElementById('adviceResponse');

adviceButton.addEventListener('click', async () => {
    const recognizedItems = analyzeResponseElement.textContent.replace('Aliments reconnus : ', '').split(', ');

    try {
        const response = await fetch('http://127.0.0.1:5000/nutritionadvice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ recognized_items: recognizedItems }),
        });

        const result = await response.json();
        adviceResponseElement.textContent = result.advice.join(' ') || 'Aucun conseil disponible.';
    } catch (error) {
        adviceResponseElement.textContent = 'Erreur lors de la génération des conseils.';
        console.error(error);
    }
});
