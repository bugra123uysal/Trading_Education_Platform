"""
Terim sözlüğü başlangıç verisi.

child_explanation alanları kasıtlı olarak jargon kullanmadan, gerçek
hayattan benzetmelerle yazıldı — amaç, hiç finans bilmeyen birinin bile
anlayabileceği bir anlatım.
"""
from sqlalchemy.orm import Session

from app.models import GlossaryTerm

TERMS = [
    dict(
        slug="stop-loss",
        term="Stop-Loss (Zarar Durdur)",
        category="risk-yonetimi",
        short_definition="Fiyat belirli bir seviyeye düşünce hisseyi otomatik satan emir.",
        child_explanation=(
            "Bir oyuncak makineye para attığını ve kaybedebileceğin en fazla parayı "
            "önceden belirlediğini düşün. 'Bu kadar kaybedersem dururum' demek gibi. "
            "Stop-loss da borsada aynı şeyi yapar: hisse fiyatı belirlediğin seviyeye "
            "düşerse, sistem otomatik olarak hisseni satar ki daha fazla kaybetmeyesin."
        ),
        example="100 dolara aldığın bir hisseye 90 dolardan stop-loss koyarsan, fiyat 90'a düşünce otomatik satılır.",
    ),
    dict(
        slug="rsi",
        term="RSI (Göreceli Güç Endeksi)",
        category="teknik-analiz",
        short_definition="Bir hissenin 'çok mu pahalandı yoksa çok mu ucuzladı' sorusuna 0-100 arası puan veren gösterge.",
        child_explanation=(
            "Bir tahterevalliyi düşün. Çok yukarı çıkmışsa, aşağı inmesi an meselesidir. "
            "RSI de fiyatın ne kadar 'yukarıda' veya 'aşağıda' olduğunu 0 ile 100 arasında "
            "bir sayıyla gösterir. 70'in üstü 'çok yükseldi, düşebilir' demek, 30'un altı "
            "'çok düştü, yükselebilir' demektir."
        ),
        example="RSI 25 ise hisse 'aşırı satılmış' kabul edilir; bazı yatırımcılar bunu ucuzluk fırsatı sayar.",
    ),
    dict(
        slug="hacim",
        term="Hacim (Volume)",
        category="temel",
        short_definition="Belirli bir sürede kaç hisse senedinin alınıp satıldığı.",
        child_explanation=(
            "Bir pazar yerinde o gün kaç tane elma satıldığını düşün. Hacim de borsada "
            "bir günde kaç hisse senedinin el değiştirdiğini gösterir. Yüksek hacim, çok "
            "kişinin o hisseyle ilgilendiği; düşük hacim, ilginin az olduğu anlamına gelir."
        ),
        example="Bir haber çıktığında hacmin aniden artması, çok kişinin hemen alım-satım yaptığını gösterir.",
    ),
    dict(
        slug="destek-direnc",
        term="Destek / Direnç",
        category="teknik-analiz",
        short_definition="Fiyatın geçmişte tekrar tekrar durduğu, 'zor geçilen' seviyeler.",
        child_explanation=(
            "Bir topu yere attığında belli bir noktadan sonra zıplamayı bırakıp durur, "
            "değil mi? Destek seviyesi, fiyatın düşerken sık sık 'durduğu' ve geri "
            "yükseldiği yer gibidir — sanki orada görünmez bir zemin var. Direnç ise "
            "tam tersi: fiyatın yükselirken sık sık çarpıp geri döndüğü görünmez tavan."
        ),
        example="Bir hisse üç kez 50 dolara kadar çıkıp geri düşüyorsa, 50 dolar bir direnç seviyesi olabilir.",
    ),
    dict(
        slug="pdt-kurali",
        term="PDT Kuralı (Pattern Day Trader)",
        category="temel",
        short_definition="ABD'de hesabında 25.000 dolardan az olan kişilerin 5 iş günü içinde 3'ten fazla gün-içi işlem yapmasını sınırlayan kural.",
        child_explanation=(
            "Bazı oyun parklarında 'küçük çocuklar bu hızlı trene sadece eşlikçiyle "
            "binebilir' kuralı vardır — güvenlik için. PDT kuralı da buna benzer: "
            "hesabında 25.000 dolardan az parası olan biri, bir hafta içinde aynı "
            "hisseyi 3'ten fazla kez aynı gün içinde alıp satarsa, borsa şirketi "
            "'dur, bu çok riskli, hesabını bir süre kısıtlıyorum' der."
        ),
        example="25.000 dolar altı bir hesapla haftada 4. gün-içi işlemi yapmaya çalışırsan sistem seni uyarır ya da engeller.",
    ),
    dict(
        slug="hareketli-ortalama",
        term="Hareketli Ortalama (Moving Average)",
        category="teknik-analiz",
        short_definition="Son X günün ortalama kapanış fiyatını gösteren, fiyat dalgalanmalarını yumuşatan bir çizgi.",
        child_explanation=(
            "Her gün hava durumuna bakmak yerine, son 7 günün ortalama sıcaklığına "
            "bakmak gibi düşün — günlük ani değişimler yerine genel eğilimi görürsün. "
            "Hareketli ortalama da fiyatın son birkaç günlük/haftalık/aylık ortalamasını "
            "alıp çizer, böylece kısa vadeli sıçramalar yerine genel yönü görmeni sağlar."
        ),
        example="20 günlük hareketli ortalama, son 20 günün kapanış fiyatlarının ortalamasıdır.",
    ),
    dict(
        slug="backtest",
        term="Backtest",
        category="temel",
        short_definition="Bir stratejiyi gerçek parayla denemeden önce geçmiş veriler üzerinde test etme yöntemi.",
        child_explanation=(
            "Bir araba yarışına girmeden önce simülatörde defalarca aynı pisti "
            "sürmek gibi düşün — gerçek riske girmeden 'bu strateji işe yarar mı?' "
            "sorusunu cevaplarsın. Backtest de bir alım-satım kuralını geçmişteki "
            "gerçek fiyatlara uygulayıp, 'eğer bu kuralı geçmişte uygulasaydım ne "
            "kazanır ya da kaybederdim?' sorusuna cevap verir."
        ),
        example="'Fiyat 20 günlük ortalamayı yukarı keserse al' kuralını son 3 yılın verisine uygulamak bir backtest'tir.",
    ),
    dict(
        slug="mum-grafigi",
        term="Mum Grafiği (Candlestick Chart)",
        category="temel",
        short_definition="Her mumun bir günün açılış, kapanış, en yüksek ve en düşük fiyatını gösterdiği grafik türü.",
        child_explanation=(
            "Her mumu küçük bir hikaye gibi düşün: gün başladığında fiyat neredeydi "
            "(açılış), gün boyunca en yükseğe nereye çıktı, en düşüğe nereye indi, ve "
            "gün bittiğinde nerede kaldı (kapanış). Yeşil mum 'fiyat yükseldi', kırmızı "
            "mum 'fiyat düştü' demektir."
        ),
        example="Uzun yeşil bir mum, o gün fiyatın açılıştan kapanışa kadar belirgin şekilde yükseldiğini gösterir.",
    ),
    dict(
        slug="portfoy",
        term="Portföy",
        category="temel",
        short_definition="Bir yatırımcının sahip olduğu tüm hisse, fon ve diğer yatırımların toplamı.",
        child_explanation=(
            "Bir oyuncak kutusundaki tüm oyuncaklarının toplamı gibi düşün — sadece "
            "bir tane değil, sahip olduğun her şeyin tamamı. Portföy de senin sahip "
            "olduğun tüm hisselerin, fonların ve yatırımların bir aradaki toplamıdır."
        ),
        example="Portföyünde MU, NVDA ve AAPL hisseleri varsa, bu üçü birlikte senin portföyünü oluşturur.",
    ),
    dict(
        slug="volatilite",
        term="Volatilite (Oynaklık)",
        category="risk-yonetimi",
        short_definition="Bir hissenin fiyatının ne kadar hızlı ve sert iniş-çıkış yaptığını gösteren ölçü.",
        child_explanation=(
            "Sakin bir gölde mi yoksa dalgalı bir denizde mi tekne kullandığını "
            "düşün — dalgalı denizde tekne çok daha fazla sallanır. Volatilitesi "
            "yüksek bir hisse de fiyatı gün içinde çok sert iniş-çıkış yapan hissedir; "
            "düşük volatilite ise daha sakin, yavaş değişen bir fiyat demektir."
        ),
        example="Küçük bir teknoloji şirketinin hissesi genelde büyük, köklü bir şirketten daha volatildir.",
    ),
]


def seed_glossary(db: Session) -> None:
    """Tablo boşsa terimleri ekler — uygulama her başladığında tekrar tekrar eklemez."""
    if db.query(GlossaryTerm).count() > 0:
        return
    for data in TERMS:
        db.add(GlossaryTerm(**data))
    db.commit()
