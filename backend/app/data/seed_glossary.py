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
    dict(
        slug="acik-satis",
        term="Açığa Satış (Short Selling)",
        category="temel",
        short_definition="Fiyatı düşeceğini düşündüğün bir hisseyi ödünç alıp satarak, düşüşten kâr etme yöntemi.",
        child_explanation=(
            "Normalde önce alır, sonra satarsın. Açığa satışta sıra ters çalışır: "
            "sahip olmadığın bir hisseyi aracı kurumdan ödünç alıp hemen satarsın. "
            "Fiyat düşünce daha ucuza geri alıp iade edersin — aradaki fark senin kârın. "
            "Ama fiyat yükselirse zararın teorik olarak sınırsızdır, bu yüzden çok risklidir."
        ),
        example="100 dolardan açığa sattığın hisse 80 dolara düşerse, 20 dolar kâr edersin. 130'a çıkarsa 30 dolar zarar.",
    ),
    dict(
        slug="boga-ayi-piyasasi",
        term="Boğa / Ayı Piyasası",
        category="temel",
        short_definition="Boğa piyasası uzun süreli yükseliş, ayı piyasası uzun süreli düşüş dönemini ifade eder.",
        child_explanation=(
            "Boğa boynuzlarıyla aşağıdan yukarıya doğru saldırır — bu yüzden yükselen piyasaya "
            "boğa piyasası denir. Ayı ise pençesiyle yukarıdan aşağıya vurur — düşen piyasaya "
            "da ayı piyasası denir. Genel kabul: fiyatlar son zirveden %20'den fazla düştüyse "
            "ayı piyasası, %20'den fazla yükseldiyse boğa piyasası başlamıştır."
        ),
        example="2020 sonrası teknoloji hisselerindeki uzun yükseliş bir boğa piyasasıydı; 2022'deki sert düşüş dönemi ayı piyasası.",
    ),
    dict(
        slug="likidite",
        term="Likidite",
        category="temel",
        short_definition="Bir varlığın fiyatını fazla etkilemeden hızla nakde çevrilebilme kolaylığı.",
        child_explanation=(
            "Elinde bir bardak su varsa hemen dökebilirsin; elinde bir buz kalıbı varsa "
            "önce erimesini beklemen gerekir. Likidite de budur: Apple gibi çok işlem gören "
            "bir hisse 'su' gibidir, istediğin an alıp satabilirsin. Az işlem gören küçük "
            "bir hisse 'buz' gibidir — satmak istediğinde alıcı bulmak zaman alabilir ve "
            "fiyatı düşürmek zorunda kalabilirsin."
        ),
        example="Günde milyonlarca adet işlem gören AAPL yüksek likiditeye sahiptir; günde birkaç bin adet işlem gören bir hisse düşük likiditeye.",
    ),
    dict(
        slug="halka-arz",
        term="Halka Arz (IPO)",
        category="temel",
        short_definition="Bir şirketin hisselerini ilk kez borsada halka satışa sunması.",
        child_explanation=(
            "Bir pastane düşün: başta sadece sahibinin. Büyümek için para lazım olunca "
            "'pastanenin küçük paylarını satıyorum, kâr edersek beraber kazanırız' der. "
            "Halka arz da budur: şirket, hisselerini ilk kez borsada herkese satışa açar. "
            "Böylece şirket para toplar, alanlar da şirketin ortağı olur."
        ),
        example="Bir teknoloji şirketi IPO yaptığında, o güne kadar sadece kurucuların elindeki hisseler artık borsada alınıp satılabilir.",
    ),
    dict(
        slug="temettu",
        term="Temettü (Dividend)",
        category="temel",
        short_definition="Şirketin kârının bir kısmını hissedarlarına nakit olarak dağıtması.",
        child_explanation=(
            "Arkadaşlarınla ortak bir limonata standı kurduğunu düşün. Ay sonunda kazanılan "
            "paranın bir kısmı ortaklara paylaştırılır. Temettü de aynısı: şirket kâr edince "
            "bunun bir kısmını 'teşekkürler, ortağımsın' diyerek hisse sahiplerine dağıtır. "
            "Her şirket temettü vermez — bazıları kârı büyümek için şirkette tutar."
        ),
        example="Hisse başına 2 dolar temettü açıklayan bir şirkette 100 hissen varsa, hesabına 200 dolar yatar.",
    ),
    dict(
        slug="arbitraj",
        term="Arbitraj",
        category="temel",
        short_definition="Aynı varlığın farklı piyasalardaki fiyat farkından risksiz kâr etme yöntemi.",
        child_explanation=(
            "Bir mahallede simit 5 lira, iki sokak ötede 7 liraysa; 5'ten alıp 7'den "
            "satarak kâr edersin. Arbitraj tam olarak budur — aynı şeyin iki farklı yerdeki "
            "fiyat farkından yararlanmak. Borsada bu farklar genelde saniyeler içinde "
            "kapanır, bu yüzden çoğunlukla bilgisayarlar (algoritmalar) yapar."
        ),
        example="Bir hisse New York borsasında 100$, Londra'da 100.5$ ise arbitrajcılar ucuzdan alıp pahalıya satarak farkı kapatır.",
    ),
    dict(
        slug="spekulasyon",
        term="Spekülasyon",
        category="risk-yonetimi",
        short_definition="Kısa vadeli fiyat hareketlerinden kâr etmek amacıyla yüksek risk alarak işlem yapmak.",
        child_explanation=(
            "Yatırım, bir ağaç dikip yıllarca meyvesini beklemek gibidir. Spekülasyon ise "
            "'yarın yağmur yağacak, şemsiye fiyatları artar' diye bugünden şemsiye stoklamak "
            "gibi — kısa vadeli bir tahmine para yatırırsın. Tahmin tutarsa hızlı kazanırsın, "
            "tutmazsa hızlı kaybedersin. Kumar değildir ama yatırımdan çok daha risklidir."
        ),
        example="Bir şirketin yarınki bilanço açıklaması öncesi 'iyi gelecek' tahminiyle hisse almak spekülatif bir işlemdir.",
    ),
    dict(
        slug="hedging",
        term="Hedging (Riskten Korunma)",
        category="risk-yonetimi",
        short_definition="Olası zararı azaltmak için ana pozisyonun tersine çalışan bir ikinci pozisyon açmak.",
        child_explanation=(
            "Pikniğe giderken hem güneş kremi hem şemsiye almak gibi: hava nasıl olursa "
            "olsun hazırlıklısın. Hedging de budur — elindeki hisse düşerse zarar edeceksen, "
            "düşüşte kazanan başka bir araç da alırsın. Böylece bir taraf kaybederken diğer "
            "taraf kazanır ve toplam zararın sınırlanır."
        ),
        example="Portföyünde teknoloji hisseleri varken, piyasa düşüşünde değer kazanan bir enstrüman almak bir hedge'dir.",
    ),
    dict(
        slug="kaldirac",
        term="Kaldıraç (Leverage)",
        category="risk-yonetimi",
        short_definition="Kendi paranın üzerine borç ekleyerek daha büyük pozisyon açmak — kâr da zarar da katlanır.",
        child_explanation=(
            "Küçük bir kuvvetle ağır bir taşı kaldıran manivela gibi: 100 doların varken "
            "10x kaldıraçla 1000 dolarlık işlem yapabilirsin. Fiyat %5 yükselirse %50 "
            "kazanırsın — ama %5 düşerse %50 kaybedersin. %10 düşerse tüm paran gider. "
            "Kaldıraç, deneyimsiz yatırımcıların en hızlı para kaybetme yoludur."
        ),
        example="10x kaldıraçla açtığın pozisyonda fiyatın sadece %10 aleyhine gitmesi, sermayenin tamamını silmeye yeter.",
    ),
    dict(
        slug="piyasa-emri-limit-emri",
        term="Piyasa Emri / Limit Emri",
        category="temel",
        short_definition="Piyasa emri anında mevcut fiyattan işlem yapar; limit emri sadece belirlediğin fiyattan işlem yapar.",
        child_explanation=(
            "Pazara gidip 'şu elmadan bir kilo ver, fiyatı neyse ödeyeceğim' demek piyasa "
            "emridir — hemen alırsın ama fiyata karışamazsın. 'Elma kilosu 20 liraya "
            "düşerse haber ver, o zaman alırım' demek ise limit emridir — fiyatı sen "
            "belirlersin ama elma o fiyata düşmezse hiç alamayabilirsin."
        ),
        example="Hisse 105$ iken 100$'a limit alış emri koyarsan, emir sadece fiyat 100$'a inerse gerçekleşir.",
    ),
    dict(
        slug="tahvil-bono",
        term="Tahvil / Bono",
        category="temel",
        short_definition="Devlete veya şirkete borç verip karşılığında düzenli faiz almanı sağlayan borç senedi.",
        child_explanation=(
            "Bir arkadaşına 'sana 100 lira borç veriyorum, bir yıl sonra 110 lira olarak "
            "geri öde' demek gibi. Tahvil alırken aslında devlete ya da şirkete borç "
            "verirsin; onlar da sana belirli aralıklarla faiz öder ve vade sonunda ana "
            "paranı iade eder. Hisse senedinden daha az risklidir ama getirisi de genelde daha düşüktür."
        ),
        example="Yıllık %5 faizli 10.000 dolarlık devlet tahvili alırsan, her yıl 500 dolar faiz kazanırsın.",
    ),
    dict(
        slug="endeks",
        term="Endeks (Index)",
        category="temel",
        short_definition="Bir grup hissenin ortak performansını tek bir sayıyla gösteren ölçüt (örn. S&P 500).",
        child_explanation=(
            "Bir sınıfın başarısını ölçmek için her öğrencinin notuna tek tek bakmak yerine "
            "sınıf ortalamasına bakarsın. Endeks de budur: S&P 500, ABD'nin en büyük 500 "
            "şirketinin 'ortalamasını' tek sayıyla gösterir. Endeks yükseliyorsa piyasa "
            "genel olarak iyi, düşüyorsa genel olarak kötü gidiyor demektir."
        ),
        example="'S&P 500 bugün %2 yükseldi' demek, ABD'nin en büyük 500 şirketinin ortalama değerinin %2 arttığı anlamına gelir.",
    ),
    dict(
        slug="temel-analiz",
        term="Temel Analiz",
        category="teknik-analiz",
        short_definition="Bir şirketin gerçek değerini bilanço, kâr ve büyüme gibi verilerle hesaplama yöntemi.",
        child_explanation=(
            "Bir araba alırken sadece boyasına bakmazsın; motoruna, kilometresine, bakım "
            "geçmişine bakarsın. Temel analiz de şirketin 'motoruna' bakar: ne kadar kâr "
            "ediyor, borcu ne kadar, büyüyor mu? Teknik analiz grafiğe (görünüşe) bakarken, "
            "temel analiz şirketin gerçek sağlığına bakar. İkisi birbirini tamamlar."
        ),
        example="Bir şirketin kârı her yıl artıyorsa ama hisse fiyatı düşük kalmışsa, temel analizci bunu fırsat olarak görebilir.",
    ),
]


# İngilizce çeviriler slug ile eşleştirilir. Şıklar/örnekler aynı anlamı
# taşır; correct_index paylaşıldığı için quiz'de sıra korunur (bkz. seed_quiz).
TERMS_EN = {
    "stop-loss": dict(
        term="Stop-Loss",
        short_definition="An order that automatically sells a stock once its price falls to a set level.",
        child_explanation=(
            "Imagine deciding in advance the most money you're willing to lose at an arcade "
            "machine — 'if I lose this much, I stop.' A stop-loss does the same in the market: "
            "if the price drops to the level you set, the system sells your stock automatically "
            "so you don't lose more."
        ),
        example="If you buy a stock at $100 and set a stop-loss at $90, it sells automatically when the price hits $90.",
    ),
    "rsi": dict(
        term="RSI (Relative Strength Index)",
        short_definition="An indicator that scores whether a stock is 'overbought or oversold' on a 0–100 scale.",
        child_explanation=(
            "Think of a seesaw: once it's tilted far up, coming back down is only a matter of "
            "time. RSI shows how far 'up' or 'down' price has stretched, as a number between 0 "
            "and 100. Above 70 means 'risen a lot, may pull back'; below 30 means 'fallen a "
            "lot, may bounce.'"
        ),
        example="An RSI of 25 is considered 'oversold'; some traders read that as a bargain opportunity.",
    ),
    "hacim": dict(
        term="Volume",
        short_definition="How many shares are bought and sold over a given period.",
        child_explanation=(
            "Think of how many apples are sold at a market on a given day. Volume shows how "
            "many shares change hands in a day. High volume means many people are interested "
            "in that stock; low volume means interest is thin."
        ),
        example="A sudden spike in volume when news breaks shows many people trading at once.",
    ),
    "destek-direnc": dict(
        term="Support / Resistance",
        short_definition="Price levels where the market has repeatedly stalled — 'hard to cross' zones.",
        child_explanation=(
            "When you drop a ball, it stops bouncing past a certain point, right? A support "
            "level is like an invisible floor where a falling price keeps 'stopping' and "
            "rebounding. Resistance is the opposite: an invisible ceiling where a rising price "
            "keeps bumping and turning back."
        ),
        example="If a stock climbs to $50 three times and falls back each time, $50 may be a resistance level.",
    ),
    "pdt-kurali": dict(
        term="PDT Rule (Pattern Day Trader)",
        short_definition="A US rule limiting accounts under $25,000 to no more than 3 day-trades in 5 business days.",
        child_explanation=(
            "Some theme parks have a rule that 'small children can only ride this fast coaster "
            "with a guardian' — for safety. The PDT rule is similar: if someone with less than "
            "$25,000 in their account buys and sells the same stock intraday more than 3 times "
            "in a week, the broker says 'stop, this is too risky, I'm restricting your account.'"
        ),
        example="Trying a 4th day-trade in a week on a sub-$25,000 account will get you warned or blocked.",
    ),
    "hareketli-ortalama": dict(
        term="Moving Average",
        short_definition="A line showing the average closing price of the last X days, smoothing out price swings.",
        child_explanation=(
            "Instead of checking the weather every single day, think of looking at the average "
            "temperature of the last 7 days — you see the general trend rather than daily "
            "spikes. A moving average plots the recent average of price, so you see the overall "
            "direction instead of short-term jumps."
        ),
        example="A 20-day moving average is the average of the last 20 daily closing prices.",
    ),
    "backtest": dict(
        term="Backtest",
        short_definition="Testing a strategy on historical data before risking real money.",
        child_explanation=(
            "Think of driving the same track many times in a simulator before an actual race — "
            "you answer 'does this strategy work?' without real risk. A backtest applies a "
            "trading rule to past real prices and answers 'if I had used this rule in the past, "
            "what would I have made or lost?'"
        ),
        example="Applying 'buy when price crosses above the 20-day average' to the last 3 years of data is a backtest.",
    ),
    "mum-grafigi": dict(
        term="Candlestick Chart",
        short_definition="A chart where each candle shows a day's open, close, high, and low.",
        child_explanation=(
            "Think of each candle as a little story: where price started (open), how high and "
            "how low it went during the day, and where it ended (close). A green candle means "
            "'price rose', a red candle means 'price fell.'"
        ),
        example="A long green candle shows the price rose noticeably from open to close that day.",
    ),
    "portfoy": dict(
        term="Portfolio",
        short_definition="The total of all stocks, funds, and other investments an investor holds.",
        child_explanation=(
            "Think of all the toys in your toy box together — not just one, but everything you "
            "own. A portfolio is the sum of all the stocks, funds, and investments you hold."
        ),
        example="If you hold MU, NVDA, and AAPL, those three together make up your portfolio.",
    ),
    "volatilite": dict(
        term="Volatility",
        short_definition="A measure of how fast and sharply a stock's price swings up and down.",
        child_explanation=(
            "Think of sailing on a calm lake versus a choppy sea — the boat rocks far more on "
            "the choppy sea. A high-volatility stock swings sharply during the day; low "
            "volatility means a calmer, slower-changing price."
        ),
        example="A small tech company's stock is usually more volatile than a large, established one.",
    ),
    "acik-satis": dict(
        term="Short Selling",
        short_definition="Borrowing and selling a stock you expect to fall, to profit from the decline.",
        child_explanation=(
            "Normally you buy first, then sell. Short selling reverses the order: you borrow a "
            "stock you don't own from your broker and sell it immediately. When the price "
            "drops, you buy it back cheaper and return it — the difference is your profit. But "
            "if the price rises, your loss is theoretically unlimited, so it's very risky."
        ),
        example="Short a stock at $100 and it falls to $80 → you make $20. If it rises to $130 → you lose $30.",
    ),
    "boga-ayi-piyasasi": dict(
        term="Bull / Bear Market",
        short_definition="A bull market is a sustained rise; a bear market is a sustained decline.",
        child_explanation=(
            "A bull attacks by thrusting its horns upward — so a rising market is called a bull "
            "market. A bear strikes downward with its paw — so a falling market is a bear "
            "market. Rule of thumb: down more than 20% from the recent peak is a bear market; "
            "up more than 20% is a bull market."
        ),
        example="The long rally in tech stocks after 2020 was a bull market; the sharp 2022 decline was a bear market.",
    ),
    "likidite": dict(
        term="Liquidity",
        short_definition="How easily an asset can be turned into cash without moving its price much.",
        child_explanation=(
            "A glass of water can be poured instantly; a block of ice has to melt first. "
            "Liquidity is the same: a heavily traded stock like Apple is 'water' — you can buy "
            "or sell anytime. A thinly traded small stock is 'ice' — finding a buyer takes time "
            "and you may have to drop the price."
        ),
        example="AAPL, trading millions of shares a day, is highly liquid; a stock trading a few thousand a day is illiquid.",
    ),
    "halka-arz": dict(
        term="IPO (Initial Public Offering)",
        short_definition="A company offering its shares to the public on a stock exchange for the first time.",
        child_explanation=(
            "Imagine a bakery owned only by its founder. Needing money to grow, they say 'I'm "
            "selling small shares of the bakery; if we profit, we win together.' That's an IPO: "
            "the company opens its shares to everyone on the exchange for the first time. The "
            "company raises money, and buyers become part-owners."
        ),
        example="After a tech company's IPO, shares once held only by founders can now be traded on the exchange.",
    ),
    "temettu": dict(
        term="Dividend",
        short_definition="A company distributing part of its profit to shareholders as cash.",
        child_explanation=(
            "Imagine running a lemonade stand with friends. At month-end, part of the earnings "
            "is shared among the partners. A dividend is the same: when a company profits, it "
            "may hand part of it to shareholders saying 'thanks, you're a part-owner.' Not "
            "every company pays dividends — some keep profits to grow."
        ),
        example="If a company declares a $2 per-share dividend and you own 100 shares, $200 lands in your account.",
    ),
    "arbitraj": dict(
        term="Arbitrage",
        short_definition="Making risk-free profit from a price difference for the same asset across markets.",
        child_explanation=(
            "If a bagel is 5 liras in one neighborhood and 7 two streets over, you profit by "
            "buying at 5 and selling at 7. That's exactly arbitrage — exploiting the price gap "
            "of the same thing in two places. In markets these gaps usually close within "
            "seconds, so computers (algorithms) mostly do it."
        ),
        example="If a stock is $100 in New York and $100.5 in London, arbitrageurs buy cheap and sell dear to close the gap.",
    ),
    "spekulasyon": dict(
        term="Speculation",
        short_definition="Taking high risk to profit from short-term price moves.",
        child_explanation=(
            "Investing is like planting a tree and waiting years for its fruit. Speculation is "
            "like stockpiling umbrellas today because 'it'll rain tomorrow and umbrella prices "
            "will rise' — you bet money on a short-term forecast. If right you win fast, if "
            "wrong you lose fast. It's not gambling, but far riskier than investing."
        ),
        example="Buying a stock before tomorrow's earnings on a hunch that 'it'll be good' is a speculative trade.",
    ),
    "hedging": dict(
        term="Hedging",
        short_definition="Opening a second position that works against your main one to reduce potential loss.",
        child_explanation=(
            "Like taking both sunscreen and an umbrella on a picnic: whatever the weather, "
            "you're prepared. Hedging is that — if your stock would lose money in a decline, "
            "you also hold something that gains in a decline. So while one side loses, the "
            "other wins and your total loss is capped."
        ),
        example="Holding tech stocks while also holding an instrument that rises in a market drop is a hedge.",
    ),
    "kaldirac": dict(
        term="Leverage",
        short_definition="Adding borrowed money to your own to open a bigger position — magnifying both gains and losses.",
        child_explanation=(
            "Like a lever that lifts a heavy stone with a small force: with $100 you can trade "
            "$1,000 at 10x leverage. A 5% rise earns you 50% — but a 5% drop loses you 50%, and "
            "a 10% drop wipes you out. Leverage is the fastest way inexperienced traders lose money."
        ),
        example="At 10x leverage, a mere 10% move against you is enough to erase your entire capital.",
    ),
    "piyasa-emri-limit-emri": dict(
        term="Market Order / Limit Order",
        short_definition="A market order trades instantly at the current price; a limit order trades only at your set price.",
        child_explanation=(
            "Going to the market and saying 'give me a kilo of those apples, whatever the "
            "price' is a market order — you buy immediately but can't control the price. Saying "
            "'let me know if apples drop to 20 a kilo, then I'll buy' is a limit order — you set "
            "the price but may never buy if apples don't drop that far."
        ),
        example="With the stock at $105, a limit buy at $100 only fills if the price falls to $100.",
    ),
    "tahvil-bono": dict(
        term="Bond / Bill",
        short_definition="A debt instrument: you lend to a government or company and receive regular interest.",
        child_explanation=(
            "Like telling a friend 'I'm lending you 100, pay me back 110 in a year.' When you "
            "buy a bond you're actually lending to a government or company; they pay you "
            "interest at set intervals and return your principal at maturity. It's less risky "
            "than stocks, but usually lower-returning too."
        ),
        example="Buy a $10,000 government bond at 5% annual interest and you earn $500 in interest each year.",
    ),
    "endeks": dict(
        term="Index",
        short_definition="A benchmark showing the combined performance of a group of stocks with a single number (e.g. S&P 500).",
        child_explanation=(
            "To gauge a class's performance you look at the class average rather than every "
            "student's grade. An index is that: the S&P 500 shows the 'average' of the 500 "
            "largest US companies as one number. If the index rises the market is broadly up; "
            "if it falls, broadly down."
        ),
        example="'The S&P 500 rose 2% today' means the average value of the 500 largest US companies rose 2%.",
    ),
    "temel-analiz": dict(
        term="Fundamental Analysis",
        short_definition="Estimating a company's true value from data like the balance sheet, profit, and growth.",
        child_explanation=(
            "When buying a car you don't just look at the paint; you check the engine, mileage, "
            "and service history. Fundamental analysis looks at the company's 'engine': how "
            "much it profits, how much debt it has, whether it's growing. Technical analysis "
            "looks at the chart (the appearance); fundamental analysis looks at the company's "
            "real health. The two complement each other."
        ),
        example="If a company's profit grows every year but its stock stays cheap, a fundamental analyst may see opportunity.",
    ),
}


def seed_glossary(db: Session) -> None:
    """Eksik terimleri ekler ve İngilizce alanları (varsa boşları) doldurur."""
    existing = {t.slug: t for t in db.query(GlossaryTerm).all()}
    changed = False
    for data in TERMS:
        en = TERMS_EN.get(data["slug"], {})
        if data["slug"] not in existing:
            db.add(GlossaryTerm(
                **data,
                term_en=en.get("term"),
                short_definition_en=en.get("short_definition"),
                child_explanation_en=en.get("child_explanation"),
                example_en=en.get("example"),
            ))
            changed = True
        else:
            # Mevcut kayıtta İngilizce boşsa geri doldur.
            row = existing[data["slug"]]
            if en and row.term_en is None:
                row.term_en = en.get("term")
                row.short_definition_en = en.get("short_definition")
                row.child_explanation_en = en.get("child_explanation")
                row.example_en = en.get("example")
                changed = True
    if changed:
        db.commit()
