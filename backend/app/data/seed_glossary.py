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


def seed_glossary(db: Session) -> None:
    """Eksik terimleri ekler — mevcut kayıtlara dokunmaz, yeni slug'ları tamamlar."""
    existing = {slug for (slug,) in db.query(GlossaryTerm.slug).all()}
    added = False
    for data in TERMS:
        if data["slug"] not in existing:
            db.add(GlossaryTerm(**data))
            added = True
    if added:
        db.commit()
