// src/components/StockBubble.jsx
import React from "react";
import { FaTimesCircle } from "react-icons/fa";
import "../styles/StockBubble.css";

const StockBubble = ({ stock, onClose }) => {
  if (!stock) return null; // Sécurité : rien à afficher

  const { regulation_details, regulatory_risk, sources } = stock;
  const snippet = sources?.[0]?.snippet || "No policy available.";

  return (
    <div className="stock-bubble-overlay" onClick={onClose}>
      <div className="stock-bubble" onClick={(e) => e.stopPropagation()}>
        <div className="bubble-header">
          <h3>{regulation_details?.law_name || "Unknown Regulation"}</h3>
          <button className="close-btn" onClick={onClose}>
            <FaTimesCircle size={22} />
          </button>
        </div>

        <div className="bubble-body">
          <p className="law-description">
            {regulation_details?.description || "No description provided."}
          </p>

          <div className="bubble-section">
            <strong>Policy Highlight:</strong>
            <p className="snippet">{snippet}</p>
          </div>

          <div className="bubble-section">
            <strong>Risk Score:</strong> {regulatory_risk?.score ?? "N/A"}
          </div>

          <div className="bubble-section">
            <strong>Key Drivers:</strong>
            <ul>
              {regulatory_risk?.drivers?.map((d, i) => (
                <li key={i}>{d}</li>
              )) || <li>No drivers listed.</li>}
            </ul>
          </div>

          {stock.recommendations && (
            <div className="bubble-section">
              <strong>Recommendations:</strong>
              <ul>
                {stock.recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StockBubble;
