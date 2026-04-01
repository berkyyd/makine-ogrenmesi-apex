# 3.1 Missing & outlier detection (Plotly) + yorum

# Missing counts
missing_cnt = df_raw.isna().sum().sort_values(ascending=False)
missing_pct = (df_raw.isna().mean() * 100).sort_values(ascending=False)
missing_df = (
    pd.DataFrame({"missing_count": missing_cnt, "missing_pct": missing_pct})
    .reset_index()
    .rename(columns={"index": "column"})
)

# % formatını net gösterelim
missing_df["missing_pct"] = missing_df["missing_pct"].map(lambda x: float(x))
missing_df["missing_pct_str"] = missing_df["missing_pct"].map(lambda x: f"%{x:.2f}")

display(missing_df[["column", "missing_count", "missing_pct_str"]])
spacer(10)

# Kısa yorum kartı (tablo + heatmap’i birlikte okuyan anlatım)
total_cells = int(df_raw.shape[0] * df_raw.shape[1])
missing_cells = int(df_raw.isna().sum().sum())
overall_pct = (missing_cells / total_cells * 100) if total_cells else 0.0

top_missing = missing_df[missing_df["missing_count"] > 0].head(3)
if len(top_missing) > 0:
    top_txt = ", ".join([f"{r.column}: {int(r.missing_count)} ({r.missing_pct_str})" for r in top_missing.itertuples(index=False)])
else:
    top_txt = "Eksik değer yok."

# Eksik değer olan kolon sayısı (net ifade için)
missing_cols_n = int((missing_df["missing_count"] > 0).sum())
missing_cols_list = missing_df.loc[missing_df["missing_count"] > 0, "column"].tolist()
missing_cols_list_txt = ", ".join(missing_cols_list) if len(missing_cols_list) else "—"

narrate(
    "Eksik değer özeti",
    [
        f"Tüm hücreler üzerinden toplam eksik oranı: %{overall_pct:.2f}.",
        f"Eksik değer sadece {missing_cols_n} özellikte görülüyor; satır silmek yerine bu özelliklerde hedefli imputation yapmak daha doğru.",
    ],
)

# Missing heatmap (0/1)
miss_mat = df_raw.isna().astype(int)
if miss_mat.to_numpy().sum() == 0:
    narrate(
        "Eksik değer analizi",
        [
            "Veri setinde eksik değer görünmüyor (missing=0).",
            "Bu, imputation bölümünü ‘karşılaştırma’ amaçlı göstereceğimiz; fakat pipeline’da yine de güvenli imputer kullanacağımız anlamına gelir.",
        ],
    )
else:
    fig_miss = px.imshow(
        miss_mat,
        aspect="auto",
        color_continuous_scale=[[0, "#ecfeff"], [1, "#ef4444"]],
        labels=dict(x="Columns", y="Rows", color="Missing"),
    )
    show_export(fig_miss, next_fig("prep_missing_heatmap"), title="3.1.1 Missing Values Heatmap")
    spacer(8)

    # Heatmap analiz kartı (görseli ölçerek yorumla)
    row_missing = miss_mat.sum(axis=1)  # satır başına kaç eksik var
    any_missing_row = (row_missing > 0)
    any_missing_rows_n = int(any_missing_row.sum())
    any_missing_rows_pct = float(any_missing_rows_n / max(len(row_missing), 1) * 100)

    # En yoğun missing bandı: rolling pencere ile (2.000 satır) en yüksek missing oranını bul
    win = int(min(2000, max(50, len(row_missing) // 5)))
    roll = row_missing.rolling(window=win, min_periods=max(10, win // 10)).mean()
    peak_end = int(roll.idxmax()) if roll.notna().any() else None
    if peak_end is not None:
        peak_start = max(0, peak_end - win + 1)
        peak_mean = float(roll.loc[peak_end])
        peak_txt = f"{peak_start:,}–{peak_end:,} aralığında satır başına ortalama ≈ {peak_mean:.2f} eksik"
    else:
        peak_txt = "belirgin bir yoğunlaşma bandı hesaplanamadı"

    # Kolon yoğunluğu
    top_cols = missing_df.loc[missing_df["missing_count"] > 0, "column"].head(3).tolist()
    top_cols_txt = ", ".join(top_cols) if top_cols else "—"

    # Dağınık mı blok mu? (heuristic): peak bandı genel ortalamanın belirgin üstünde mi?
    overall_mean = float(row_missing.mean())
    if peak_end is not None and overall_mean > 0:
        ratio = peak_mean / overall_mean if overall_mean else 1.0
        pattern_txt = "Eksikler satırlar boyunca genel olarak dağınık; net bir blok/batch etkisi baskın görünmüyor." if ratio < 1.6 else "Eksikler belirli bir satır bandında daha yoğun; bu, batch/grup kaynaklı yapısal eksiklik ihtimalini artırır."
    else:
        pattern_txt = "Eksik değer yapısı sınırlı görünüyor; satır bazında belirgin bir blok paterni çıkmıyor."

    narrate(
        "Missing heatmap analizi",
        [
            "Tanım: Satır–sütun bazında eksik hücre konumları (kırmızı=eksik).",
            f"Özet: {any_missing_rows_n:,}/{len(row_missing):,} satırda en az 1 eksik var (%{any_missing_rows_pct:.2f}).",
            f"Yoğunluk: Eksikler ağırlıkla {top_cols_txt} kolonlarında.",
            f"Satır paterni: {peak_txt}.",
            pattern_txt,
            "Not: Bu profil, satır silmek yerine ilgili birkaç kolonda KNN gibi ilişki-koruyan imputation’ı destekler.",
        ],
    )

# Outlier detection (IQR + Z-score)
num_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()

out_rows = []
for col in num_cols:
    s = df_raw[col].dropna()
    if len(s) < 10:
        continue
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    iqr_out = int(((s < lower) | (s > upper)).sum())

    z = (s - s.mean()) / (s.std(ddof=1) if s.std(ddof=1) != 0 else 1)
    z_out = int((z.abs() > 3).sum())

    out_rows.append({
        "column": col,
        "iqr_outliers": iqr_out,
        "iqr_outlier_pct": iqr_out / max(len(s), 1) * 100,
        "z_outliers": z_out,
        "z_outlier_pct": z_out / max(len(s), 1) * 100,
        "iqr_lower": float(lower),
        "iqr_upper": float(upper),
    })

out_df = pd.DataFrame(out_rows).sort_values("iqr_outliers", ascending=False)
display(out_df.head(10))
spacer(10)

fig_out_bar = px.bar(
    out_df,
    x="column",
    y="iqr_outlier_pct",
    color="z_outlier_pct",
    color_continuous_scale="RdBu",
    labels={"iqr_outlier_pct": "IQR Outlier %", "z_outlier_pct": "Z-score Outlier %"},
)
fig_out_bar.update_layout(xaxis_tickangle=25)
show_export(fig_out_bar, next_fig("prep_outlier_rates"), title="3.1.2 Outlier Oranları (IQR % + Z-score %) ")

worst = out_df.head(3)
n1 = out_df.sort_values("iqr_outlier_pct", ascending=False).head(1)
n2 = out_df.sort_values("z_outlier_pct", ascending=False).head(1)
if len(n1) > 0:
    r1 = n1.iloc[0]
else:
    r1 = None
if len(n2) > 0:
    r2 = n2.iloc[0]
else:
    r2 = None

ex_txt_parts = []
if r1 is not None:
    ex_txt_parts.append(f"{r1['column']} (IQR %{r1['iqr_outlier_pct']:.2f})")
if r2 is not None and (r1 is None or r2['column'] != r1['column']):
    ex_txt_parts.append(f"{r2['column']} (Z-score %{r2['z_outlier_pct']:.2f})")
ex_txt = " & ".join(ex_txt_parts) if ex_txt_parts else "—"

narrate(
    "Aykırı değer tespiti (IQR + Z-score)",
    [
        "Çubuk yüksekliği (IQR %) arttıkça: “tipik aralığın dışına taşma” daha sık. Renk maviye yaklaştıkça (Z-score %): daha “ekstrem” sapmalar daha fazla.",
        f"Örnek: Grafikte maviye yakın olan {r2['column'] if r2 is not None else 'kolon'} → ekstrem sapma oranı görece yüksek; en yüksek çubuk olan {r1['column'] if r1 is not None else 'kolon'} → tipik aralığın dışına çıkma daha sık.",
        f"Pratik çıkarım: 3.2’de bu iki kolon ({ex_txt}) üzerinde önce ‘hata→NaN→impute’, sonra gerekiyorsa seçici capping uygulayınca before/after farkı en net görünür.",
    ],
    note="Sonraki adım: 3.2’de imputation karşılaştırması ve capping ile önce/sonra etkisini göstermek.",
)
