"""
Senaryo bazlı quiz üretimi.

Mantık: gerçek bir hissenin geçmişinden rastgele bir "kesme noktası"
seçilir. Kullanıcıya o noktaya kadarki fiyat hareketi gösterilir ve
"bu noktada ne yapardın?" diye sorulur. Cevap verildikten sonra kesme
noktasından sonraki gerçek fiyat hareketi gösterilir — böylece kullanıcı
kendi tahminini gerçekle karşılaştırır. Bu, piyasa öngörmenin ne kadar
zor olduğunu deneyimleyerek öğretmenin en doğrudan yoludur.
"""
import random

import pandas as pd
from sqlalchemy.orm import Session

from app.data.fetcher import get_candles, DEFAULT_SYMBOLS
from app.i18n import t
from app.indicators import with_indicators

LOOKBACK_DAYS = 60   # kullanıcıya gösterilen "geçmiş" pencere
LOOKAHEAD_DAYS = 20  # kesme noktasından sonra "gerçekte ne oldu" penceresi


def generate_scenario(db: Session) -> dict:
    symbol = random.choice(list(DEFAULT_SYMBOLS.keys()))
    bars = get_candles(db, symbol)

    # Kesme noktası, en az LOOKBACK_DAYS geçmişi ve LOOKAHEAD_DAYS geleceği
    # olacak şekilde rastgele seçilir.
    min_index = LOOKBACK_DAYS
    max_index = len(bars) - LOOKAHEAD_DAYS - 1
    if max_index <= min_index:
        raise ValueError("Senaryo üretmek için yeterli veri yok.")

    cut_index = random.randint(min_index, max_index)

    before = bars[cut_index - LOOKBACK_DAYS: cut_index + 1]
    after = bars[cut_index + 1: cut_index + 1 + LOOKAHEAD_DAYS]

    cut_price = bars[cut_index].close
    end_price = after[-1].close
    outcome_pct = round((end_price - cut_price) / cut_price * 100, 2)

    history = [_bar_to_dict(b) for b in bars[: cut_index + 1]]
    df = with_indicators(history)
    last = df.iloc[-1]

    return {
        "symbol": symbol,
        "candles_before": [_bar_to_dict(b) for b in before],
        "cut_date": bars[cut_index].date,
        "candles_after": [_bar_to_dict(b) for b in after],
        "outcome_pct": outcome_pct,
        # Yapısal bayrak: UI eğitici tavsiyeyi metin ayrıştırmadan bunun
        # üzerinden verir (dilden bağımsız).
        "trend_up": bool(last["close"] > last["ema_200"]),
        "reasoning": _generate_reasoning(df, bars, cut_index, after),
    }


def _generate_reasoning(df, bars, cut_index: int, after: list) -> list[str]:
    """
    Kesme noktasındaki teknik görünümü (EMA trendi, dolar hacmi) ve
    sonrasında gerçekleşen hareketin bu görünümle tutarlı olup olmadığını
    anlatan gözlemler üretir (seçili dilde). Amaç kesin bir "neden" iddia
    etmek değil — piyasa hareketlerinin gerçek nedeni (haber, kazanç vb.)
    fiyat verisinde yok — amaç, teknik göstergelerin o anda ne söylediğini
    ve sonradan gerçekleşenle ne kadar uyumlu olduğunu göstermek.
    """
    last = df.iloc[-1]

    notes: list[str] = []
    notes.append(t("reason_above_200") if last["close"] > last["ema_200"] else t("reason_below_200"))
    notes.append(t("reason_ema50_above") if last["ema_50"] > last["ema_200"] else t("reason_ema50_below"))

    recent = df.tail(10)
    baseline_dv = last["dollar_volume_ma50"]
    if pd.notna(baseline_dv) and recent["dollar_volume"].notna().all():
        avg_recent_dv = recent["dollar_volume"].mean()
        if avg_recent_dv > baseline_dv * 1.15:
            notes.append(t("reason_dv_high"))
        elif avg_recent_dv < baseline_dv * 0.85:
            notes.append(t("reason_dv_low"))
        else:
            notes.append(t("reason_dv_normal"))

        if after:
            full_with_after = [_bar_to_dict(b) for b in bars[: cut_index + 1 + len(after)]]
            after_df = with_indicators(full_with_after).tail(len(after))
            moved_up = after_df["close"].iloc[-1] > after_df["close"].iloc[0]
            avg_after_dv = after_df["dollar_volume"].mean()
            if pd.notna(avg_after_dv):
                if moved_up and avg_after_dv > baseline_dv:
                    notes.append(t("reason_after_up_highvol"))
                elif (not moved_up) and avg_after_dv > baseline_dv:
                    notes.append(t("reason_after_down_highvol"))
                elif avg_after_dv < baseline_dv:
                    notes.append(t("reason_after_lowvol"))

    return notes


def _bar_to_dict(b) -> dict:
    return {
        "date": b.date,
        "open": b.open,
        "high": b.high,
        "low": b.low,
        "close": b.close,
        "volume": b.volume,
    }
