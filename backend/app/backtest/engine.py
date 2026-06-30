"""
Backtest motoru: bir stratejinin pozisyon serisini alıp gerçek işlemlere
(trade) ve performans metriklerine çevirir.

Mantık: pozisyon 0 -> 1 olduğu gün "alış" yapılır (o günün kapanış
fiyatından), 1 -> 0 olduğu gün "satış" yapılır. Her alış-satış çifti bir
trade'dir. Sermayenin tamamı her seferinde tek pozisyona yatırılır
(bileşik getiri) — bu basit ama anlaşılır bir model, gerçek fon
yönetimi karmaşıklığına girmeden stratejinin "işe yarayıp yaramadığını"
göstermek için yeterli.
"""
import pandas as pd

from app.backtest.strategies import STRATEGIES


def run_backtest(
    bars: list[dict],
    strategy: str,
    initial_capital: float = 10000,
    **strategy_params,
) -> dict:
    if strategy not in STRATEGIES:
        raise ValueError(f"Bilinmeyen strateji: {strategy}")

    df = pd.DataFrame(bars)
    if df.empty or len(df) < 5:
        raise ValueError("Backtest için yeterli veri yok (en az birkaç barlık geçmiş gerekli).")

    df = df.reset_index(drop=True)
    position = STRATEGIES[strategy](df, **strategy_params)

    trades = []
    capital = initial_capital
    entry_price = None
    entry_date = None

    for i in range(len(df)):
        was_in = position.iloc[i - 1] == 1 if i > 0 else False
        is_in = position.iloc[i] == 1

        if not was_in and is_in:
            entry_price = df.loc[i, "close"]
            entry_date = df.loc[i, "date"]
        elif was_in and not is_in and entry_price is not None:
            exit_price = df.loc[i, "close"]
            exit_date = df.loc[i, "date"]
            profit_pct = (exit_price - entry_price) / entry_price * 100
            capital *= (1 + profit_pct / 100)
            trades.append({
                "entry_date": entry_date,
                "entry_price": round(float(entry_price), 2),
                "exit_date": exit_date,
                "exit_price": round(float(exit_price), 2),
                "profit_pct": round(float(profit_pct), 2),
                "profit_abs": round(float(capital - (capital / (1 + profit_pct / 100))), 2),
            })
            entry_price = None
            entry_date = None

    # Backtest sonunda hâlâ pozisyondaysak, son kapanış fiyatından
    # "kâğıt üzerinde" kapatıp gösteriyoruz ki kullanıcı açık pozisyonun
    # durumunu da görsün.
    if entry_price is not None:
        exit_price = df.loc[len(df) - 1, "close"]
        exit_date = df.loc[len(df) - 1, "date"]
        profit_pct = (exit_price - entry_price) / entry_price * 100
        capital *= (1 + profit_pct / 100)
        trades.append({
            "entry_date": entry_date,
            "entry_price": round(float(entry_price), 2),
            "exit_date": exit_date,
            "exit_price": round(float(exit_price), 2),
            "profit_pct": round(float(profit_pct), 2),
            "profit_abs": round(float(capital - (capital / (1 + profit_pct / 100))), 2),
        })

    total_trades = len(trades)
    wins = [t for t in trades if t["profit_pct"] > 0]
    win_rate = round(len(wins) / total_trades * 100, 1) if total_trades else 0.0
    total_return_pct = round((capital - initial_capital) / initial_capital * 100, 2)

    best_trade = max(trades, key=lambda t: t["profit_pct"]) if trades else None
    worst_trade = min(trades, key=lambda t: t["profit_pct"]) if trades else None

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "total_return_pct": total_return_pct,
        "final_capital": round(capital, 2),
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "trades": trades,
    }
