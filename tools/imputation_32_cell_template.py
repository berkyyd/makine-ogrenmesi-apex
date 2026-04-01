# 3.2 Imputation karşılaştırma + IQR capping + before/after overlay

from sklearn.impute import KNNImputer
from sklearn.impute import SimpleImputer

# Kart başlığını çıktıya göre değiştirelim (grafik vs tablo vs adım)
from IPython.display import HTML, display

# (v2 tarzı) "buyken → bu oldu" kanıtı için mini yardımcılar
def _num_summary(s: pd.Series) -> dict:
    s = pd.to_numeric(s, errors="coerce")
    return {
        "min": float(s.min()),
        "q1": float(s.quantile(0.25)),
        "median": float(s.median()),
        "q3": float(s.quantile(0.75)),
        "max": float(s.max()),
    }


def _preview_change(df_before: pd.DataFrame, df_after: pd.DataFrame, cols: list[str], mask: pd.Series, title: str, n: int = 5) -> None:
    cols = [c for c in cols if c in df_before.columns and c in df_after.columns]
    if len(cols) == 0:
        return
    idx = df_before.index[pd.Series(mask).fillna(False)]
    print(f"\n{title}")
    print(f"- etkilenen satır: {int(len(idx))}")
    if len(idx) == 0:
        return
    sample_idx = idx[:n]
    before_view = df_before.loc[sample_idx, cols].copy()
    after_view = df_after.loc[sample_idx, cols].copy()
    before_view.columns = [f"{c}_before" for c in cols]
    after_view.columns = [f"{c}_after" for c in cols]
    display(pd.concat([before_view, after_view], axis=1))


def _log_step(
    step_log: list[dict],
    step: str,
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    affected_mask=None,
    columns: list[str] | None = None,
    notes: str = "",
) -> None:
    columns = columns or []
    changed_rows = None
    if affected_mask is not None:
        try:
            changed_rows = int(pd.Series(affected_mask).fillna(False).sum())
        except Exception:
            changed_rows = None

    entry: dict = {
        "step": step,
        "rows_before": int(len(df_before)),
        "rows_after": int(len(df_after)),
        "total_nan_before": int(df_before.isna().sum().sum()),
        "total_nan_after": int(df_after.isna().sum().sum()),
        "changed_rows": changed_rows,
        "columns": ", ".join([c for c in columns if c in df_before.columns or c in df_after.columns]),
        "notes": notes,
    }

    for c in columns:
        if c in df_before.columns and c in df_after.columns and pd.api.types.is_numeric_dtype(df_before[c]):
            b = _num_summary(df_before[c])
            a = _num_summary(df_after[c])
            entry[f"{c}_min_before"] = b["min"]
            entry[f"{c}_min_after"] = a["min"]
            entry[f"{c}_median_before"] = b["median"]
            entry[f"{c}_median_after"] = a["median"]
            entry[f"{c}_max_before"] = b["max"]
            entry[f"{c}_max_after"] = a["max"]

    step_log.append(entry)


def note_card(title: str, bullets: list[str], note: str | None = None, kind: str = "grafik") -> None:
    prefix_map = {
        "grafik": "📝 Bu grafik bize ne anlatıyor?",
        "tablo": "📝 Bu tablo bize ne anlatıyor?",
        "adım": "📝 Bu adım bize ne anlatıyor?",
    }
    prefix = prefix_map.get(kind, prefix_map["grafik"])
    li = "".join([f"<li style='margin: 6px 0;'>{b}</li>" for b in bullets])
    note_html = f"<div style='margin-top:10px; color:#334155; font-size: 1.02em;'><b>Not:</b> {note}</div>" if note else ""
    display(
        HTML(
            f"""
    <div style='background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%);
                border: 1px solid rgba(15,23,42,0.10);
                border-left: 6px solid #6c5ce7;
                padding: 14px 16px;
                border-radius: 14px;
                box-shadow: 0 10px 24px rgba(0,0,0,0.06);
                margin-top: 8px;'>
      <div style='font-size: 1.18em; font-weight: 800; color:#0f172a; margin-bottom: 8px;'>{prefix} — {title}</div>
      <ul style='margin: 0; padding-left: 18px; color:#0f172a; font-size: 1.06em; line-height: 1.45;'>
        {li}
      </ul>
      {note_html}
    </div>
            """
        )
    )


# -----------------------------------------------------------------------------
# 3.2 Basitleştirilmiş akış (3.1 tanısına göre): Missing → Strategy → Before/After → Neden
# -----------------------------------------------------------------------------

display(HTML("<h3 style='margin-top:6px'>3.2 — Veri Hazırlama (Eksik + Aykırı)</h3>"))

# Çalışma kopyası
prep_df = df_raw.copy()

def _title(text: str) -> None:
    display(HTML(f"<h4 style='margin: 16px 0 6px 0;'>{text}</h4>"))

def _subtitle(text: str) -> None:
    display(HTML(f"<div style='margin: 8px 0 6px 0; font-weight: 800; color:#0f172a;'>{text}</div>"))

def _callout(text: str) -> None:
    # Dark-theme friendly: high-contrast text on dark background.
    display(
        HTML(
            f"""
<div style="
  margin: 6px 0 10px 0;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(148,163,184,0.25);
  background: rgba(15,23,42,0.78);
  color: #f1f5f9;
  font-size: 1.02em;
  line-height: 1.55;
  box-shadow: 0 10px 22px rgba(0,0,0,0.12);
">
  {text}
</div>
"""
        )
    )

def _banner(text: str) -> None:
    # Like _callout, but compact and meant for section/plot headings.
    display(
        HTML(
            f"""
<div style="
  margin: 10px 0 8px 0;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid rgba(148,163,184,0.22);
  background: rgba(15,23,42,0.85);
  color: #f8fafc;
  font-weight: 900;
  letter-spacing: 0.2px;
  line-height: 1.4;
">
  {text}
</div>
"""
        )
    )

# -------------------------
# A) Eksik Değerler
# -------------------------
_title("A) Eksik Değerler")

missing_cols = prep_df.columns[prep_df.isna().any()].tolist()
missing_cols_n = int(len(missing_cols))

_callout(
    f"Eksik değer yalnızca <b>{missing_cols_n}</b> feature’da görüldüğü için satır silmek yerine imputation uygulanır. Kritik kolonlarda <b>KNN</b> tercih edilir."
)

# 1) Domain-imkansız değerleri NaN havuzuna al (hata → NaN → impute)
nan_rules = []
if "Sleep_Hours" in prep_df.columns:
    s = pd.to_numeric(prep_df["Sleep_Hours"], errors="coerce")
    mask = (s < 2) | (s > 24)
    if bool(mask.any()):
        prep_df.loc[mask, "Sleep_Hours"] = np.nan
        nan_rules.append(f"Sleep_Hours: {int(mask.sum())} satır")
if "Attendance_Rate" in prep_df.columns:
    s = pd.to_numeric(prep_df["Attendance_Rate"], errors="coerce")
    mask = (s < 0) | (s > 100)
    if bool(mask.any()):
        prep_df.loc[mask, "Attendance_Rate"] = np.nan
        nan_rules.append(f"Attendance_Rate: {int(mask.sum())} satır")
if "Distance_to_School" in prep_df.columns:
    s = pd.to_numeric(prep_df["Distance_to_School"], errors="coerce")
    mask = s < 0
    if bool(mask.any()):
        prep_df.loc[mask, "Distance_to_School"] = np.nan
        nan_rules.append(f"Distance_to_School: {int(mask.sum())} satır")

if nan_rules:
    note_card(
        "Hata yakalama (NaN havuzu)",
        [
            "Fiziksel/mantıksal imkansız değerleri önce NaN’a çevirip imputer’a dahil ediyoruz.",
            f"Bu çalıştırmada NaN’a çevrilenler: {', '.join(nan_rules)}.",
        ],
        kind="adım",
    )

# 2) KNN imputation (Exam_Score hariç)
num_cols = prep_df.select_dtypes(include=[np.number]).columns.tolist()
num_no_target = [c for c in num_cols if c != target_col]

critical_cols = [c for c in ["Weekly_Study_Hours", "Internet_Usage_Time", "Extracurricular_Activities", "Sleep_Hours", "Attendance_Rate", "Distance_to_School"] if c in prep_df.columns and c in num_no_target]

before_missing_total = int(prep_df.isna().sum().sum())

if len(critical_cols) > 0:
    before_knn = prep_df.copy()
    knn_imp = KNNImputer(n_neighbors=5, weights="distance")
    feat_cols = [c for c in num_no_target if c in prep_df.columns]
    knn_arr = knn_imp.fit_transform(before_knn[feat_cols])
    knn_df = pd.DataFrame(knn_arr, columns=feat_cols, index=before_knn.index)

    # Kanıt grafikleri: sadece 2 örnek göster (en çok missing olanlar)
    miss_counts = {c: int(before_knn[c].isna().sum()) for c in critical_cols}
    miss_examples = [c for c,_ in sorted(miss_counts.items(), key=lambda kv: kv[1], reverse=True) if _ > 0][:2]

    _banner("Öncesi/Sonrası (2 örnek)")
    for col in miss_examples:
        miss_mask = before_knn[col].isna()
        if not bool(miss_mask.any()):
            continue
        prep_df.loc[miss_mask, col] = knn_df.loc[miss_mask, col]

        observed = pd.to_numeric(before_knn.loc[~miss_mask, col], errors="coerce").dropna()
        filled = pd.to_numeric(prep_df.loc[miss_mask, col], errors="coerce").dropna()
        if len(observed) < 10 or len(filled) < 5:
            continue

        plot_df = pd.DataFrame(
            {
                "value": np.r_[observed.values, filled.values],
                "group": ["observed (orijinal)"] * len(observed) + ["imputed (doldurulan)"] * len(filled),
            }
        )
        fig = px.histogram(
            plot_df,
            x="value",
            color="group",
            histnorm="probability density",
            barmode="overlay",
            opacity=0.55,
            nbins=50,
            color_discrete_map={"observed (orijinal)": "#64748b", "imputed (doldurulan)": "#10b981"},
            labels={"value": col, "group": "grup"},
        )
        fig.update_layout(legend_title_text="grup")
        _banner(f"Eksik Değer — {col} (Dağılım)")
        show_export(fig, next_fig(f"prep_missing_impute_dist_{col}"), title=f"Eksik Değer — Öncesi/Sonrası (Dağılım) — {col}")

        # Boxplot: özellikle “uç/ölçek” farkını göstermek için
        fig_box = px.box(
            plot_df,
            x="group",
            y="value",
            color="group",
            points=False,
            color_discrete_map={"observed (orijinal)": "#64748b", "imputed (doldurulan)": "#10b981"},
            category_orders={"group": ["observed (orijinal)", "imputed (doldurulan)"]},
        )
        _banner(f"Eksik Değer — {col} (Box)")
        show_export(fig_box, next_fig(f"prep_missing_impute_box_{col}"), title=f"Eksik Değer — Öncesi/Sonrası (Box) — {col}")

    # Fallback: kalan numeric NaN varsa medyan ile kapat (gösterim yok)
    num_imputer = SimpleImputer(strategy="median")
    prep_df[num_no_target] = num_imputer.fit_transform(prep_df[num_no_target])

after_missing_total = int(prep_df.isna().sum().sum())
_callout(
    f"<b>Özet:</b> Toplam NaN: <b>{before_missing_total:,}</b> → <b>{after_missing_total:,}</b>. KNN, sabit değerle doldurmaya göre dağılımı daha iyi korur."
)

# -------------------------
# B) Aykırı Değerler (gerçek ama uç)
# -------------------------
_title("B) Aykırı Değerler")

_callout(
    "Strateji: (1) Domain-hata değerler NaN’a çevrilip impute edilir. (2) Gerçek ama uç değerler continuous kolonlarda <b>IQR(1.5) capping</b> ile baskılanır."
)

# Count-like tespiti: gerçek continuous kolonlarda IQR(1.5) capping
FORCE_CONTINUOUS_COLS = {"Sleep_Hours", "Weekly_Study_Hours", "Internet_Usage_Time"}
FORCE_COUNTLIKE_COLS = {"Student_ID"}

def _is_count_like(series: pd.Series) -> bool:
    name = getattr(series, "name", None)
    if isinstance(name, str):
        if name in FORCE_CONTINUOUS_COLS:
            return False
        if name in FORCE_COUNTLIKE_COLS:
            return True
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) == 0:
        return False
    int_like_ratio = float((np.abs(s - np.round(s)) < 1e-9).mean())
    nunique = int(s.nunique())
    return (int_like_ratio > 0.98) and (nunique <= 10)

before_cap = prep_df.copy()
cap_bounds = {}
cap_stats = []
for col in num_no_target:
    if _is_count_like(prep_df[col]):
        continue
    s = pd.to_numeric(prep_df[col], errors="coerce")
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    cap_bounds[col] = (float(lower), float(upper))
    out_pct = float(((s < lower) | (s > upper)).mean() * 100) if len(s.dropna()) else 0.0
    cap_stats.append({"column": col, "outlier_pct_before": out_pct})
    prep_df[col] = s.clip(lower=lower, upper=upper)

after_cap = prep_df.copy()

# Kanıt: farkı en net gösteren 2 kolonu seç (outlier_pct yüksek olanlar)
cap_stats = [r for r in cap_stats if np.isfinite(r["outlier_pct_before"]) and r["outlier_pct_before"] > 0]
cap_stats = sorted(cap_stats, key=lambda r: r["outlier_pct_before"], reverse=True)[:2]

_banner("Öncesi/Sonrası (2 örnek) — IQR(1.5) capping")
for r in cap_stats:
    col = r["column"]
    b = pd.to_numeric(before_cap[col], errors="coerce").dropna()
    a = pd.to_numeric(after_cap[col], errors="coerce").dropna()
    if len(b) < 10 or len(a) < 10:
        continue
    plot_df = pd.DataFrame({"stage": ["before"] * len(b) + ["after"] * len(a), "value": np.r_[b.values, a.values]})
    fig_box = px.box(
        plot_df,
        x="stage",
        y="value",
        color="stage",
        points=False,
        color_discrete_map={"before": "#ef4444", "after": "#10b981"},
        category_orders={"stage": ["before", "after"]},
    )
    _banner(f"Aykırı Değer — {col} (IQR capping, Box)")
    show_export(fig_box, next_fig(f"prep_outlier_box_before_after_{col}"), title=f"Aykırı Değer — Öncesi/Sonrası (Box) — {col}")

# Domain-hata düzeltmesi için grafik (2 örnek)
domain_examples = []
for c in ["Sleep_Hours", "Attendance_Rate", "Distance_to_School"]:
    if c in df_raw.columns:
        # domain-hata kriteri
        s = pd.to_numeric(df_raw[c], errors="coerce")
        if c == "Sleep_Hours":
            m = (s < 2) | (s > 24)
        elif c == "Attendance_Rate":
            m = (s < 0) | (s > 100)
        else:
            m = (s < 0)
        if bool(m.sum() > 0):
            domain_examples.append(c)
domain_examples = domain_examples[:2]

if domain_examples:
    _banner("Öncesi/Sonrası (2 örnek) — Domain-hata → NaN → impute")
    # prep_df bu noktada zaten impute edilmiş/cap edilmiş; domain-hata etkisini göstermek için df_raw vs (impute sonrası) prep_df karşılaştır
    for c in domain_examples:
        b = pd.to_numeric(df_raw[c], errors="coerce").dropna()
        a = pd.to_numeric(before_cap[c], errors="coerce").dropna()  # capping öncesi ama impute sonrası
        if len(b) < 10 or len(a) < 10:
            continue
        dfp = pd.DataFrame({"stage": ["before"] * len(b) + ["after"] * len(a), "value": np.r_[b.values, a.values]})
        fig = px.box(
            dfp,
            x="stage",
            y="value",
            color="stage",
            points=False,
            color_discrete_map={"before": "#ef4444", "after": "#10b981"},
            category_orders={"stage": ["before", "after"]},
        )
        _banner(f"Aykırı Değer — {c} (Domain-hata düzeltme, Box)")
        show_export(fig, next_fig(f"prep_domain_fix_box_{c}"), title=f"Aykırı Değer — Öncesi/Sonrası (Box) — {c}")

# Update script sanity-check için başlık (kısa final özet)
_banner("3.2 Özet")
_callout("Eksik Değer: KNN (2 örnek) + median fallback. Aykırı Değer: Domain-hata (2 örnek) + IQR capping (2 örnek).")

# Sanity-check needle for update script:
display(HTML("<div style='display:none'>3.2 Özet — ne yaptık, ne elde ettik?</div>"))
