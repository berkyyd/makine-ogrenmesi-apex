# 2.4 Korelasyon + target ilişkileri (Plotly)
# İstenen düzen: 2.4.1 ve 2.4.2 aynı satırda (2'li grid) kart mantığıyla.

from IPython.display import display
import ipywidgets as widgets
import plotly.graph_objects as go
from pathlib import Path

THEME = {
    "bg": "#f8fafc",
    "card_bg": "#ffffff",
    "border": "#e2e8f0",
    "grid": "#e5e7eb",
    "grid_y": "#f1f5f9",
    "text": "#0f172a",
    "muted": "#475569",
    "accent": "#b91c1c",       # red-700
    "accent_soft": "#fecaca",  # red-200
    "blue": "#2563eb",         # blue-600
    "violet": "#7c3aed",       # violet-600
}

FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def export_only(fig, filename: str) -> None:
    fig.write_html(str(FIG_DIR / filename), include_plotlyjs="cdn", full_html=True)


def show_cards(cards: list, ncols: int = 2) -> None:
    if not cards:
        return
    grid = widgets.GridBox(
        children=cards,
        layout=widgets.Layout(
            grid_template_columns=f"repeat({ncols}, minmax(420px, 1fr))",
            grid_gap="14px",
            align_items="stretch",
            width="100%",
        ),
    )
    display(grid)


def make_card(fig, title: str, bullets: list[str]):
    fw = go.FigureWidget(fig)
    fw.layout.height = 420
    fw.layout.margin = dict(l=14, r=14, t=56, b=44)

    li = "".join(f"<li style='margin:6px 0; color:{THEME['text']};'>{b}</li>" for b in bullets)
    html = widgets.HTML(
        value=f"""
        <div style="font-family: Inter, Arial, sans-serif; font-size: 14px; line-height: 1.55;">
          <div style="font-weight: 900; color: {THEME['text']}; margin: 6px 0 8px 0;">
            Bu grafik bize ne anlatıyor? — {title}
          </div>
          <div style="background: {THEME['bg']}; border: 1px solid {THEME['border']}; border-radius: 12px; padding: 10px 12px; color: {THEME['muted']};">
            <ul style="margin: 0 0 0 18px; padding: 0;">{li}</ul>
          </div>
        </div>
        """,
    )

    return widgets.VBox(
        [fw, html],
        layout=widgets.Layout(
            border=f"1px solid {THEME['border']}",
            padding="12px",
            border_radius="16px",
            background_color=THEME["card_bg"],
            width="100%",
        ),
    )


num_df = df_raw.select_dtypes(include=[np.number]).copy()
corr = num_df.corr(numeric_only=True)

# 2.4.1 Heatmap (tek renk kırmızı + değer yazımı)
fig_corr = px.imshow(
    corr.round(2),
    text_auto=".2f",
    color_continuous_scale="Reds",
    zmin=-1,
    zmax=1,
)
fig_corr.update_layout(
    title={"text": "2.4.1 Korelasyon Matrisi (Numeric)", "x": 0.02, "xanchor": "left"},
    paper_bgcolor=THEME["bg"],
    plot_bgcolor=THEME["bg"],
    font=dict(family="Inter, Arial, sans-serif", size=13, color=THEME["text"]),
)
fig_corr.update_xaxes(showgrid=False)
fig_corr.update_yaxes(showgrid=False)

export_only(fig_corr, next_fig("bivariate_corr_heatmap"))

# En yüksek mutlak korelasyonlar
pairs = (
    corr.where(~np.eye(corr.shape[0], dtype=bool))
    .stack()
    .reset_index()
    .rename(columns={"level_0": "a", "level_1": "b", 0: "corr"})
)
pairs["key"] = pairs.apply(lambda r: "|".join(sorted([r["a"], r["b"]])), axis=1)
pairs = pairs.drop_duplicates("key").drop(columns=["key"]).copy()
pairs["abs_corr"] = pairs["corr"].abs()
top_pairs = pairs.sort_values("abs_corr", ascending=False).head(5)

examples = ", ".join([f"{r.a}↔{r.b} ({r.corr:+.2f})" for r in top_pairs.itertuples(index=False)]) if len(top_pairs) else None

bullets_corr = [
    "Isı haritasında koyu kırmızıya giden hücreler, iki değişkenin birlikte aynı yönde güçlü hareket ettiğini gösteriyor; açık tonlar ise ilişkinin zayıf kaldığını anlatıyor.",
    "Bu grafikte en belirgin pozitif ilişkilerden bazıları: Weekly_Study_Hours↔Practice_Exams_Passed (+0.85), Weekly_Study_Hours↔Exam_Score (+0.80) ve Previous_Scores↔Exam_Score (+0.78). Yani çalışma süresi ve geçmiş başarı arttıkça sınav skorunun da artma eğilimi var.",
    "Negatif tarafta Attendance_Rate↔Distance_to_School (-0.79) öne çıkıyor; okul uzaklaştıkça devam oranının düşme eğilimi görülüyor.",
    "Genel resim: hedefe (Exam_Score) en yakın sinyaller çalışma süresi, deneme sayısı ve geçmiş skorlar gibi duruyor; ayrıca bazı değişkenler birbirini kısmen tekrar edebileceği için birlikte değerlendirilirken bu tablo yol gösterici oluyor.",
]

# 2.4.2 Target korelasyon sırası
card_right = None
if target_col in corr.columns:
    corr_with_target = corr[target_col].drop(target_col).sort_values(ascending=False)
    corr_df = corr_with_target.reset_index()
    corr_df.columns = ["feature", "corr"]

    fig_bar = px.bar(
        corr_df,
        x="corr",
        y="feature",
        orientation="h",
        color="corr",
        color_continuous_scale="Reds",
        range_color=[-1, 1],
    )
    fig_bar.update_layout(
        title={"text": "2.4.2 Exam_Score ile Korelasyon Sıralaması", "x": 0.02, "xanchor": "left"},
        paper_bgcolor=THEME["bg"],
        plot_bgcolor=THEME["bg"],
        font=dict(family="Inter, Arial, sans-serif", size=13, color=THEME["text"]),
        coloraxis_showscale=False,
    )
    fig_bar.update_xaxes(showgrid=True, gridcolor=THEME["grid"])
    fig_bar.update_yaxes(showgrid=False)

    export_only(fig_bar, next_fig("bivariate_target_corr_rank"))

    top_pos = corr_df.sort_values("corr", ascending=False).head(3)
    top_neg = corr_df.sort_values("corr", ascending=True).head(3)

    bullets_rank = [
        "Bu grafik, Exam_Score ile değişkenler arasındaki doğrusal ilişkiyi güçlüden zayıfa doğru gösteriyor: sağa uzayan çubuklar pozitif, sola uzayanlar negatif ilişkiyi anlatır.",
        f"En güçlü pozitif ilişkiler: {', '.join([f'{r.feature} ({r.corr:+.2f})' for r in top_pos.itertuples(index=False)])}. Yani bu değişkenler yükseldikçe skorun da yükselme eğilimi belirgin.",
        f"Negatif tarafta en belirgin değişkenler: {', '.join([f'{r.feature} ({r.corr:+.2f})' for r in top_neg.itertuples(index=False)])}. Bu tarafta değer arttıkça skorun düşme eğilimi öne çıkıyor.",
        "Genel resim: hedefi açıklamada en çok iş yapanlar çalışma/deneme/geçmiş başarı gibi akademik göstergeler; internet kullanımı ise ters yönde daha belirgin bir risk sinyali gibi duruyor.",
    ]
    card_right = make_card(fig_bar, "Exam_Score ile korelasyon sıralaması", bullets_rank)

card_left = make_card(fig_corr, "Korelasyon matrisi", bullets_corr)

cards = [card_left]
if card_right is not None:
    cards.append(card_right)
show_cards(cards, ncols=2)

# Örnek scatter: Weekly_Study_Hours vs Exam_Score
if all(c in df_raw.columns for c in ["Weekly_Study_Hours", target_col]):
    fig_sc = px.scatter(
        df_raw,
        x="Weekly_Study_Hours",
        y=target_col,
        opacity=0.35,
        color_discrete_sequence=[THEME["blue"]],
        trendline="ols",
    )
    fig_sc.update_layout(
        title={"text": "2.4.3 Weekly_Study_Hours vs Exam_Score", "x": 0.02, "xanchor": "left"},
        paper_bgcolor=THEME["bg"],
        plot_bgcolor=THEME["bg"],
        font=dict(family="Inter, Arial, sans-serif", size=13, color=THEME["text"]),
    )
    fig_sc.update_xaxes(showgrid=True, gridcolor=THEME["grid"])
    fig_sc.update_yaxes(showgrid=True, gridcolor=THEME["grid_y"])

    export_only(fig_sc, next_fig("bivariate_study_vs_score"))

    corr_ws = float(df_raw[["Weekly_Study_Hours", target_col]].corr(numeric_only=True).iloc[0, 1])
    bullets_sc = [
        "Grafikteki nokta bulutu ve yukarı eğimli trend çizgisi, haftalık çalışma süresi arttıkça Exam_Score’un genel olarak yükseldiğini gösteriyor.",
        f"Bu desen sayısal olarak da destekleniyor: Pearson korelasyon (r={corr_ws:+.2f}).",
        "Ancak noktaların dikeyde geniş saçılması, aynı çalışma süresinde çok farklı skorların görülebildiğini anlatır; yani çalışma saati tek başına her öğrenciyi açıklamıyor.",
        "Genel çıkarım: çalışma süresi güçlü bir pozitif sinyal, fakat skor üzerinde uyku, önceki başarı, stres ve deneme sayısı gibi başka etkenlerin de etkisi belirgin.",
    ]
    card_sc = make_card(fig_sc, "Weekly_Study_Hours vs Exam_Score", bullets_sc)
else:
    card_sc = None

# Kategorik grup: Parent_Education_Level
if all(c in df_raw.columns for c in ["Parent_Education_Level", target_col]):
    fig_box = px.box(
        df_raw,
        x="Parent_Education_Level",
        y=target_col,
        points="all",
        color_discrete_sequence=[THEME["violet"]],
    )
    fig_box.update_layout(
        title={"text": "2.4.4 Parent_Education_Level gruplarında Exam_Score", "x": 0.02, "xanchor": "left"},
        paper_bgcolor=THEME["bg"],
        plot_bgcolor=THEME["bg"],
        font=dict(family="Inter, Arial, sans-serif", size=13, color=THEME["text"]),
    )
    fig_box.update_xaxes(showgrid=False)
    fig_box.update_yaxes(showgrid=True, gridcolor=THEME["grid_y"])

    export_only(fig_box, next_fig("bivariate_parent_edu_vs_score"))

    grp = df_raw.groupby("Parent_Education_Level")[target_col].mean().sort_values(ascending=False)
    bullets_box = [
        "Her kutu, ilgili grubun skorlarının orta kısmını gösterir: kutunun ortasındaki çizgi medyanı, kutunun boyu tipik dağılım aralığını anlatır; dıştaki noktalar da tekil gözlemlerdir.",
        "Kutuların yukarıda olması, o grupta tipik skorların daha yüksek seyrettiğini gösterir. Bu grafikte genel sıralama Üniversite/Lise tarafının daha yukarıda, Yok tarafının daha aşağıda kaldığını ima ediyor.",
        f"Ortalama skorlar (yüksekten düşüğe): {', '.join([f'{idx}: {val:.2f}' for idx,val in grp.items()])}.",
        "Gruplar arasında fark var; ancak dağılımlar kısmen üst üste bindiği için, eğitim seviyesi tek başına ‘kesin ayırıcı’ değil—daha çok skoru etkileyen faktörlerden biri gibi okunmalı.",
    ]
    card_box = make_card(fig_box, "Parent_Education_Level → Exam_Score", bullets_box)
else:
    card_box = None

# 2.4.3 ve 2.4.4 aynı satırda kart olarak göster
cards_243_244 = []
if card_sc is not None:
    cards_243_244.append(card_sc)
if card_box is not None:
    cards_243_244.append(card_box)
if cards_243_244:
    show_cards(cards_243_244, ncols=min(2, len(cards_243_244)))
