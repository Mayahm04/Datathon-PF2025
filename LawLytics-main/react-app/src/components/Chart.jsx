 // PieChart.jsx
import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import mockStocks from "./mocks/monStock";
import "../styles/DescriptionSection.css";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const PieChart = ({ sectors }) => {
  const data_IA = sectors?.length ? sectors : mockStocks;

  const sectorLabels = [...new Set(data_IA.map((item) => item.sector))];

  const INITIAL_VALUES = {
    Tech: 40,
    Energy: 25,
    Finance: 20,
    Healthcare: 15,
  };

  const variations = data_IA.reduce((acc, item) => {
    acc[item.sector] = (acc[item.sector] || 0) + item.impact_estimation.magnitude;
    return acc;
  }, {});

  const datasetValues = sectorLabels.map(
    (sector) => (INITIAL_VALUES[sector] || 0) + (variations[sector] || 0)
  );

  const data = {
    labels: sectorLabels,
    datasets: [
      {
        data: datasetValues,
        backgroundColor: ["#4B9CE2", "#34D399", "#FBBF24", "#F87171"],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        position: "right",
        labels: {
          color: "#fff",
          font: { size: 14 },
        },
      },
    },
    responsive: true,
  };

  return (
    <div style={{ width: "500px" }}>
      <h3 className="portfolio">Portfolio Distribution</h3>
      <Pie data={data} options={options} />
    </div>

  );
};

export default PieChart;  