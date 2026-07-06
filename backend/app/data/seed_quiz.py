"""
Bilgi testi soruları — başlangıç verisi.

Üç konu: temel-kavramlar, teknik-analiz, risk-yonetimi. Her sorunun
explanation alanı, cevap doğru ya da yanlış olsun fark etmeksizin
gösterilir — amaç sınav değil, her seferinde bir şey öğretmek.
"""
import json

from sqlalchemy.orm import Session

from app.models import QuizQuestion

QUESTIONS = [
    # --- Temel Kavramlar ---
    dict(
        topic="temel-kavramlar",
        question_text="Bir hissenin 'mum grafiğinde' yeşil bir mum ne anlama gelir?",
        options=["O gün fiyat düştü", "O gün fiyat yükseldi", "Hiç işlem olmadı", "Şirket temettü ödedi"],
        correct_index=1,
        explanation=(
            "Yeşil (veya bazı platformlarda beyaz) mum, kapanış fiyatının açılış "
            "fiyatından yüksek olduğunu, yani o gün fiyatın yükseldiğini gösterir. "
            "Kırmızı mum ise tam tersini, fiyatın düştüğünü gösterir."
        ),
        related_glossary_slug="mum-grafigi",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="'Portföy' kelimesi trading'de ne anlama gelir?",
        options=[
            "Sadece en çok kazandıran hisse",
            "Bir yatırımcının sahip olduğu tüm yatırımların toplamı",
            "Bir borsanın günlük işlem hacmi",
            "Bir şirketin yıllık geliri",
        ],
        correct_index=1,
        explanation=(
            "Portföy, bir yatırımcının elinde bulunan tüm hisse, fon ve diğer "
            "yatırım araçlarının bütünüdür — tek bir hisse değil, sahip olunan her şeyin toplamı."
        ),
        related_glossary_slug="portfoy",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="PDT (Pattern Day Trader) kuralı kimleri etkiler?",
        options=[
            "Hesabında 25.000 dolardan az olan ve sık gün-içi işlem yapanları",
            "Sadece emeklilik hesabı olanları",
            "Sadece yabancı yatırımcıları",
            "Hiç kimseyi, bu kural artık geçerli değil",
        ],
        correct_index=0,
        explanation=(
            "PDT kuralı, ABD borsalarında 25.000 dolar altı hesabı olan ve 5 iş günü "
            "içinde 3'ten fazla gün-içi (aynı gün alıp satma) işlem yapan yatırımcıları "
            "kısıtlar. Bu kural küçük yatırımcıları aşırı riskli, sık alım-satımdan korumak için var."
        ),
        related_glossary_slug="pdt-kurali",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="Bir backtest size ne gösterir?",
        options=[
            "Stratejinin gelecekte kesin olarak nasıl performans göstereceğini",
            "Stratejinin geçmiş verilerde nasıl performans gösterdiğini",
            "Şirketin yöneticilerinin geçmişini",
            "Borsanın açılış saatini",
        ],
        correct_index=1,
        explanation=(
            "Backtest, bir stratejiyi gerçek parayla denemeden önce geçmiş veriler "
            "üzerinde test etmenizi sağlar. Ama unutmayın: geçmişte işe yaramış olması, "
            "gelecekte de işe yarayacağının garantisi değildir."
        ),
        related_glossary_slug="backtest",
    ),
    # --- Teknik Analiz ---
    dict(
        topic="teknik-analiz",
        question_text="RSI 80 değerini gösteriyorsa bu genellikle ne anlama gelir?",
        options=[
            "Hisse aşırı satılmış, ucuz olabilir",
            "Hisse aşırı alınmış, pahalı olabilir",
            "Şirket iflas etmiş",
            "Hacim sıfıra düşmüş",
        ],
        correct_index=1,
        explanation=(
            "RSI 70'in üzerindeyse genellikle 'aşırı alım' bölgesi olarak yorumlanır — "
            "fiyat çok hızlı yükselmiş olabilir ve bir düzeltme (geri çekilme) gelebilir. "
            "Ama bu kesin bir kural değil, sadece bir ipucu."
        ),
        related_glossary_slug="rsi",
    ),
    dict(
        topic="teknik-analiz",
        question_text="20 günlük hareketli ortalama, 50 günlük hareketli ortalamayı yukarı keserse bu neye işaret eder?",
        options=[
            "Düşüş trendinin güçlendiğine",
            "Yükseliş trendinin başlayabileceğine",
            "Şirketin temettü dağıtacağına",
            "Hiçbir şeye, hareketli ortalamalar anlamsızdır",
        ],
        correct_index=1,
        explanation=(
            "Kısa vadeli ortalamanın (20 gün) uzun vadeli ortalamayı (50 gün) yukarı "
            "kesmesine 'altın kesişim' denir ve genellikle yükseliş trendinin başladığının "
            "bir işareti olarak yorumlanır. Bu strateji platformdaki backtest motorunda da kullanılıyor."
        ),
        related_glossary_slug="hareketli-ortalama",
    ),
    dict(
        topic="teknik-analiz",
        question_text="Bir hisse fiyatı, geçmişte üç kez 100 dolara kadar çıkıp her seferinde geri düşmüşse, 100 dolar seviyesi ne olarak adlandırılır?",
        options=["Destek seviyesi", "Direnç seviyesi", "Stop-loss seviyesi", "Hacim seviyesi"],
        correct_index=1,
        explanation=(
            "Fiyatın yükselirken tekrar tekrar çarpıp geri döndüğü seviyeye direnç denir — "
            "sanki orada görünmez bir tavan var. Tam tersi durumda (fiyatın düşerken durduğu "
            "seviye) ise destek seviyesi denir."
        ),
        related_glossary_slug="destek-direnc",
    ),
    dict(
        topic="teknik-analiz",
        question_text="Bir hissede günlük işlem hacminin aniden çok artması neyi gösterir?",
        options=[
            "Hiçbir şey, hacim önemsizdir",
            "O hisseyle ilgili kayda değer bir ilginin/haberin olduğunu",
            "Şirketin kapandığını",
            "Borsanın tatil olduğunu",
        ],
        correct_index=1,
        explanation=(
            "Hacim, bir hissenin ne kadar 'el değiştirdiğini' gösterir. Ani hacim artışı "
            "genellikle önemli bir haber, kazanç açıklaması ya da piyasa olayının habercisidir."
        ),
        related_glossary_slug="hacim",
    ),
    # --- Risk Yönetimi ---
    dict(
        topic="risk-yonetimi",
        question_text="Stop-loss emri ne işe yarar?",
        options=[
            "Hisseyi otomatik olarak daha yüksek fiyattan satar",
            "Fiyat belirlediğiniz seviyeye düşünce hisseyi otomatik satarak zararı sınırlar",
            "Şirketin temettüsünü artırır",
            "Vergi ödemenizi sağlar",
        ],
        correct_index=1,
        explanation=(
            "Stop-loss, kaybedebileceğiniz en fazla miktarı önceden belirlemenizi sağlar. "
            "Fiyat o seviyeye düşünce pozisyon otomatik kapanır — duygularınızla karar "
            "vermek zorunda kalmazsınız."
        ),
        related_glossary_slug="stop-loss",
    ),
    dict(
        topic="risk-yonetimi",
        question_text="Yüksek volatiliteye sahip bir hisse ne anlama gelir?",
        options=[
            "Fiyatı çok az değişen, sakin bir hisse",
            "Fiyatı sert ve hızlı iniş-çıkışlar yapan bir hisse",
            "Asla zarar etmeyen bir hisse",
            "Sadece büyük şirketlerin sahip olduğu bir özellik",
        ],
        correct_index=1,
        explanation=(
            "Volatilite, fiyatın ne kadar sert dalgalandığını ölçer. Yüksek volatilite hem "
            "büyük kazanç hem de büyük kayıp potansiyeli taşır — bu yüzden risk yönetiminde "
            "dikkate alınması gereken önemli bir faktördür."
        ),
        related_glossary_slug="volatilite",
    ),
    dict(
        topic="risk-yonetimi",
        question_text="Tüm sermayenizi tek bir hisseye yatırmak neden riskli kabul edilir?",
        options=[
            "Riskli değildir, en mantıklı yöntem budur",
            "O hisse düşerse tüm portföyünüz aynı anda etkilenir, çeşitlendirme yapılmamış olur",
            "Borsa kuralları buna izin vermez",
            "Sadece vergi açısından dezavantajlıdır",
        ],
        correct_index=1,
        explanation=(
            "'Yumurtaları aynı sepete koymamak' prensibi burada geçerlidir: tüm parayı tek "
            "bir hisseye yatırırsanız, o şirkette bir sorun çıktığında tüm portföyünüz aynı "
            "anda zarar görür. Çeşitlendirme bu riski azaltır."
        ),
        related_glossary_slug="portfoy",
    ),
    # --- Yeni terimlerden üretilen sorular ---
    dict(
        topic="temel-kavramlar",
        question_text="Açığa satış (short selling) yapan bir yatırımcı ne zaman kâr eder?",
        options=[
            "Hisse fiyatı yükselince",
            "Hisse fiyatı düşünce",
            "Şirket temettü dağıtınca",
            "Hisse fiyatı hiç değişmeyince",
        ],
        correct_index=1,
        explanation=(
            "Açığa satışta önce ödünç alınan hisse satılır, fiyat düşünce daha ucuza geri "
            "alınıp iade edilir — aradaki fark kârdır. Ancak fiyat yükselirse zarar teorik "
            "olarak sınırsızdır, bu yüzden çok riskli bir işlemdir."
        ),
        related_glossary_slug="acik-satis",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="'Ayı piyasası' ne anlama gelir?",
        options=[
            "Fiyatların uzun süreli yükseldiği dönem",
            "Fiyatların uzun süreli düştüğü dönem",
            "Borsanın tatil olduğu dönem",
            "Sadece hayvancılık şirketlerinin işlem gördüğü piyasa",
        ],
        correct_index=1,
        explanation=(
            "Ayı pençesiyle yukarıdan aşağıya vurur — düşen piyasaya bu yüzden ayı piyasası "
            "denir. Genel kabul, fiyatların zirveden %20'den fazla düşmesidir. Tersine, "
            "uzun süreli yükselişe boğa piyasası denir."
        ),
        related_glossary_slug="boga-ayi-piyasasi",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="Yüksek likiditeye sahip bir hisse ne demektir?",
        options=[
            "Fiyatı çok yüksek bir hisse",
            "Fiyatı fazla etkilemeden kolayca alınıp satılabilen bir hisse",
            "Sadece bankaların alabildiği bir hisse",
            "Temettü ödemeyen bir hisse",
        ],
        correct_index=1,
        explanation=(
            "Likidite, bir varlığın nakde çevrilme kolaylığıdır. Çok işlem gören hisselerde "
            "istediğin an alıcı/satıcı bulursun; az işlem görenlerde satmak istediğinde "
            "fiyatı düşürmek zorunda kalabilirsin."
        ),
        related_glossary_slug="likidite",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="Halka arz (IPO) nedir?",
        options=[
            "Şirketin iflasını açıklaması",
            "Şirketin hisselerini ilk kez borsada halka satışa sunması",
            "Şirketin başka bir şirketi satın alması",
            "Devletin şirkete el koyması",
        ],
        correct_index=1,
        explanation=(
            "Halka arzda şirket, o güne kadar sadece kurucuların/ortakların elinde olan "
            "hisselerini ilk kez borsada herkese satışa açar. Şirket böylece büyümek için "
            "para toplar, hisse alanlar da şirkete ortak olur."
        ),
        related_glossary_slug="halka-arz",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="Temettü (dividend) nedir?",
        options=[
            "Hisse alırken ödenen komisyon",
            "Şirketin kârının bir kısmını hissedarlarına dağıtması",
            "Borsaya giriş ücreti",
            "Hisse fiyatındaki günlük değişim",
        ],
        correct_index=1,
        explanation=(
            "Şirket kâr edince bunun bir kısmını hisse sahiplerine nakit olarak dağıtabilir — "
            "buna temettü denir. Her şirket temettü vermez; hızlı büyüyen şirketler genelde "
            "kârı büyüme için şirkette tutar."
        ),
        related_glossary_slug="temettu",
    ),
    dict(
        topic="risk-yonetimi",
        question_text="10x kaldıraçla işlem yapan bir yatırımcı için fiyatın %10 aleyhine gitmesi ne anlama gelir?",
        options=[
            "%10 zarar eder",
            "Hiçbir şey olmaz",
            "Sermayesinin tamamını kaybedebilir",
            "%10 kâr eder",
        ],
        correct_index=2,
        explanation=(
            "Kaldıraç kârı da zararı da katlar: 10x kaldıraçta fiyattaki %10'luk ters hareket, "
            "%100 zarara — yani sermayenin tamamının silinmesine — denk gelir. Bu yüzden "
            "kaldıraç, deneyimsiz yatırımcılar için en tehlikeli araçlardan biridir."
        ),
        related_glossary_slug="kaldirac",
    ),
    dict(
        topic="risk-yonetimi",
        question_text="Hedging (riskten korunma) ne yapar?",
        options=[
            "Kârı garantiler",
            "Ana pozisyonun tersine çalışan bir pozisyonla olası zararı sınırlar",
            "Vergiden muaf olmayı sağlar",
            "Hisse fiyatını sabitler",
        ],
        correct_index=1,
        explanation=(
            "Hedging, 'hem güneş kremi hem şemsiye almak' gibidir: elindeki varlık zarar "
            "ederse kazanan başka bir pozisyon açarsın. Kârı garantilemez ama büyük "
            "kayıpları sınırlar — bunun bedeli de genelde bir miktar potansiyel kârdan vazgeçmektir."
        ),
        related_glossary_slug="hedging",
    ),
    dict(
        topic="risk-yonetimi",
        question_text="Spekülasyon ile uzun vadeli yatırım arasındaki temel fark nedir?",
        options=[
            "Spekülasyon kısa vadeli fiyat tahminine dayanır ve daha risklidir",
            "Spekülasyon her zaman daha kârlıdır",
            "Uzun vadeli yatırım yasa dışıdır",
            "Aralarında hiçbir fark yoktur",
        ],
        correct_index=0,
        explanation=(
            "Yatırım, bir şirketin uzun vadeli büyümesine ortak olmaktır. Spekülasyon ise "
            "kısa vadeli fiyat hareketini tahmin edip ondan kâr etmeye çalışmaktır — tahmin "
            "tutmazsa kayıp da hızlı olur. İkisi de meşrudur ama risk profilleri çok farklıdır."
        ),
        related_glossary_slug="spekulasyon",
    ),
    dict(
        topic="teknik-analiz",
        question_text="Temel analiz ile teknik analiz arasındaki fark nedir?",
        options=[
            "Temel analiz şirketin finansal sağlığına, teknik analiz fiyat grafiğine bakar",
            "İkisi de sadece grafiğe bakar",
            "Teknik analiz sadece tahvillerde kullanılır",
            "Temel analiz sadece kripto paralarda geçerlidir",
        ],
        correct_index=0,
        explanation=(
            "Temel analiz şirketin 'motoruna' bakar: kâr, borç, büyüme. Teknik analiz ise "
            "fiyat ve hacim grafiklerindeki örüntülere bakar. Birçok yatırımcı ikisini "
            "birlikte kullanır: temel analizle 'ne alacağını', teknik analizle 'ne zaman alacağını' belirler."
        ),
        related_glossary_slug="temel-analiz",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="Limit emri ile piyasa emri arasındaki fark nedir?",
        options=[
            "Limit emri sadece belirlediğin fiyattan, piyasa emri anında mevcut fiyattan işlem yapar",
            "İkisi de aynıdır",
            "Piyasa emri sadece kapanışta çalışır",
            "Limit emri sadece satış için kullanılır",
        ],
        correct_index=0,
        explanation=(
            "Piyasa emri 'hemen al/sat, fiyat neyse kabul' der — hız önceliklidir. Limit "
            "emri 'sadece şu fiyattan al/sat' der — fiyat kontrolü önceliklidir ama emir "
            "hiç gerçekleşmeyebilir. Volatil hisselerde limit emri sürpriz fiyatlardan korur."
        ),
        related_glossary_slug="piyasa-emri-limit-emri",
    ),
    dict(
        topic="temel-kavramlar",
        question_text="S&P 500 endeksi neyi ölçer?",
        options=[
            "ABD'nin en büyük 500 şirketinin ortak performansını",
            "Sadece 500 dolarlık hisseleri",
            "Avrupa borsalarının toplamını",
            "Altın fiyatını",
        ],
        correct_index=0,
        explanation=(
            "Endeks, bir grup hissenin ortalamasını tek sayıyla gösterir — sınıf ortalaması "
            "gibi. S&P 500, ABD'nin en büyük 500 şirketini kapsar ve 'piyasa bugün nasıl?' "
            "sorusunun en yaygın cevabıdır."
        ),
        related_glossary_slug="endeks",
    ),
    # --- Grafik Okuma (Teknik Analiz Eğitimi dersleriyle eşleşen test) ---
    dict(
        topic="grafik-okuma",
        question_text="Yükselen bir trendde piyasa yapısı nasıl görünür?",
        options=[
            "Lower High (LH) ve Lower Low (LL) dizisi",
            "Higher High (HH) ve Higher Low (HL) dizisi",
            "Sadece yatay hareket",
            "Rastgele tepe ve dipler",
        ],
        correct_index=1,
        explanation=(
            "Yükselen trend, her tepenin bir öncekinden yüksek (HH) ve her dibin bir "
            "öncekinden yüksek (HL) olduğu yapıdır. Bu dizi bozulduğunda — örneğin fiyat "
            "bir öncekinden düşük dip (LL) yaptığında — trendin zayıfladığının ilk sinyalidir."
        ),
        related_glossary_slug="destek-direnc",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Kırılan bir direnç seviyesi genellikle neye dönüşür?",
        options=["Yeni bir dirence", "Desteğe", "Stop-loss seviyesine", "Hiçbir şeye — anlamını yitirir"],
        correct_index=1,
        explanation=(
            "Teknik analizin klasik kuralı: kırılan direnç desteğe dönüşür (rol değişimi). "
            "O seviyeden alamayanlar geri çekilmede alıcı olur, kıranlar da pozisyonlarını savunur — "
            "bu yüzden fiyat kırdığı seviyeye geri test için döndüğünde genelde tepki alır."
        ),
        related_glossary_slug="destek-direnc",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Düşüş trendinin dibinde uzun alt fitilli, küçük gövdeli bir mum (çekiç/hammer) ne anlatır?",
        options=[
            "Satıcıların tamamen kazandığını",
            "Gün içinde satıcılar bastırdı ama alıcılar fiyatı geri yukarı taşıdı — potansiyel dip sinyali",
            "Hacmin sıfır olduğunu",
            "Piyasanın kapalı olduğunu",
        ],
        correct_index=1,
        explanation=(
            "Çekiç mumunda fiyat gün içinde sert düşer (uzun alt fitil) ama kapanışa doğru "
            "toparlar. Bu, satış baskısının emildiğini gösterir. Tek başına yetmez — destek "
            "bölgesinde ve yüksek hacimle oluşursa anlamı güçlenir."
        ),
        related_glossary_slug="mum-grafigi",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Altın Kesişim (Golden Cross) nedir?",
        options=[
            "RSI'ın 50'yi kesmesi",
            "50 günlük ortalamanın 200 günlük ortalamayı yukarı kesmesi",
            "Fiyatın altın fiyatını geçmesi",
            "İki mumun aynı renkte olması",
        ],
        correct_index=1,
        explanation=(
            "Altın Kesişim, 50 günlük ortalamanın 200 günlüğü yukarı kesmesidir ve uzun "
            "vadeli yükselişin teyidi sayılır. Tersi (50'nin 200 altına inmesi) Ölüm "
            "Kesişimidir. Gecikmeli sinyallerdir: trendi başlatmaz, doğrular."
        ),
        related_glossary_slug="hareketli-ortalama",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Güçlü bir yükseliş trendinde RSI'ın uzun süre 70 üzerinde kalması ne anlama gelir?",
        options=[
            "Hemen satmak gerekir, düşüş kesindir",
            "Güçlü trendlerde RSI aşırı bölgede uzun süre kalabilir — tek başına satış sinyali değildir",
            "RSI bozulmuştur",
            "Hisse işleme kapatılır",
        ],
        correct_index=1,
        explanation=(
            "Osilatörlerin en çok yanlış anlaşılan yönü budur: güçlü trendde RSI haftalarca "
            "aşırı alımda kalabilir ve fiyat yükselmeye devam eder. 'RSI 70 = sat' kuralı "
            "yatay piyasada işe yarar; trendli piyasada erken sattırır."
        ),
        related_glossary_slug="rsi",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Bollinger Bantlarının aşırı daralması (squeeze) neyin habercisidir?",
        options=[
            "Fiyatın kesin yükseleceğinin",
            "Fiyatın kesin düşeceğinin",
            "Yakında büyük bir hareketin gelebileceğinin — ama yönünü söylemez",
            "Temettü dağıtımının",
        ],
        correct_index=2,
        explanation=(
            "Bantlar volatiliteyle nefes alır: daralma, piyasanın sıkıştığını ve enerji "
            "biriktirdiğini gösterir. Sıkışma sonrası genelde sert bir hareket gelir ama "
            "yön bilgisi vermez — yönü kırılım ve hacim teyidi belirler."
        ),
        related_glossary_slug="volatilite",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Direnç kırılımında (breakout) hacim neden önemlidir?",
        options=[
            "Önemli değildir",
            "Düşük hacimli kırılımlar genelde yanlış çıkar (fakeout); gerçek kırılım ortalamanın üstünde hacim ister",
            "Hacim sadece düşüşlerde önemlidir",
            "Hacim yüksekse kırılım her zaman başarısız olur",
        ],
        correct_index=1,
        explanation=(
            "Kırılım, o seviyeyi savunanların yenildiği andır — gerçekse çok sayıda katılımcı "
            "gerektirir, bu da hacimde görünür. Ortalamanın altında hacimle olan kırılımların "
            "çoğu geri döner (fakeout). Hacim teyidi, kırılım işlemlerinin en kritik filtresidir."
        ),
        related_glossary_slug="hacim",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Konsolidasyon sırasında hacmin kuruması (Volume Dry-Up, VDU) ne anlama gelir?",
        options=[
            "Hisse ölmüştür, uzak durulmalı",
            "Satıcıların azaldığını gösterir — patlama öncesi sessizlik olabilir",
            "Şirketin iflas ettiğini",
            "Verinin hatalı olduğunu",
        ],
        correct_index=1,
        explanation=(
            "Sıkışma bölgesinde hacmin ortalamanın çok altına inmesi, satmak isteyen herkesin "
            "sattığını, arzın kuruduğunu gösterir. Minervini/Qullamaggie tarzı momentum "
            "stratejilerinde VDU, kırılım öncesi aranan işaretlerden biridir."
        ),
        related_glossary_slug="hacim",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Fiyat %38.2 Fibonacci seviyesinde durup trend yönüne dönerse bu nasıl yorumlanır?",
        options=[
            "Trend zayıftır",
            "Sığ düzeltme — trend güçlü demektir",
            "Fibonacci çalışmamıştır",
            "Piyasa manipüle edilmiştir",
        ],
        correct_index=1,
        explanation=(
            "Düzeltmenin derinliği trendin sağlığını gösterir: %23.6-38.2 gibi sığ "
            "düzeltmelerden dönen fiyat, alıcıların sabırsız olduğunu ve trendin güçlü "
            "olduğunu anlatır. %61.8'in kaybı ise hareketin sorgulanmasıdır."
        ),
        related_glossary_slug="destek-direnc",
    ),
    dict(
        topic="grafik-okuma",
        question_text="1:2 Risk/Ödül oranıyla işlem yapan bir trader, işlemlerinin sadece %40'ını kazansa ne olur?",
        options=[
            "Kesin zarar eder",
            "Başa baş kalır",
            "Uzun vadede kâr eder — beklentisi (expectancy) pozitiftir",
            "Hesabı kapatılır",
        ],
        correct_index=2,
        explanation=(
            "Hesap: 100 işlemde 40 kazanç × 2R − 60 kayıp × 1R = 80R − 60R = +20R. "
            "İsabet oranı %50'nin altında olsa bile kazançların kayıplardan büyük olması "
            "sistemi kârlı yapar. Bu yüzden profesyoneller isabet oranından çok R:R'ye odaklanır."
        ),
        related_glossary_slug="stop-loss",
    ),
    dict(
        topic="grafik-okuma",
        question_text="ATR bazlı stop-loss, sabit yüzdeli stop'a göre neden daha mantıklıdır?",
        options=[
            "Daha az matematik gerektirir",
            "Hissenin kendi volatilitesine uyum sağlar: oynak hissede geniş, sakin hissede dar durur",
            "Her zaman daha yakın durur",
            "Komisyonu düşürür",
        ],
        correct_index=1,
        explanation=(
            "Günde %5 oynayan bir hisseye %2'lik stop koyarsan normal gürültüyle stop olursun; "
            "günde %0.5 oynayan hisseye %10'luk stop koyarsan gereksiz risk alırsın. ATR, "
            "hissenin gerçek günlük hareketini ölçtüğü için stop mesafesini hisseye göre ayarlar."
        ),
        related_glossary_slug="volatilite",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Bireysel hisse ne kadar güçlü görünürse görünsün, genel piyasa (SPY/QQQ) düşüş trendindeyse ne beklenir?",
        options=[
            "Hiçbir etkisi olmaz",
            "Kırılımların (breakout) çoğu başarısız olur — piyasa geneli bireysel hisseyi bastırır",
            "Hisse daha hızlı yükselir",
            "Hacim otomatik artar",
        ],
        correct_index=1,
        explanation=(
            "Hisselerin büyük çoğunluğu genel piyasayla birlikte hareket eder. Ayı "
            "piyasasında en güçlü görünen kırılımlar bile çoğunlukla satışla karşılanır. "
            "Bu yüzden deneyimli trader'lar önce piyasanın yönüne (SPY/QQQ trendine) bakar, "
            "sonra hisse seçer — O'Neil ve Minervini'nin sisteminin temelidir."
        ),
        related_glossary_slug="endeks",
    ),
    # --- Qullamaggie Swing Stratejisi ---
    dict(
        topic="grafik-okuma",
        question_text="Qullamaggie'nin Breakout setup'ında giriş ne zaman yapılır?",
        options=[
            "Konsolidasyon içinde, kırılımı önceden tahmin ederek",
            "Konsolidasyon tepesi yüksek hacimle kırıldıktan sonra (opening range high)",
            "Fiyat 200 günlük ortalamanın altına inince",
            "RSI 30'un altına düşünce",
        ],
        correct_index=1,
        explanation=(
            "Qullamaggie asla tahmin etmez: 'kırılacak gibi duruyor' diye içeride beklemez. "
            "Kırılım gerçekleştikten sonra, açılış aralığının (ilk 1/5/60 dk mumun) tepesi "
            "aşılınca girer. Stop günün dibindedir ve risk hesabın %0.25-1'ini geçmez."
        ),
        related_glossary_slug="destek-direnc",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Episodic Pivot (EP) setup'ında hissenin son 3-6 ayda rally YAPMAMIŞ olması neden istenir?",
        options=[
            "Ucuz hisse daha çok kazandırdığı için",
            "Haber sürpriz olmalı — zaten koşmuş hissede haber çoğunlukla fiyatlanmıştır",
            "Komisyonlar düşük olduğu için",
            "PDT kuralından kaçınmak için",
        ],
        correct_index=1,
        explanation=(
            "EP'nin gücü sürprizdedir: beklenmedik kazanç/haber, hisseyi yeni sahiplerine "
            "aylarca taşıtacak taze bir hikâye başlatır. Aylardır yükselen hissede aynı haber "
            "'beklenen haber' olur ve çoğu kez 'haberi sat' tepkisi gelir."
        ),
        related_glossary_slug="hacim",
    ),
    dict(
        topic="grafik-okuma",
        question_text="Qullamaggie kazanan pozisyonun kalan kısmını ne zamana kadar taşır?",
        options=[
            "%5 kâr edince hepsini satar",
            "Fiyat 10 veya 20 günlük hareketli ortalamayı aşağı kırana kadar",
            "Tam bir yıl",
            "RSI 70 olana kadar",
        ],
        correct_index=1,
        explanation=(
            "Sistemin asimetrisi buradadır: ilk 3-5 günde pozisyonun 1/3-1/2'si satılır "
            "(maliyet güvenceye alınır), kalanı 10/20 günlük ortalama trend bozulana kadar "
            "taşınır. Boğa piyasasında bu, 10-20R'lik hareketleri yakalamayı sağlar — "
            "küçük sabit risk, açık uçlu kazanç."
        ),
        related_glossary_slug="hareketli-ortalama",
    ),
]


def seed_quiz(db: Session) -> None:
    """Eksik soruları ekler — mevcut kayıtlara dokunmaz, yeni soruları tamamlar."""
    existing = {text for (text,) in db.query(QuizQuestion.question_text).all()}
    added = False
    for q in QUESTIONS:
        if q["question_text"] in existing:
            continue
        db.add(
            QuizQuestion(
                topic=q["topic"],
                question_text=q["question_text"],
                options_json=json.dumps(q["options"], ensure_ascii=False),
                correct_index=q["correct_index"],
                explanation=q["explanation"],
                related_glossary_slug=q.get("related_glossary_slug"),
            )
        )
        added = True
    if added:
        db.commit()
