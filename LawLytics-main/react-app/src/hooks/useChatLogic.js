// src/hooks/useChatLogic.js

import { useState, useCallback } from 'react';

// ⚠️ Configuration des endpoints Flask
const SIGN_URL_API_ENDPOINT = "http://127.0.0.1:5000/sign_url"; 
const CHAT_API_ENDPOINT = "http://127.0.0.1:5000/chat"; 

/**
 * Hook personnalisé pour gérer la logique de communication RAG/S3/Chat.
 * @param {function} addMessage - Fonction pour ajouter un message à l'historique.
 * @param {function} updateLastMessage - Fonction pour mettre à jour le dernier message.
 */
export const useChatLogic = (addMessage, updateLastMessage) => {
    
    // États gérés par le hook
    const [ragContextId, setRagContextId] = useState(null); 
    const [fileExtension, setFileExtension] = useState(null); 
    const [fileName, setFileName] = useState(null); 
    const [isLoading, setIsLoading] = useState(false);

    // --- Logique d'Upload S3 (Flux 1) ---

    const uploadFileToS3 = useCallback(async (file) => {
        setIsLoading(true);
        addMessage(`Préparation de l'upload sécurisé pour ${file.name}...`, 'model');

        const name = file.name;
        const type = file.type || 'application/octet-stream';

        try {
            // ÉTAPE 1 : Demander une URL pré-signée à Flask
            const signUrlResponse = await fetch(SIGN_URL_API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    file_name: name,
                    file_type: type,
                }),
            });

            if (!signUrlResponse.ok) {
                throw new Error("Erreur lors de la demande d'URL de signature.");
            }

            const signData = await signUrlResponse.json();
            const { signedUrl, fileId } = signData; 

            if (!signedUrl || !fileId) {
                throw new Error("L'API n'a pas retourné l'URL ou l'ID nécessaire.");
            }

            updateLastMessage(`URL de signature reçue. Démarrage du transfert direct à S3 (ID: ${fileId.substring(0, 8)}...).`);

            // ÉTAPE 2 : Uploader le fichier DIRECTEMENT à S3
            const s3UploadResponse = await fetch(signedUrl, {
                method: 'PUT',
                headers: { 'Content-Type': type }, 
                body: file, 
            });

            if (!s3UploadResponse.ok) {
                throw new Error(`Échec de l'upload S3. Réponse: ${s3UploadResponse.status}`);
            }

            // ÉTAPE 3 : Succès de l'upload
            setRagContextId(fileId);
            setFileName(name);
            setFileExtension(name.split('.').pop().toLowerCase());

            updateLastMessage(`Fichier ${name} **téléchargé sur S3.** Le processus RAG commence l'indexation. Vous pouvez poser votre question.`);

        } catch (error) {
            console.error("Erreur complète du flux RAG/S3:", error);
            updateLastMessage(`[ERREUR] Échec du processus RAG/S3. Détails : ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    }, [addMessage, updateLastMessage]);


    // --- Logique de Soumission du Prompt (Flux 2) ---

    const handlePromptSubmit = useCallback(async (promptText) => {
        setIsLoading(true);
        addMessage(promptText, 'user');
        addMessage("Recherche de contexte RAG et analyse en cours...", 'model');

        const payload = {
            prompt: promptText, 
            rag_context_id: ragContextId, 
        };
        
        try {
            const response = await fetch(CHAT_API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            // Gestion des erreurs du Backend (RAG_NOT_READY inclus)
            if (!response.ok) {
                if (data.status === "RAG_NOT_READY") {
                    updateLastMessage(data.response); 
                    return; 
                }
                throw new Error(`Erreur API Chat: ${response.status} - ${data.response || 'Erreur inconnue'}`);
            }

            // Succès : Affichage de la réponse du modèle
            const generatedResponse = data.response || "L'API n'a pas retourné de réponse texte valide.";
            updateLastMessage(generatedResponse);
            
        } catch (error) {
            console.error("Erreur lors de l'appel API Chat:", error);
            updateLastMessage(`[ERREUR] Échec de la communication avec l'API Chat. Détails : ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    }, [ragContextId, addMessage, updateLastMessage]);

    // Exposer les états et les fonctions nécessaires au composant App.jsx
    return {
        ragContextId,
        fileName,
        fileExtension,
        isLoading,
        uploadFileToS3,
        handlePromptSubmit,
    };
};