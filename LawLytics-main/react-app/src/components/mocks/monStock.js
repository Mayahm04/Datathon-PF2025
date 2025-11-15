// src/components/mock/mockStocks.js

const mockStocks = [
  {
    stock_symbol: "TSLA",
    impact_estimation: { magnitude: 0.42 },
    sector: "Energy",
    summary: "US clean energy subsidies boost domestic EV production.",
    regulation_details: {
      law_name: "Inflation Reduction Act of 2022",
      description: "Federal subsidies for clean energy and EV production."
    },
    regulatory_risk: {
      score: 0.25,
      drivers: ["Tax credits for EVs", "Domestic supply chain incentives"]
    },
    sources: [{ snippet: "Federal incentives boost local EV production." }],
    recommendations: [
      "Increase renewable exposure",
      "Monitor subsidy updates"
    ]
  },
  {
    stock_symbol: "XOM",
    sector: "Energy",
    impact_estimation: { magnitude: -0.50 },
    summary: "Carbon policy pressure on oil producers.",
    regulation_details: {
      law_name: "EU Green Deal 2030",
      description: "New carbon pricing and emission standards for heavy industries."
    },
    regulatory_risk: {
      score: 0.78,
      drivers: [
        "Carbon tax expansion in EU",
        "Operational limits on fossil production"
      ]
    },
    sources: [
      {
        snippet:
          "EU carbon neutrality objectives impose stricter industry caps by 2030."
      }
    ],
    recommendations: [
      "Hedge energy exposure through renewables",
      "Re-evaluate carbon-heavy assets"
    ]
  },
  {
    stock_symbol: "MSFT",
    sector: "Tech",
    impact_estimation: { magnitude: -0.35 },
    summary: "EU digital regulations increase compliance costs for US tech firms.",
    regulation_details: {
      law_name: "Regulation (EU) 2024/1689",
      description:
        "Framework governing AI transparency and platform interoperability in the EU."
    },
    regulatory_risk: {
      score: 0.65,
      drivers: [
        "Transparency obligations for AI systems",
        "Cross-border data restrictions"
      ]
    },
    sources: [
      {
        snippet:
          "The regulation introduces new transparency rules for algorithms operating in EU markets."
      }
    ],
    recommendations: [
      "Monitor European Commission updates",
      "Strengthen internal compliance reporting"
    ]
  },
  {
    stock_symbol: "AAPL",
    sector: "Healthcare",
    impact_estimation: { magnitude: 0.18 },
    summary: "Tech exports benefit from favorable tax policy extensions.",
    regulation_details: {
      law_name: "Tax Modernization Act 2025",
      description: "US fiscal adjustments supporting digital exports and innovation."
    },
    regulatory_risk: {
      score: 0.32,
      drivers: ["Lower taxation on overseas digital products"]
    },
    sources: [
      {
        snippet:
          "New tax reforms provide incentives for hardware and software exports."
      }
    ],
    recommendations: [
      "Increase global hardware shipments",
      "Leverage R&D credits for innovation"
    ]
  },
  {
    stock_symbol: "AMZN",
    sector: "Finance",
    impact_estimation: { magnitude: 0.25 },
    summary: "E-commerce demand rises following import tariff adjustments.",
    regulation_details: {
      law_name: "US Trade Simplification Act",
      description:
        "Tariff reductions on consumer goods to stimulate domestic online sales."
    },
    regulatory_risk: {
      score: 0.40,
      drivers: ["Reduced tariffs increase operational efficiency"]
    },
    sources: [
      {
        snippet:
          "Simplified import procedures expected to benefit e-commerce and logistics companies."
      }
    ],
    recommendations: [
      "Expand logistics network in key trade zones",
      "Optimize pricing on imported products"
    ]
  }
];

export default mockStocks;
