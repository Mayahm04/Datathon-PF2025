import yfinance as yf

try:
    # ✅ plus de session manuelle : yfinance s’en charge
    ticker = yf.Ticker("AAPL")
    data = ticker.history(period="5d")

    if data.empty:
        print("⚠️ Aucun historique trouvé pour AAPL.")
    else:
        print("✅ Données récupérées :")
        print(data.tail())

except Exception as e:
    print("❌ Erreur :", e)
