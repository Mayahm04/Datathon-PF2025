// src/App.jsx
import React, { useState, useCallback } from 'react';
import { PromptInput } from './components/PromptInput';
import { ConversationHistory } from './components/ConversationHistory';
import PieChart from "./components/Chart";
import DescriptionSection from "./components/DescriptionSection";
import './styles/App.css';
import './styles/components.css';

const CHAT_API_ENDPOINT = "http://127.0.0.1:5000/chat";


const App = () => {
  const [fileContent, setFileContent] = useState(null);
  const [fileExtension, setFileExtension] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [summary, setSummary] = useState("");
  const [sectors, setSectors] = useState([]);
  const [stocks, setStocks] = useState([]);

  const [isLoading, setIsLoading] = useState(false);

  console.log("✅ Frontend running correctly");

  // --- Message handling ---
  const addMessage = useCallback((content, type) => {
    setConversationHistory(prev => [...prev, { content, type }]);
  }, []);

  const updateLastMessage = useCallback((content) => {
    setConversationHistory(prev => {
      const newHistory = [...prev];
      if (newHistory.length > 0) {
        newHistory[newHistory.length - 1].content = content;
      } else {
        newHistory.push({ content, type: 'model' });
      }
      return newHistory;
    });
  }, []);

  // --- File handlers ---
  const handleDataLoad = (content, extension, fileName) => {
    setFileContent(content);
    setFileExtension(extension);
    addMessage(`Fichier **${fileName}** (.${extension}) chargé avec succès.`, 'model');
  };

  const handleFileClear = () => {
    setFileContent(null);
    setFileExtension(null);
    addMessage(`Fichier en attente d'analyse annulé.`, 'model');
  };

  // --- Main chat handler ---
  const handlePromptSubmit = async (promptText) => {
    setIsLoading(true);
    addMessage(promptText, 'user');
    addMessage("Analyse en cours. Veuillez patienter...", 'model');
    console.log("🚀 handlePromptSubmit triggered with:", promptText);

    try {
      const payload = {
        prompt: promptText,
        file_content: fileContent,
        file_extension: fileExtension,
      };

      const res = await fetch(CHAT_API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`Erreur HTTP: ${res.status}`);

      const text = await res.text();
      console.log("📩 Raw backend response:", text);

      let data;
      try {
        data = JSON.parse(text);
      } catch (err) {
        console.error("❌ JSON parse error:", err);
        updateLastMessage("Erreur de format JSON dans la réponse du serveur.");
        return;
      }

      console.log("🧩 Parsed backend data:", data);

      const responseData = data.response ? data.response : data;

      updateLastMessage(responseData.summary || "No summary available.");

      setSummary(responseData.summary || "No summary available.");
        setStocks((prevStocks) => {
        const newStocks = responseData.stocks || [];

        console.log("🪙 Previous stocks:", prevStocks);
        console.log("🆕 New stocks from backend:", newStocks);

        // If no new stocks, keep previous
        if (newStocks.length === 0) {
          return prevStocks;
        }

        // Merge: update existing stocks or add new ones
        const updatedStocks = [...prevStocks];
        
        for (const newStock of newStocks) {
          const index = updatedStocks.findIndex(
            (s) => s.stock_symbol === newStock.stock_symbol
          );

          if (index !== -1) {
            // Update existing stock
            updatedStocks[index] = { ...updatedStocks[index], ...newStock };
            console.log(`✏️ Updated ${newStock.stock_symbol}`);
          } else {
            // Add new stock
            updatedStocks.push(newStock);
            console.log(`➕ Added ${newStock.stock_symbol}`);
          }
        }

        console.log("📊 Final stocks array:", updatedStocks);
        return updatedStocks;
      });

      setSectors(responseData.sectors || []);

      setFileContent(null);
      setFileExtension(null);

    } catch (error) {
      console.error("💥 Fetch or network error:", error);
      updateLastMessage(`[ERREUR] ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- JSX ---
  return (
    <div className="datathon-app">
      <div className="main-interface">
        {/* --- LEFT COLUMN --- */}
        <div id="description-section">
          <DescriptionSection variations={stocks} />
        </div>

        {/* --- CHART + SUMMARY --- */}
        <div id="pie-chart">
          <PieChart data={sectors} />
          <div className="chart-summary">
            <h3>Market Summary</h3>
            <p>
              {summary
                ? summary
                : "Awaiting analysis... Submit a prompt to see your portfolio summary."}
            </p>
          </div>
        </div>

        {/* --- CHAT AREA --- */}
        <div className="conversation-zone">
          <ConversationHistory history={conversationHistory} />
          <PromptInput
            onSubmit={handlePromptSubmit}
            isLoading={isLoading}
            onDataLoad={handleDataLoad}
            onFileClear={handleFileClear}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
