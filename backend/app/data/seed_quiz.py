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


# İngilizce çeviriler QUESTIONS ile AYNI SIRADA. Şık sırası birebir korunur
# (correct_index paylaşıldığı için kritik). Her giriş: question_text, options, explanation.
QUESTIONS_EN = [
    dict(
        question_text="What does a green candle on a stock's candlestick chart mean?",
        options=["Price fell that day", "Price rose that day", "No trading occurred", "The company paid a dividend"],
        explanation=(
            "A green (or white, on some platforms) candle means the close was higher than the "
            "open — i.e. the price rose that day. A red candle means the opposite, that price fell."
        ),
    ),
    dict(
        question_text="What does the word 'portfolio' mean in trading?",
        options=[
            "Only the best-performing stock",
            "The total of all investments an investor holds",
            "A stock exchange's daily trading volume",
            "A company's annual revenue",
        ],
        explanation=(
            "A portfolio is the whole of all stocks, funds, and other investment instruments an "
            "investor holds — not a single stock, but the total of everything owned."
        ),
    ),
    dict(
        question_text="Who does the PDT (Pattern Day Trader) rule affect?",
        options=[
            "Those with under $25,000 who trade intraday frequently",
            "Only those with a retirement account",
            "Only foreign investors",
            "No one — the rule no longer applies",
        ],
        explanation=(
            "The PDT rule restricts investors on US exchanges who have under $25,000 in their "
            "account and make more than 3 intraday (same-day buy-and-sell) trades within 5 "
            "business days. It exists to protect small investors from overly risky, frequent trading."
        ),
    ),
    dict(
        question_text="What does a backtest show you?",
        options=[
            "Exactly how the strategy will perform in the future",
            "How the strategy performed on historical data",
            "The background of the company's executives",
            "The market's opening time",
        ],
        explanation=(
            "A backtest lets you test a strategy on historical data before risking real money. "
            "But remember: having worked in the past is no guarantee it will work in the future."
        ),
    ),
    dict(
        question_text="If RSI reads 80, what does that usually mean?",
        options=[
            "The stock is oversold and may be cheap",
            "The stock is overbought and may be expensive",
            "The company has gone bankrupt",
            "Volume has dropped to zero",
        ],
        explanation=(
            "An RSI above 70 is usually read as 'overbought' — price may have risen too fast and "
            "a pullback could follow. But it's not a hard rule, just a hint."
        ),
    ),
    dict(
        question_text="If the 20-day moving average crosses above the 50-day moving average, what does it signal?",
        options=[
            "A strengthening downtrend",
            "A potential start of an uptrend",
            "The company will pay a dividend",
            "Nothing — moving averages are meaningless",
        ],
        explanation=(
            "The short-term average (20-day) crossing above the long-term average (50-day) is "
            "called a 'golden cross' and is usually read as a sign that an uptrend has begun. "
            "This strategy is also used in the platform's backtest engine."
        ),
    ),
    dict(
        question_text="If a stock's price has risen to $100 three times in the past and fallen back each time, what is the $100 level called?",
        options=["Support level", "Resistance level", "Stop-loss level", "Volume level"],
        explanation=(
            "The level a rising price repeatedly bumps into and turns back from is called "
            "resistance — as if there's an invisible ceiling there. The opposite (where a falling "
            "price stops) is called support."
        ),
    ),
    dict(
        question_text="What does a sudden sharp rise in a stock's daily trading volume indicate?",
        options=[
            "Nothing — volume is irrelevant",
            "There's notable interest or news about that stock",
            "The company has shut down",
            "The exchange is on holiday",
        ],
        explanation=(
            "Volume shows how much a stock is 'changing hands.' A sudden volume spike usually "
            "heralds important news, an earnings release, or a market event."
        ),
    ),
    dict(
        question_text="What does a stop-loss order do?",
        options=[
            "Automatically sells the stock at a higher price",
            "Automatically sells the stock when price falls to your set level, limiting the loss",
            "Increases the company's dividend",
            "Handles your tax payments",
        ],
        explanation=(
            "A stop-loss lets you decide in advance the most you can lose. When price falls to "
            "that level the position closes automatically — you don't have to decide with your emotions."
        ),
    ),
    dict(
        question_text="What does a high-volatility stock mean?",
        options=[
            "A calm stock whose price barely changes",
            "A stock whose price makes sharp, fast swings",
            "A stock that never loses money",
            "A feature only large companies have",
        ],
        explanation=(
            "Volatility measures how sharply price swings. High volatility carries both large "
            "gain and large loss potential — which is why it's an important factor in risk management."
        ),
    ),
    dict(
        question_text="Why is putting all your capital into a single stock considered risky?",
        options=[
            "It isn't risky — it's the most sensible approach",
            "If that stock falls, your whole portfolio is hit at once — no diversification",
            "Exchange rules don't allow it",
            "It's only disadvantageous for tax reasons",
        ],
        explanation=(
            "The 'don't put all your eggs in one basket' principle applies: if you put all your "
            "money in one stock, any problem at that company hits your whole portfolio at once. "
            "Diversification reduces this risk."
        ),
    ),
    dict(
        question_text="When does a short seller make a profit?",
        options=[
            "When the stock price rises",
            "When the stock price falls",
            "When the company pays a dividend",
            "When the stock price never changes",
        ],
        explanation=(
            "In short selling the borrowed stock is sold first, then bought back cheaper when "
            "price falls — the difference is profit. But if price rises the loss is theoretically "
            "unlimited, which makes it very risky."
        ),
    ),
    dict(
        question_text="What does a 'bear market' mean?",
        options=[
            "A period of sustained rising prices",
            "A period of sustained falling prices",
            "A period when the exchange is closed",
            "A market where only livestock companies trade",
        ],
        explanation=(
            "A bear strikes downward with its paw — so a falling market is called a bear market. "
            "The common definition is a drop of more than 20% from the peak. Conversely, a "
            "sustained rise is a bull market."
        ),
    ),
    dict(
        question_text="What does a highly liquid stock mean?",
        options=[
            "A stock with a very high price",
            "A stock that can be bought and sold easily without moving its price much",
            "A stock only banks can buy",
            "A stock that pays no dividend",
        ],
        explanation=(
            "Liquidity is how easily an asset turns into cash. In heavily traded stocks you find "
            "a buyer/seller anytime; in thinly traded ones you may have to drop the price to sell."
        ),
    ),
    dict(
        question_text="What is an IPO (Initial Public Offering)?",
        options=[
            "A company announcing bankruptcy",
            "A company offering its shares to the public on an exchange for the first time",
            "A company acquiring another company",
            "The government seizing a company",
        ],
        explanation=(
            "In an IPO a company opens shares — previously held only by founders/partners — to "
            "everyone on the exchange for the first time. The company raises money to grow, and "
            "buyers become part-owners."
        ),
    ),
    dict(
        question_text="What is a dividend?",
        options=[
            "A commission paid when buying a stock",
            "A company distributing part of its profit to shareholders",
            "An entry fee to the stock exchange",
            "The daily change in a stock's price",
        ],
        explanation=(
            "When a company profits it may distribute part of it to shareholders as cash — that's "
            "a dividend. Not every company pays one; fast-growing companies usually keep profits to grow."
        ),
    ),
    dict(
        question_text="For an investor trading at 10x leverage, what does a 10% move against them mean?",
        options=[
            "They lose 10%",
            "Nothing happens",
            "They can lose their entire capital",
            "They gain 10%",
        ],
        explanation=(
            "Leverage magnifies both gains and losses: at 10x, a 10% adverse move equals a 100% "
            "loss — wiping out your entire capital. That's why leverage is one of the most "
            "dangerous tools for inexperienced investors."
        ),
    ),
    dict(
        question_text="What does hedging do?",
        options=[
            "Guarantees a profit",
            "Limits potential loss with a position that works against your main one",
            "Makes you tax-exempt",
            "Fixes the stock price",
        ],
        explanation=(
            "Hedging is like 'taking both sunscreen and an umbrella': if your asset loses money, "
            "you open another position that gains. It doesn't guarantee profit but caps large "
            "losses — the cost is usually giving up some potential gain."
        ),
    ),
    dict(
        question_text="What is the key difference between speculation and long-term investing?",
        options=[
            "Speculation relies on short-term price forecasts and is riskier",
            "Speculation is always more profitable",
            "Long-term investing is illegal",
            "There is no difference",
        ],
        explanation=(
            "Investing means sharing in a company's long-term growth. Speculation is trying to "
            "predict short-term price moves and profit from them — if the guess fails, the loss "
            "is fast too. Both are legitimate but their risk profiles differ greatly."
        ),
    ),
    dict(
        question_text="What is the difference between fundamental analysis and technical analysis?",
        options=[
            "Fundamental analysis looks at the company's financial health, technical at the price chart",
            "Both only look at the chart",
            "Technical analysis is only used for bonds",
            "Fundamental analysis only applies to cryptocurrencies",
        ],
        explanation=(
            "Fundamental analysis looks at the company's 'engine': profit, debt, growth. Technical "
            "analysis looks at patterns in price and volume charts. Many investors use both: "
            "fundamentals to decide 'what to buy', technicals to decide 'when to buy'."
        ),
    ),
    dict(
        question_text="What is the difference between a limit order and a market order?",
        options=[
            "A limit order trades only at your set price; a market order trades instantly at the current price",
            "They are the same",
            "A market order only works at the close",
            "A limit order is only used for selling",
        ],
        explanation=(
            "A market order says 'buy/sell now, whatever the price' — speed first. A limit order "
            "says 'buy/sell only at this price' — price control first, but the order may never "
            "fill. In volatile stocks a limit order protects you from surprise prices."
        ),
    ),
    dict(
        question_text="What does the S&P 500 index measure?",
        options=[
            "The combined performance of the 500 largest US companies",
            "Only stocks priced at $500",
            "The sum of European exchanges",
            "The price of gold",
        ],
        explanation=(
            "An index shows the average of a group of stocks as one number — like a class average. "
            "The S&P 500 covers the 500 largest US companies and is the most common answer to "
            "'how's the market today?'"
        ),
    ),
    dict(
        question_text="What does market structure look like in an uptrend?",
        options=[
            "A sequence of Lower Highs (LH) and Lower Lows (LL)",
            "A sequence of Higher Highs (HH) and Higher Lows (HL)",
            "Only sideways movement",
            "Random peaks and troughs",
        ],
        explanation=(
            "An uptrend is a structure where each peak is higher than the last (HH) and each "
            "trough is higher than the last (HL). When this sequence breaks — e.g. price makes a "
            "lower low (LL) — it's the first sign the trend is weakening."
        ),
    ),
    dict(
        question_text="What does a broken resistance level usually turn into?",
        options=["A new resistance", "Support", "A stop-loss level", "Nothing — it loses its meaning"],
        explanation=(
            "A classic technical-analysis rule: broken resistance turns into support (role "
            "reversal). Those who couldn't buy at that level become buyers on the pullback, and "
            "those who broke it defend their positions — so when price returns to retest the "
            "level, it usually finds a reaction."
        ),
    ),
    dict(
        question_text="At the bottom of a downtrend, what does a candle with a long lower wick and small body (hammer) tell you?",
        options=[
            "That sellers won completely",
            "Sellers pressed during the day but buyers pushed price back up — a potential bottom signal",
            "That volume was zero",
            "That the market was closed",
        ],
        explanation=(
            "In a hammer candle price falls sharply during the day (long lower wick) but recovers "
            "toward the close. This shows selling pressure was absorbed. It's not enough alone — "
            "its meaning strengthens if it forms at a support zone and on high volume."
        ),
    ),
    dict(
        question_text="What is a Golden Cross?",
        options=[
            "RSI crossing 50",
            "The 50-day average crossing above the 200-day average",
            "Price exceeding the price of gold",
            "Two candles being the same color",
        ],
        explanation=(
            "A Golden Cross is the 50-day average crossing above the 200-day, seen as confirmation "
            "of a long-term uptrend. The opposite (50 falling below 200) is a Death Cross. These "
            "are lagging signals: they don't start the trend, they confirm it."
        ),
    ),
    dict(
        question_text="In a strong uptrend, what does RSI staying above 70 for a long time mean?",
        options=[
            "You must sell immediately, a decline is certain",
            "In strong trends RSI can stay in the extreme zone for a long time — it's not a sell signal by itself",
            "RSI is broken",
            "The stock is halted from trading",
        ],
        explanation=(
            "This is the most misunderstood aspect of oscillators: in a strong trend RSI can stay "
            "overbought for weeks while price keeps rising. The 'RSI 70 = sell' rule works in a "
            "sideways market; in a trending market it makes you sell too early."
        ),
    ),
    dict(
        question_text="What does an extreme squeeze in the Bollinger Bands herald?",
        options=[
            "That price will certainly rise",
            "That price will certainly fall",
            "That a big move may come soon — but it doesn't tell the direction",
            "A dividend distribution",
        ],
        explanation=(
            "The bands breathe with volatility: a squeeze shows the market is compressing and "
            "building energy. A sharp move usually follows a squeeze, but it gives no direction — "
            "the breakout and volume confirmation decide direction."
        ),
    ),
    dict(
        question_text="Why does volume matter on a resistance breakout?",
        options=[
            "It doesn't matter",
            "Low-volume breakouts often turn out false (fakeout); a real breakout needs above-average volume",
            "Volume only matters in declines",
            "If volume is high the breakout always fails",
        ],
        explanation=(
            "A breakout is the moment defenders of a level are beaten — if real, it takes many "
            "participants, which shows up in volume. Most breakouts on below-average volume come "
            "back (fakeout). Volume confirmation is the most critical filter for breakout trades."
        ),
    ),
    dict(
        question_text="What does Volume Dry-Up (VDU) during consolidation mean?",
        options=[
            "The stock is dead, stay away",
            "It shows sellers are thinning out — it can be the calm before the breakout",
            "That the company has gone bankrupt",
            "That the data is faulty",
        ],
        explanation=(
            "Volume dropping far below average in a consolidation zone shows everyone who wanted "
            "to sell has sold — supply has dried up. In Minervini/Qullamaggie-style momentum "
            "strategies, VDU is one of the signs sought before a breakout."
        ),
    ),
    dict(
        question_text="If price stops at the 38.2% Fibonacci level and turns back in the trend direction, how is that read?",
        options=[
            "The trend is weak",
            "A shallow retracement — meaning the trend is strong",
            "Fibonacci didn't work",
            "The market is manipulated",
        ],
        explanation=(
            "The depth of a retracement shows the trend's health: price turning from a shallow "
            "retracement (like 23.6–38.2%) shows buyers are impatient and the trend is strong. "
            "Losing the 61.8% level, by contrast, questions the move."
        ),
    ),
    dict(
        question_text="With a 1:2 risk/reward ratio, what happens if a trader wins only 40% of trades?",
        options=[
            "They definitely lose",
            "They break even",
            "They profit long-term — their expectancy is positive",
            "Their account is closed",
        ],
        explanation=(
            "The math: over 100 trades, 40 wins × 2R − 60 losses × 1R = 80R − 60R = +20R. Even "
            "with a win rate below 50%, gains being larger than losses makes the system profitable. "
            "That's why professionals focus on R:R more than win rate."
        ),
    ),
    dict(
        question_text="Why is an ATR-based stop-loss more sensible than a fixed-percentage stop?",
        options=[
            "It requires less math",
            "It adapts to the stock's own volatility: wide on a volatile stock, tight on a calm one",
            "It's always closer",
            "It lowers commissions",
        ],
        explanation=(
            "Put a 2% stop on a stock that swings 5% a day and normal noise stops you out; put a "
            "10% stop on a stock that swings 0.5% a day and you take needless risk. ATR measures "
            "the stock's real daily move, so it sizes the stop distance to the stock."
        ),
    ),
    dict(
        question_text="No matter how strong an individual stock looks, if the broad market (SPY/QQQ) is in a downtrend, what should you expect?",
        options=[
            "No effect at all",
            "Most breakouts fail — the broad market suppresses the individual stock",
            "The stock rises faster",
            "Volume increases automatically",
        ],
        explanation=(
            "The vast majority of stocks move with the broad market. In a bear market even the "
            "strongest-looking breakouts are mostly met with selling. That's why experienced "
            "traders check the market's direction (the SPY/QQQ trend) first, then pick stocks — "
            "the foundation of the O'Neil and Minervini system."
        ),
    ),
    dict(
        question_text="In Qullamaggie's Breakout setup, when is the entry made?",
        options=[
            "Inside the consolidation, predicting the breakout in advance",
            "After the consolidation high breaks on high volume (opening range high)",
            "When price drops below the 200-day average",
            "When RSI falls below 30",
        ],
        explanation=(
            "Qullamaggie never predicts: he doesn't sit inside 'looks like it'll break.' He enters "
            "after the breakout happens, once the opening range high (first 1/5/60-min candle) is "
            "taken out. The stop is the day's low, and risk never exceeds 0.25–1% of the account."
        ),
    ),
    dict(
        question_text="In the Episodic Pivot (EP) setup, why is it required that the stock has NOT rallied in the past 3–6 months?",
        options=[
            "Because a cheap stock pays more",
            "The news must be a surprise — in an already-rallied stock the news is usually priced in",
            "Because commissions are lower",
            "To avoid the PDT rule",
        ],
        explanation=(
            "The EP's power is in the surprise: unexpected earnings/news starts a fresh story that "
            "carries the stock to new owners for months. In a stock that's been rising for months "
            "the same news becomes 'expected news' and often triggers a 'sell the news' reaction."
        ),
    ),
    dict(
        question_text="Until when does Qullamaggie hold the remainder of a winning position?",
        options=[
            "He sells everything at 5% profit",
            "Until price breaks below the 10- or 20-day moving average",
            "For exactly one year",
            "Until RSI reaches 70",
        ],
        explanation=(
            "This is where the system's asymmetry lives: in the first 3–5 days 1/3–1/2 of the "
            "position is sold (locking in cost), and the rest is carried until the 10/20-day "
            "average trend breaks. In a bull market this captures 10–20R moves — small fixed "
            "risk, open-ended gain."
        ),
    ),
]

assert len(QUESTIONS) == len(QUESTIONS_EN), (
    f"TR/EN soru sayısı uyuşmuyor: {len(QUESTIONS)} != {len(QUESTIONS_EN)}"
)


def seed_quiz(db: Session) -> None:
    """Eksik soruları ekler ve İngilizce alanları (varsa boşları) doldurur."""
    existing = {q.question_text: q for q in db.query(QuizQuestion).all()}
    changed = False
    for q, en in zip(QUESTIONS, QUESTIONS_EN):
        if q["question_text"] not in existing:
            db.add(
                QuizQuestion(
                    topic=q["topic"],
                    question_text=q["question_text"],
                    options_json=json.dumps(q["options"], ensure_ascii=False),
                    correct_index=q["correct_index"],
                    explanation=q["explanation"],
                    related_glossary_slug=q.get("related_glossary_slug"),
                    question_text_en=en["question_text"],
                    options_json_en=json.dumps(en["options"], ensure_ascii=False),
                    explanation_en=en["explanation"],
                )
            )
            changed = True
        else:
            row = existing[q["question_text"]]
            if row.question_text_en is None:
                row.question_text_en = en["question_text"]
                row.options_json_en = json.dumps(en["options"], ensure_ascii=False)
                row.explanation_en = en["explanation"]
                changed = True
    if changed:
        db.commit()
