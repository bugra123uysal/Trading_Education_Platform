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

    return {
        "symbol": symbol,
        "candles_before": [_bar_to_dict(b) for b in before],
        "cut_date": bars[cut_index].date,
        "candles_after": [_bar_to_dict(b) for b in after],
        "outcome_pct": outcome_pct,
        "reasoning": _generate_reasoning(bars, cut_index, after),
    }


def _generate_reasoning(bars, cut_index: int, after: list) -> list[str]:
    """
    Kesme noktasındaki teknik görünümü (EMA trendi, dolar hacmi) ve
    sonrasında gerçekleşen hareketin bu görünümle tutarlı olup olmadığını
    anlatan gözlemler üretir. Amaç kesin bir "neden" iddia etmek değil —
    piyasa hareketlerinin gerçek nedeni (haber, kazanç vb.) fiyat
    verisinde yok — amaç, teknik göstergelerin o anda ne söylediğini ve
    sonradan gerçekleşenle ne kadar uyumlu olduğunu göstermek.
    """
    history = [_bar_to_dict(b) for b in bars[: cut_index + 1]]
    df = with_indicators(history)
    last = df.iloc[-1]

    notes: list[str] = []

    if last["close"] > last["ema_200"]:
        notes.append(
            "Kesme noktasında fiyat, uzun vadeli eğilimi gösteren 200 günlük EMA'nın "
            "üzerindeydi — bu genellikle büyük resimde bir yükseliş trendine işaret eder."
        )
    else:
        notes.append(
            "Kesme noktasında fiyat, 200 günlük EMA'nın altındaydı — bu genellikle "
            "büyük resimde bir düşüş ya da zayıf trende işaret eder."
        )

    if last["ema_50"] > last["ema_200"]:
        notes.append(
            "Kısa vadeli ortalama (EMA 50), uzun vadeli ortalamanın (EMA 200) üzerindeydi — "
            "momentum yukarı yönlüydü."
        )
    else:
        notes.append(
            "Kısa vadeli ortalama (EMA 50), uzun vadeli ortalamanın (EMA 200) altındaydı — "
            "momentum aşağı yönlüydü."
        )

    recent = df.tail(10)
    baseline_dv = last["dollar_volume_ma50"]
    if pd.notna(baseline_dv) and recent["dollar_volume"].notna().all():
        avg_recent_dv = recent["dollar_volume"].mean()
        if avg_recent_dv > baseline_dv * 1.15:
            notes.append(
                "Son günlerde dolar hacmi, 50 günlük ortalamasının belirgin şekilde "
                "üzerindeydi — hisseye yoğun bir ilgi vardı."
            )
        elif avg_recent_dv < baseline_dv * 0.85:
            notes.append(
                "Son günlerde dolar hacmi, 50 günlük ortalamasının altındaydı — "
                "hisseye olan ilgi nispeten sönükleşmişti."
            )
        else:
            notes.append("Dolar hacmi son günlerde normal seviyelerdeydi, belirgin bir anormallik yoktu.")

        if after:
            full_with_after = [_bar_to_dict(b) for b in bars[: cut_index + 1 + len(after)]]
            after_df = with_indicators(full_with_after).tail(len(after))
            moved_up = after_df["close"].iloc[-1] > after_df["close"].iloc[0]
            avg_after_dv = after_df["dollar_volume"].mean()
            if pd.notna(avg_after_dv):
                if moved_up and avg_after_dv > baseline_dv:
                    notes.append(
                        "Sonrasında gerçekleşen yükseliş, ortalamanın üzerinde bir hacimle "
                        "desteklendi — teknik analizde bu genelde hareketin 'sağlıklı' / "
                        "katılımlı kabul edildiği bir işarettir."
                    )
                elif (not moved_up) and avg_after_dv > baseline_dv:
                    notes.append(
                        "Sonrasında gerçekleşen düşüş, ortalamanın üzerinde bir hacimle "
                        "gerçekleşti — bu genelde satış baskısının güçlü olduğunu gösterir."
                    )
                elif avg_after_dv < baseline_dv:
                    notes.append(
                        "Sonraki hareket, düşük hacimle gerçekleşti — bu tür hareketler "
                        "genelde daha az güvenilir kabul edilir, kolayca tersine dönebilir."
                    )

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
