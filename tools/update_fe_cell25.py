import json
import math
from pathlib import Path

import nbformat


NOTEBOOK_PATH = Path(r"C:/Users/cenkg/Desktop/apex/student_performance_final.ipynb")
CELL_IDX = 25


NEW_SOURCE = """# 4 Feature Engineering: 6+ yeni feature + raporlama (OPTİMİZE)

from sklearn.feature_selection import mutual_info_regression

fe_df = clean_df.copy()

# Yardımcı güvenli bölme
EPS = 1e-9

# 4.1.1 Oran / etkileşim özellikleri
if all(c in fe_df.columns for c in ["Weekly_Study_Hours", "Sleep_Hours"]):
    fe_df["study_per_sleep"] = fe_df["Weekly_Study_Hours"] / (fe_df["Sleep_Hours"] + EPS)

if all(c in fe_df.columns for c in ["Internet_Usage_Time", "Sleep_Hours"]):
    fe_df["internet_per_sleep"] = fe_df["Internet_Usage_Time"] / (fe_df["Sleep_Hours"] + EPS)

if all(c in fe_df.columns for c in ["Attendance_Rate", "Weekly_Study_Hours"]):
    fe_df["attendance_x_study"] = fe_df["Attendance_Rate"] * fe_df["Weekly_Study_Hours"]

if all(c in fe_df.columns for c in ["Previous_Scores", "Practice_Exams_Passed"]):
    fe_df["preparedness_index"] = 0.7 * fe_df["Previous_Scores"] + 0.3 * fe_df["Practice_Exams_Passed"]

if "Stress_Level" in fe_df.columns:
    fe_df["stress_inverse"] = 1.0 / (fe_df["Stress_Level"] + 1.0)

# 4.1.2 Polynomial (karesel) — seçili kolonlar
for col in [c for c in ["Weekly_Study_Hours", "Attendance_Rate", "Previous_Scores"] if c in fe_df.columns]:
    fe_df[f"{col}_sq"] = fe_df[col] ** 2

# 4.1.3 Binning (kategorileştirme)
if "Sleep_Hours" in fe_df.columns:
    fe_df["Sleep_Bin"] = pd.qcut(fe_df["Sleep_Hours"], q=4, labels=["Q1_low", "Q2_mid", "Q3_mid", "Q4_high"])

if "Internet_Usage_Time" in fe_df.columns:
    fe_df["Internet_Bin"] = pd.qcut(
        fe_df["Internet_Usage_Time"], q=4, labels=["Q1_low", "Q2_mid", "Q3_mid", "Q4_high"]
    )

# 4.1.4 Hızlı kontrol
new_cols = [c for c in fe_df.columns if c not in clean_df.columns]
print("✅ Yeni feature sayısı (ham FE):", len(new_cols))
print("Yeni feature örnekleri:", new_cols[:12])

# ================================
# 4.2 Mutual Information (MI)
# ================================
X_cols = [c for c in fe_df.columns if c not in [target_col, "Student_ID"]]
X = fe_df[X_cols].copy()
y = fe_df[target_col].astype(float)

cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

# MI için basit encoding: kategorikleri kodla (sunum amaçlı)
X_mi = X.copy()
for c in cat_cols:
    X_mi[c] = X_mi[c].astype("category").cat.codes

mi = mutual_info_regression(X_mi, y, random_state=RANDOM_STATE)
mi_df = pd.DataFrame({"feature": X_cols, "mi": mi}).sort_values("mi", ascending=False)
mi_map = dict(zip(mi_df["feature"], mi_df["mi"]))

display(mi_df.head(15))

fig_mi = px.bar(
    mi_df.head(25),
    x="mi",
    y="feature",
    orientation="h",
    color_discrete_sequence=["#6c5ce7"],
    title="4.2.1 Mutual Information — Top 25 (bilgi katkısı)",
)
show_export(fig_mi, next_fig("fe_mutual_info_top"), title="4.2.1 Mutual Information — Top 25")

# ================================
# 4.3 Korelasyon (tek renk) + fazla benzer feature optimizasyonu
# ================================
num_fe = fe_df.select_dtypes(include=[np.number])

# Tek renk korelasyon: burada işaret (poz/neg) yerine benzerlik gücünü göstermek için |corr| kullanıyoruz.
if target_col in num_fe.columns:
    corr_fe = num_fe.corr(numeric_only=True)
    abs_corr = corr_fe.abs()

    fig_fe_corr = px.imshow(
        abs_corr,
        color_continuous_scale="Blues",
        zmin=0,
        zmax=1,
        title="4.3.1 Korelasyon matrisi (tek renk, |corr|)",
    )
    show_export(
        fig_fe_corr,
        next_fig("fe_corr_matrix_single"),
        title="4.3.1 Korelasyon matrisi (tek renk, |corr|)",
    )

    # 1'e yakın (aşırı benzer) çiftleri bul
    THRESH = 0.90
    feats = [c for c in abs_corr.columns if c not in [target_col, "Student_ID"]]

    pairs = []
    for i in range(len(feats)):
        for j in range(i + 1, len(feats)):
            a, b = feats[i], feats[j]
            v = float(abs_corr.loc[a, b])
            if v >= THRESH:
                pairs.append((a, b, v))

    # Exam_Score ilişkisi (mutlak korelasyon) ve MI ile karar skoru
    target_abs = abs_corr[target_col].drop(target_col)

    # MI normalize (0-1) — sadece karşılaştırma için
    import numpy as _np

    mi_vals = _np.array([mi_map.get(f, 0.0) for f in feats], dtype=float)
    mi_min = float(mi_vals.min()) if len(mi_vals) else 0.0
    mi_max = float(mi_vals.max()) if len(mi_vals) else 1.0

    def mi_norm(f: str) -> float:
        v = float(mi_map.get(f, 0.0))
        if mi_max - mi_min < 1e-12:
            return 0.0
        return (v - mi_min) / (mi_max - mi_min)

    def score(f: str) -> float:
        # Basit, anlaşılır karar: hedefle ilişki daha önemli; MI destekleyici.
        return 0.65 * float(target_abs.get(f, 0.0)) + 0.35 * mi_norm(f)

    to_drop = set()
    decisions = []

    for a, b, v in sorted(pairs, key=lambda x: x[2], reverse=True):
        if a in to_drop or b in to_drop:
            continue

        sa, sb = score(a), score(b)
        keep, drop = (a, b) if sa >= sb else (b, a)
        to_drop.add(drop)

        decisions.append(
            {
                "pair": f"{a} ↔ {b}",
                "abs_corr": v,
                "keep": keep,
                "drop": drop,
                "Exam_Score_corr_keep": float(target_abs.get(keep, 0.0)),
                "Exam_Score_corr_drop": float(target_abs.get(drop, 0.0)),
                "MI_keep": float(mi_map.get(keep, 0.0)),
                "MI_drop": float(mi_map.get(drop, 0.0)),
            }
        )

    dec_df = pd.DataFrame(decisions)

    if len(dec_df):
        display(dec_df)

        plot_rows = []
        for r in decisions:
            plot_rows.append(
                {
                    "feature": r["keep"],
                    "status": "Keep",
                    "abs_target_corr": r["Exam_Score_corr_keep"],
                    "mi": r["MI_keep"],
                }
            )
            plot_rows.append(
                {
                    "feature": r["drop"],
                    "status": "Drop",
                    "abs_target_corr": r["Exam_Score_corr_drop"],
                    "mi": r["MI_drop"],
                }
            )

        plot_df = pd.DataFrame(plot_rows).sort_values(["abs_target_corr", "mi"], ascending=False)

        fig_pick = px.bar(
            plot_df,
            x="abs_target_corr",
            y="feature",
            color="status",
            orientation="h",
            title="4.3.2 Benzer (|corr|≈1) feature’larda: Exam_Score ilişkisi ile seçim",
            color_discrete_map={"Keep": "#16a34a", "Drop": "#ef4444"},
            hover_data={"mi": ":.4f", "abs_target_corr": ":.3f", "status": True},
        )
        show_export(fig_pick, next_fig("fe_highcorr_pick"), title="4.3.2 Benzer feature seçimi (Exam_Score + MI)")

        ex = decisions[0]
        note_card(
            "Benzer feature’larda karar mantığı",
            [
                f"{ex['pair']} arasında korelasyon çok yüksek (|corr|={ex['abs_corr']:.2f}) → iki sütun aynı şeyi tekrar ediyor.",
                f"Bu değerle bu değer arasında bir karar verildiğinde Exam_Score ile ilişkisi daha az kuvvetli olduğundan ({ex['drop']} |corr|={ex['Exam_Score_corr_drop']:.2f}), aynı korelasyonlu olan bu değeri silmeye karar verdik.",
                "Kararı tek başına korelasyonla değil; MI (bilgi katkısı) ile de destekledik.",
            ],
            note="Amaç: ‘daha az ama daha anlamlı’ feature seti — tekrar eden bilgiyi azaltıp modeli daha stabil yapmak.",
        )
    else:
        note_card(
            "Benzer feature kontrolü",
            [
                f"|corr| ≥ {THRESH:.2f} seviyesinde ‘neredeyse aynı’ iki feature bulunmadı.",
                "Bu yüzden FE ile gelen yeni sütunlar şimdilik korunabilir.",
            ],
        )

    fe_df_final = fe_df.drop(columns=sorted(list(to_drop))) if len(to_drop) else fe_df.copy()

    kept_new = [c for c in fe_df_final.columns if c in new_cols]
    dropped_new = [c for c in to_drop if c in new_cols]

    note_card(
        "Nihai karar (özet)",
        [
            f"Yeni feature sayısı: ham {len(new_cols)} → final {len(kept_new)} (drop: {len(dropped_new)}).",
            "Drop edilenler: başka bir sütunla neredeyse aynı bilgiyi taşıdığı için elendi.",
            "Kalanlar: Exam_Score ile ilişkisi daha güçlü ve/veya MI katkısı daha yüksek olanlar.",
        ],
        note="Bu kararlar modelleme adımında (CV ile) ayrıca doğrulanmalıdır; burada amaç pratik ve anlaşılır bir optimizasyon.",
    )
else:
    fe_df_final = fe_df.copy()

# 4.4 Feature tablosunu kaydet (nihai)
FEATURE_PATH = DATA_PROCESSED_DIR / "student_performance_features.csv"
fe_df_final.to_csv(FEATURE_PATH, index=False)
print("✅ Nihai feature tablosu kaydedildi:", FEATURE_PATH)
"""


def _cleanse(x):
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
        return x
    if isinstance(x, list):
        return [_cleanse(v) for v in x]
    if isinstance(x, dict):
        return {k: _cleanse(v) for k, v in x.items()}
    return x


def main() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    nb.cells[CELL_IDX].source = NEW_SOURCE
    nbformat.write(nb, NOTEBOOK_PATH)

    # Re-write as strict JSON for tooling that rejects NaN/Inf
    data = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    NOTEBOOK_PATH.write_text(
        json.dumps(_cleanse(data), ensure_ascii=False, indent=1, allow_nan=False),
        encoding="utf-8",
    )

    print(f"Updated cell {CELL_IDX} in {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

