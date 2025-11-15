import yfinance as yf
import datetime
import numpy as np

def get_stock_data(ticker_symbol, with_projection=False):
    """
    Récupère les données boursières récentes pour une entreprise donnée.
    Si with_projection=True, calcule une estimation prudente de la tendance (non spéculative).
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="6mo")

        if data.empty:
            return f"No recent data found for {ticker_symbol}."

        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

        summary = (
            f"📈 Stock: {ticker_symbol} | Date: {latest.name.strftime('%Y-%m-%d')} | "
            f"Close: {latest['Close']:.2f} USD | Daily change: {change:+.2f}%."
        )

        # 🔮 Simple projection linéaire basée sur tendance 6 mois
        if with_projection:
            data['returns'] = data['Close'].pct_change()
            avg_monthly = data['returns'].mean() * 21  # approx 21 trading days
            projected = latest['Close'] * (1 + avg_monthly * 12)
            summary += (
                f" Estimated 12-month projection (trend-based): {projected:.2f} USD "
                f"(average monthly return: {avg_monthly*100:.2f}%)."
            )

        return summary

    except Exception as e:
        return f"Error fetching stock data for {ticker_symbol}: {str(e)}"
