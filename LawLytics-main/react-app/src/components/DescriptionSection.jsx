// src/components/DescriptionSection.jsx
import React, { useState } from "react";
import { FaArrowUp, FaArrowDown, FaSearch } from "react-icons/fa";
import StockBubble from "./StockBubble";
import mockStocks from "./mocks/monStock";
import "../styles/DescriptionSection.css";

const DescriptionSection = ({ variations }) => {
  const data = variations?.length ? variations : mockStocks;
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStock, setSelectedStock] = useState(null);

  const filteredData = data.filter((item) =>
    item.stock_symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="description-section">
      <div className="description-header">
        <h2 className="section-title">Market Impact Analysis</h2>

        <div className="search-bar">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search company (ex: TSLA)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="description-scroll">
        {filteredData.length > 0 ? (
          filteredData.map((item, index) => {
            const variation = item.impact_estimation?.magnitude ?? 0;
            const isPositive = variation >= 0;
            return (
              <div
                key={index}
                className="stock-row"
                onClick={() => setSelectedStock(item)}
              >
                <div className="stock-info">
                  <span className="ticker">{item.stock_symbol}</span>
                  <span
                    className={`variation ${isPositive ? "positive" : "negative"}`}
                  >
                    {isPositive ? <FaArrowUp /> : <FaArrowDown />}
                    {Math.abs(variation).toFixed(2)}%
                  </span>
                </div>
                <p className="reason">{item.summary}</p>
              </div>
            );
          })
        ) : (
          <p className="no-results">No results found.</p>
        )}
      </div>

      {selectedStock && (
        <StockBubble
          stock={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}
    </div>
  );
};

export default DescriptionSection;
