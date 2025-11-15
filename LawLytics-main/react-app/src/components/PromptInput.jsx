import React, { useState, useRef } from 'react';
import { FaArrowUp, FaPaperclip, FaFolder, FaTimes } from 'react-icons/fa';

export const PromptInput = ({ onSubmit, isLoading, onDataLoad, onFileClear }) => {
    const [promptText, setPromptText] = useState('');
    const [fileName, setFileName] = useState('');
    const [error, setError] = useState(null);
    const [isHovering, setIsHovering] = useState(false);
    const fileInputRef = useRef(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (promptText.trim() && !isLoading) {
            onSubmit(promptText.trim());
            setPromptText('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        setError(null);

        const extension = file.name.split('.').pop().toLowerCase();
        const allowed = ['txt', 'csv', 'html', 'xml', 'json', 'log'];
        if (!allowed.includes(extension)) {
            setError(`Format .${extension} non standard, tentative de chargement...`);
        }

        setFileName(file.name);

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            onDataLoad(content, extension, file.name);
        };
        reader.readAsText(file);
        event.target.value = '';
    };

    const handleClearFile = () => {
        setFileName('');
        setError(null);
        fileInputRef.current.value = '';
        onFileClear();
    };

    return (
        <form id="prompt-input" className="prompt-input" onSubmit={handleSubmit}>
            <input
                type="file"
                accept=".txt,.csv,.html,.xml,.json,.log"
                style={{ display: 'none' }}
                ref={fileInputRef}
                onChange={handleFileChange}
            />

            {/* Zone d’entrée */}
            <button
                type="button"
                className="attach-button"
                onClick={() => {
                    if (!fileName) fileInputRef.current?.click();
                }}
                disabled={isLoading}
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
            >
                {/* 📎 Trombone par défaut */}
                {!fileName && <FaPaperclip style={{ fontSize: '20px' }} />}

                {/* 📁 Dossier ou ❌ au survol */}
                {fileName && (
                    <>
                        {!isHovering ? (
                            <FaFolder style={{ fontSize: '20px', color: 'var(--color-primary)' }} />
                        ) : (
                            <FaTimes
                                onClick={handleClearFile}
                                style={{ fontSize: '18px', color: '#ff4d4d' }}
                            />
                        )}
                    </>
                )}
            </button>

            <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Posez une question ou joignez un fichier..."
                rows="2"
                disabled={isLoading}
            />

            <button type="submit" disabled={!promptText.trim() || isLoading}>
                {isLoading ? '...' : <FaArrowUp style={{ fontSize: '20px' }} />}
            </button>

            {error && <p className="error-message">{error}</p>}
        </form>
    );
};
