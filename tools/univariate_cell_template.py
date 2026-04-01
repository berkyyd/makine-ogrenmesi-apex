# 2.3 Univariate: Her sütun için Plotly + export + kompakt görünüm
# Amaç: her sütun için görsel üret + figures/ altına export et + notebook içinde 2-3 grafiği yan yana göstermek.
#
# Not: VS Code/Jupyter bazı durumlarda HTML içindeki script'leri çalıştırmayabildiği için,
# grafikleri doğrudan Plotly renderer ile gösterip yan yana yerleşimi ipywidgets ile yapıyoruz.

from pathlib import Path

import plotly.express as px

THEME = {
    "bg": "#f8fafc",          # slate-50
    "card_bg": "#ffffff",
    "border": "#e2e8f0",      # slate-200
    "grid": "#e5e7eb",        # gray-200
    "grid_y": "#f1f5f9",      # slate-100
    "text": "#0f172a",        # slate-900
    "muted": "#475569",       # slate-600
    "accent": "#6d28d9",      # violet-700
    "accent_soft": "#a78bfa", # violet-300
    "success": "#10b981",     # emerald-500
}

cat_cols = df_raw.select_dtypes(include=["object"]).columns.tolist()
num_cols = [c for c in df_raw.columns if c not in cat_cols]

fig_counter = 4  # 01-04 target analizi (görsel numarası)

FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_COLS = 3


def next_fig(title_slug: str) -> str:
    global fig_counter
    fig_counter += 1
    safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in title_slug)
    return f"{fig_counter:02d}_{safe}.html"


def export_fig(fig, filename: str) -> None:
    fig.write_html(str(FIG_DIR / filename), include_plotlyjs="cdn", full_html=True)


def show_cards(cards: list, ncols: int = N_COLS) -> None:
    """Render (figure + text) cards in a responsive grid."""
    if not cards:
        return
    try:
        import ipywidgets as widgets
        from IPython.display import display

        grid = widgets.GridBox(
            children=cards,
            layout=widgets.Layout(
                grid_template_columns=f"repeat({ncols}, minmax(340px, 1fr))",
                grid_gap="14px",
                align_items="stretch",
                width="100%",
            ),
        )
        display(grid)
    except Exception:
        for c in cards:
            display(c)


def make_card(fig, title: str, bullets: list[str]):
    """Create a single card: plot on top, bullets below."""
    import ipywidgets as widgets
    import plotly.graph_objects as go

    fw = go.FigureWidget(fig)
    fw.layout.height = 340
    fw.layout.margin = dict(l=14, r=14, t=56, b=44)

    li = "".join(f"<li style='margin:6px 0; color:{THEME['text']};'>{b}</li>" for b in bullets)
    html = widgets.HTML(
        value=f"""
        <div style="font-family: Inter, Arial, sans-serif; font-size: 14px; line-height: 1.55;">
          <div style="
              font-weight: 900;
              color: {THEME['text']};
              margin: 6px 0 8px 0;
              letter-spacing: .1px;
          ">
            Bu grafik bize ne anlatıyor? — {title}
          </div>
          <div style="
              background: {THEME['bg']};
              border: 1px solid {THEME['border']};
              border-radius: 12px;
              padding: 10px 12px;
              color: {THEME['muted']};
          ">
            <ul style="margin: 0 0 0 18px; padding: 0;">
              {li}
            </ul>
          </div>
        </div>
        """,
    )

    box = widgets.VBox(
        [fw, html],
        layout=widgets.Layout(
            border=f"1px solid {THEME['border']}",
            padding="12px",
            border_radius="16px",
            background_color=THEME["card_bg"],
            width="100%",
        ),
    )
    return box


improved_hist_layout = dict(
    bargap=0.08,
    plot_bgcolor=THEME["bg"],
    paper_bgcolor=THEME["bg"],
    xaxis=dict(showgrid=True, gridcolor=THEME["grid"], title_font_size=14, tickfont_size=12, tickformat=",", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor=THEME["grid_y"], title_font_size=14, tickfont_size=12, zeroline=False),
    font=dict(family="Inter, Arial, sans-serif", size=13, color=THEME["text"]),
    margin=dict(t=64, l=54, r=28, b=64),
)


NUM_TEXT = {
    "weekly_study_hours": [
        "Haftalık çalışma süresi değerleri belirgin biçimde 15–25 saat/hafta bandında toplanıyor; en tipik seviye ~20 saat civarında.",
        "Dağılım tek tepeli ve genel olarak dengeli; uçlara gidildikçe gözlem sayısı kademeli azalıyor.",
        "Çok düşük (<~5) ve çok yüksek (>~35–38) birkaç değer ana kitleden ayrışıyor; bunlar istisna bir grubu işaret ediyor olabilir.",
        "Genel resim, öğrencilerin çoğunda çalışma süresinin benzer bir rutin etrafında kümelendiğini gösteriyor.",
    ],
    "attendance_rate": [
        "Devam oranı değerleri büyük ölçüde 80–95 bandında toplanıyor; en yoğun bölge 85–92 civarında.",
        "Dağılım genel olarak dengeli; çok düşük devam oranları az, çoğunluk orta-yüksek devam seviyesinde.",
        "0–100 dışına taşan değerler (varsa) fiziksel/mantıksal olarak tutarsız kabul edilmelidir; bu durum Adım 3’te “hata→NaN→akıllı imputation” akışında ele alınır.",
        "Genel tablo, devamın veri içinde yüksek ve tutarlı bir davranış olduğunu düşündürüyor; tanı aşamasında uç noktalar ayrıca sayılmalıdır.",
    ],
    "sleep_hours": [
        "Uyku saatlerinin büyük kısmı gerçekçi aralıkta (yaklaşık 6–12 saat) yoğunlaşıyor; çoğunluğun uyku düzeni bu bantta.",
        "2’nin altı veya 24’ün üstü gibi değerler fiziksel olarak imkansız kabul edilir; bu tür değerler Adım 3’te önce NaN’a çevrilip sonra akıllı imputation ile tamamlanır.",
        "Bu uç değerler ölçeği “çektiği” için ana kitlenin dağılımı daha sıkışık görünür; bu yüzden tanı aşamasında imkansız değer sayımı ayrıca raporlanmalıdır.",
        "Genel çıkarım: Uyku değişkeninde çoğunluk normal; küçük bir anomali kümesi veri temizleme ihtiyacını netleştiriyor.",
    ],
    "internet_usage_time": [
        "İnternet kullanım süresi değerleri ağırlıkla 6–9 saat/gün bandında toplanıyor; en yoğun bölge 7–9 civarında görünüyor.",
        "Grafikte 9.0 etrafında belirgin bir yığılma var; bu, öğrencilerin önemli bir kısmının çok yüksek kullanımda olduğunu gösterdiği gibi ölçümde üst sınıra takılma (tavan) ihtimalini de akla getiriyor.",
        "Daha düşük kullanım seviyelerinde (3–5 saat) gözlem sayısı belirgin biçimde azalıyor; “az internet kullanan” grup daha küçük kalmış.",
        "Genel resim, bu değişkende değerlerin yüksek tarafa doğru yığıldığını ve üst sınıra yakın kullanımın veri içinde baskın olduğunu gösteriyor.",
    ],
    "previous_scores": [
        "Önceki skorlar geniş bir aralığa yayılıyor ama değerlerin büyük kısmı orta bantta (yaklaşık 45–75) toplanmış; tipik geçmiş performans bu bölgede.",
        "Dağılım genel olarak dengeli; çok düşük ve çok yüksek skorlar var ancak ana kitleden uzaklaştıkça gözlem sayısı kademeli azalıyor.",
        "Grafikte belirgin bir “tek tarafa yığılma” ya da keskin bir kopuş görünmüyor; bu da değişkenin genel yapısının istikrarlı olduğunu düşündürüyor.",
        "Genel tablo, öğrencilerin geçmiş başarı seviyesinin çeşitli ama ağırlıkla orta seviyede kümelendiğini gösteriyor.",
    ],
    "distance_to_school": [
        "Okula uzaklık değerleri genel olarak geniş bir aralığa yayılmış; gözlemler büyük ölçüde 0–40 km bandını dolduruyor ve belirgin bir “tek noktada yığılma” çok güçlü görünmüyor.",
        "Medyanın ~20 km civarında olması, tipik öğrencinin okula orta mesafeden geldiğini düşündürüyor; kutu grafiği de ana kitlenin bu orta bandın etrafında toplandığını ima ediyor.",
        "Negatif uzaklık gibi değerler fiziksel olarak anlamsızdır; bu durum veri hatası kabul edilip Adım 3’te NaN havuzuna alınarak akıllı imputation ile düzeltilir.",
        "Genel resim, uzaklık değişkeninin çeşitlilik barındırdığını; küçük sayıdaki tutarsız değerin ise temizleme ihtiyacını gösterdiğini anlatıyor.",
    ],
    "stress_level": [
        "Stres düzeyi değerleri çoğunlukla 2–4 bandında toplanıyor; en yoğun bölge ~3 civarı ve tipik öğrencinin stres seviyesi bu orta aralıkta görünüyor.",
        "Dağılımın sağ tarafında uzayan bir kuyruk var; yani stres arttıkça gözlem sayısı azalıyor ama yüksek stres yaşayan küçük bir grup net biçimde mevcut.",
        "Üst uçta 7–8 civarında az sayıda değer dikkat çekiyor; bunlar ana kitleden ayrışan, daha “uç” stres seviyelerini temsil ediyor.",
        "Genel resim, öğrencilerin büyük kısmının orta düzey stres yaşadığını; buna karşılık veri içinde yüksek stresli küçük bir segment bulunduğunu gösteriyor.",
    ],
    "practice_exams_passed": [
        "Geçilen deneme sayısı değerleri belirgin biçimde 7–12 bandında toplanıyor; en yoğun bölge ~9–10 civarı ve tipik öğrencinin bu aralıkta yer aldığı görülüyor.",
        "Dağılım tek tepeli ve genel olarak dengeli; hem düşük hem yüksek deneme sayılarında gözlem sayısı kademeli biçimde azalıyor.",
        "Uçlarda 0–2 gibi çok düşük ve 16+ gibi çok yüksek birkaç değer dikkat çekiyor; bunlar ana kitleden ayrışan küçük bir grubu işaret ediyor.",
        "Genel resim, öğrencilerin çoğunun deneme sınavı deneyiminin orta seviyede kümelendiğini ve çok az öğrencinin uç seviyelerde kaldığını gösteriyor.",
    ],
    "extracurricular_activities": [
        "Değerler 0–20 aralığına yayılmış ve çubuklar birbirine oldukça yakın; yani etkinlik seviyesi öğrenciler arasında geniş ve dengeli biçimde dağılmış görünüyor.",
        "Belirgin bir “tek tepe” yok; bu da veride tek bir tipik seviyeden çok, farklı yoğunluklarda çeşitli profiller bulunduğunu düşündürüyor.",
        "Kutu grafiği orta kitlenin geniş olduğunu ima ediyor; yani “ortalama” bir değer var ama öğrencilerin önemli kısmı bu ortalamanın hem altında hem üstünde dağılmış.",
        "Genel resim, okul dışı etkinlik katılımının veri içinde ayırt edici bir çeşitlilik taşıdığını ve tek bir seviyeye sıkışmadığını gösteriyor.",
    ],
}


CAT_TEXT = {
    "parent_education_level": [
        "Kategoriler arasında gözlem sayıları birbirine çok yakın; her bir seviyede yaklaşık ~2000 öğrenci var ve belirgin bir dengesizlik görünmüyor.",
        "“Yok”, “Üniversite”, “İlkokul”, “Lise”, “Ortaokul” grupları benzer büyüklükte olduğu için, karşılaştırmalar tek bir grubun baskınlığıyla gölgelenmiyor.",
        "En yüksek grup “Yok”, en düşük grup “Ortaokul” gibi dursa da fark küçük; dağılım genel olarak homojen.",
        "Genel resim, veli eğitim seviyesinin veri içinde dengeli temsil edildiğini ve farklı seviyeleri kıyaslamak için elverişli bir tablo sunduğunu gösteriyor.",
    ]
}


# -----------------------------
# Numeric sütunlar
# -----------------------------
cards = []

for col in num_cols:
    if col == target_col:
        continue

    fig = px.histogram(
        df_raw,
        x=col,
        nbins=40,
        marginal="box",
        opacity=0.85,
        color_discrete_sequence=[THEME["accent_soft"]],
        histnorm=None,
    )
    fig.update_traces(
        marker_line_width=1.2,
        marker_line_color=THEME["border"],
        selector=dict(type="histogram"),
    )
    fig.update_layout(
        title={
            "text": f"2.3 Univariate (Numeric) — {col}",
            "font": dict(size=18, color=THEME["text"]),
            "x": 0.02,
            "xanchor": "left",
            "y": 0.95,
        },
        xaxis_title=col,
        yaxis_title="Gözlem Sayısı",
        **improved_hist_layout,
    )
    fig.update_layout(template="simple_white", height=320)
    fig.update_xaxes(showline=True, linewidth=1.0, linecolor=THEME["border"], tickformat=",.3g")
    fig.update_yaxes(showline=True, linewidth=1.0, linecolor=THEME["border"])

    fname = next_fig(f"univariate_num_{col}")
    export_fig(fig, fname)

    key = col.lower()
    if key == "student_id":
        bullets = [
            "Student_ID sayısal gibi görünse de yalnızca tanımlama amaçlıdır, modelleme için bir anlam taşımaz.",
            "Histogram ve boxplot burada tipik varyasyon/veri desenini göstermez; değişkeni modelden çıkarmak uygun olur.",
            "Sadece referans olarak tutulmalı, öngörüde kullanılması önerilmez.",
        ]
        cards.append(make_card(fig, col, bullets))
        continue

    bullets = NUM_TEXT.get(
        key,
        [
            "Değerler belirli bir aralıkta yoğunlaşıyor; grafikte ana kitlenin nerede toplandığı net biçimde görülüyor.",
            "Uçlara gidildikçe gözlem sayısı azalıyor; az sayıda istisna değer ana kitleden ayrışabiliyor.",
            "Dağılımın şekli (dengeli/çarpık) değişkenin veri içindeki genel örüntüsünü anlatıyor.",
            "Genel resim, bu değişkenin öğrenciler arasında ne kadar farklılaştığını ve tipik seviyenin nerede olduğunu gösteriyor.",
        ],
    )
    cards.append(make_card(fig, col, bullets))

    if len(cards) >= N_COLS:
        show_cards(cards, ncols=N_COLS)
        cards = []

if cards:
    show_cards(cards, ncols=min(N_COLS, len(cards)))


# -----------------------------
# Categorical sütunlar
# -----------------------------
cards = []

for col in cat_cols:
    vc = df_raw[col].fillna("(Eksik)").value_counts(dropna=False).reset_index()
    vc.columns = [col, "count"]

    fig = px.bar(
        vc,
        x=col,
        y="count",
        text="count",
        color_discrete_sequence=[THEME["success"]],
        opacity=0.92,
    )
    fig.update_traces(textposition="outside", marker_line_width=1.0, marker_line_color=THEME["border"])
    fig.update_layout(
        title={
            "text": f"2.3 Univariate (Categorical) — {col}",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.92,
            "yanchor": "top",
            "font": {"size": 18, "color": THEME["text"], "family": "Inter, Arial, sans-serif"},
        },
        xaxis_title=col,
        yaxis_title="Gözlem Sayısı",
        plot_bgcolor=THEME["bg"],
        bargap=0.18,
        font={"size": 13, "family": "Inter, Arial, sans-serif", "color": THEME["text"]},
        margin=dict(l=30, r=15, b=60, t=60),
    )
    fig.update_layout(template="simple_white", height=320, paper_bgcolor=THEME["bg"])

    fname = next_fig(f"univariate_cat_{col}")
    export_fig(fig, fname)

    bullets = CAT_TEXT.get(
        col.lower(),
        [
            "Grafik, kategorilerin veri içindeki gözlem sayılarını karşılaştırmalı olarak gösteriyor.",
            "Barların birbirine yakın/uzak olması, dağılımın dengeli mi yoksa dengesiz mi olduğunu anlatır.",
            "Bu görünüm, kategoriler arası kıyas yaparken hangi grupların daha baskın olduğunu anlamayı sağlar.",
        ],
    )
    cards.append(make_card(fig, col, bullets))

    if len(cards) >= N_COLS:
        show_cards(cards, ncols=N_COLS)
        cards = []

if cards:
    show_cards(cards, ncols=min(N_COLS, len(cards)))

print("✅ Univariate figürleri üretildi (figures/).")

