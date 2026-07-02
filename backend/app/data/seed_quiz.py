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
