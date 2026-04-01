import json
from pathlib import Path


def main() -> None:
    nb_path = Path(__file__).resolve().parents[1] / "student_performance_final.ipynb"
    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    cell_idx = 11
    old_src = "".join(nb["cells"][cell_idx].get("source", []))
    needle = "# 2.3 Univariate: Her sütun için Plotly + export"
    if needle not in old_src:
        raise RuntimeError("Target cell content not found; aborting.")

    new_src = """# 2.3 Univariate: Her sütun için Plotly + export + kompakt görünüm
# Amaç: her sütun için görsel üret + figures/ altına export et + notebook içinde 2-3 grafiği yan yana göstermek.
#
# Not: VS Code/Jupyter bazı durumlarda HTML içindeki script'leri çalıştırmayabildiği için,
# grafikleri doğrudan Plotly renderer ile gösterip yan yana yerleşimi ipywidgets ile yapıyoruz.

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
    \"\"\"Render (figure + text) cards in a responsive grid.\"\"\"\n+    if not cards:\n+        return\n+    try:\n+        import ipywidgets as widgets\n+        from IPython.display import display\n+\n+        grid = widgets.GridBox(\n+            children=cards,\n+            layout=widgets.Layout(\n+                grid_template_columns=f\"repeat({ncols}, minmax(0, 1fr))\",\n+                grid_gap=\"14px\",\n+                align_items=\"stretch\",\n+            ),\n+        )\n+        display(grid)\n+    except Exception:\n+        # Fallback: show sequentially\n+        for c in cards:\n+            display(c)\n+\n+\n+def make_card(fig, title: str, bullets: list[str]):\n+    \"\"\"Create a single card: plot on top, bullets below.\"\"\"\n+    import ipywidgets as widgets\n+    import plotly.graph_objects as go\n+\n+    fw = go.FigureWidget(fig)\n+    fw.layout.height = 320\n+    fw.layout.margin = dict(l=10, r=10, t=48, b=40)\n+\n+    # Bullet list HTML (no overlap, wraps naturally)\n+    li = \"\".join(f\"<li style='margin:6px 0;'>{b}</li>\" for b in bullets)\n+    html = widgets.HTML(\n+        value=f\"\"\"\n+        <div style='font-family: Inter, Arial, sans-serif; color:#0f172a; font-size: 14px; line-height:1.45;'>\n+          <div style='font-weight:800; margin: 6px 0 6px 0;'>Bu grafik bize ne anlatıyor? — {title}</div>\n+          <ul style='margin: 0 0 6px 18px; padding:0;'>\n+            {li}\n+          </ul>\n+        </div>\n+        \"\"\",\n+    )\n+\n+    box = widgets.VBox(\n+        [fw, html],\n+        layout=widgets.Layout(\n+            border=\"1px solid rgba(15,23,42,0.12)\",\n+            padding=\"10px\",\n+            border_radius=\"14px\",\n+            background_color=\"#ffffff\",\n+        ),\n+    )\n+    return box


improved_hist_layout = dict(
    bargap=0.08,
    plot_bgcolor="#f8f7fa",
    paper_bgcolor="#f8f7fa",
    xaxis=dict(showgrid=True, gridcolor="#e6e6ed", title_font_size=16, tickfont_size=12, tickformat=","),
    yaxis=dict(showgrid=True, gridcolor="#f2f1f8", title_font_size=16, tickfont_size=12),
    font=dict(family="Inter, Arial, sans-serif", size=15, color="#232446"),
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
        "Alt uçta ~75, üst uçta 100’e yakın az sayıda değer var; bunlar ana kitleden ayrışan istisnalar gibi duruyor.",
        "Genel tablo, devamın veri içinde yüksek ve tutarlı bir davranış olduğunu düşündürüyor.",
    ],
    "sleep_hours": [
        "Uyku saatlerinin büyük kısmı gerçekçi aralıkta (yaklaşık 6–12 saat) yoğunlaşıyor; çoğunluğun uyku düzeni bu bantta.",
        "Buna rağmen çok aşırı yüksek (100+ gibi) az sayıda değer net biçimde ayrışıyor; bu durum çoğu zaman kayıt/format hatası ihtimalini güçlendirir.",
        "Bu uç değerler ölçeği “çektiği” için ana kitlenin dağılımı daha sıkışık görünür; yani grafiğin görünümü uçlardan belirgin biçimde etkileniyor.",
        "Genel çıkarım: Uyku değişkeninde çoğunluk normal, fakat veri içinde bariz anomaliler de var.",
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
        "Grafikte negatif uzaklık (≈ -5 km) gibi gerçek hayatta anlamsız bir değer görülüyor; bu, değişkende az sayıda da olsa kayıt/işaret hatası olabileceğini gösteriyor.",
        "Genel resim, uzaklık değişkeninin öğrenciler arasında çeşitlilik barındırdığını; ancak küçük sayıdaki tutarsız değerin veride “temizlik gerektiren” bir sinyal verdiğini anlatıyor.",
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
        color_discrete_sequence=["#6c5ce7"],
        histnorm=None,
    )
    fig.update_traces(marker_line_width=1.6, marker_line_color="#232446", selector=dict(type="histogram"))
    fig.update_layout(
        title={
            "text": f"2.3 Univariate (Numeric) — {col}",
            "font": dict(size=20, color="#22213b"),
            "x": 0.02,
            "xanchor": "left",
            "y": 0.95,
        },
        xaxis_title=col,
        yaxis_title="Gözlem Sayısı",
        **improved_hist_layout,
    )
    fig.update_xaxes(showline=True, linewidth=1.5, linecolor="#232446", tickformat=",.3g")
    fig.update_yaxes(showline=True, linewidth=1.5, linecolor="#232446")

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
        color_discrete_sequence=["#00b894"],
        opacity=0.92,
    )
    fig.update_traces(textposition="outside", marker_line_width=1.3, marker_line_color="#232446")
    fig.update_layout(
        title={
            "text": f"2.3 Univariate (Categorical) — {col}",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.92,
            "yanchor": "top",
            "font": {"size": 22, "color": "#232446", "family": "Nunito Sans,sans-serif"},
        },
        xaxis_title=col,
        yaxis_title="Gözlem Sayısı",
        plot_bgcolor="#fff",
        bargap=0.18,
        font={"size": 16, "family": "Nunito Sans,sans-serif"},
        margin=dict(l=30, r=15, b=60, t=60),
    )

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
"""

    # Use the external template as source-of-truth (easier styling edits)
    template_path = Path(__file__).resolve().parent / "univariate_cell_template.py"
    new_src = template_path.read_text(encoding="utf-8")

    nb["cells"][cell_idx]["source"] = [line + "\n" for line in new_src.split("\n")]
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    # Validate and sanity-check
    nb2 = json.loads(nb_path.read_text(encoding="utf-8"))
    chk = "".join(nb2["cells"][cell_idx].get("source", []))
    if "make_card" not in chk or "NUM_TEXT" not in chk or "CAT_TEXT" not in chk:
        raise RuntimeError("Update failed sanity-check.")


if __name__ == "__main__":
    main()

