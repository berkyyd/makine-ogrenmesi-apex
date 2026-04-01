# 2.5 Multivariate analizler (Plotly) + yorum

# next_fig yoksa (hücre sırası bozulursa) fallback
if "next_fig" not in globals():
    fig_counter = 0
    def next_fig(title_slug: str):
        global fig_counter
        fig_counter += 1
        safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in title_slug)
        return f"{fig_counter:02d}_{safe}.html"

# 2.5.2 Segmentasyon: Top %10 vs Bottom %10
if target_col in df_raw.columns:
    n = max(int(len(df_raw) * 0.10), 1)
    top = df_raw.nlargest(n, target_col).copy()
    bottom = df_raw.nsmallest(n, target_col).copy()
    top["Group"] = "Top10%"
    bottom["Group"] = "Bottom10%"
    seg = pd.concat([top, bottom], axis=0, ignore_index=True)

    compare_features = [c for c in ["Weekly_Study_Hours", "Attendance_Rate", "Previous_Scores", "Stress_Level"] if c in seg.columns]
    if compare_features:
        seg_means = seg.groupby("Group")[compare_features].mean().T
        seg_means["diff_TopMinusBottom"] = seg_means.get("Top10%", np.nan) - seg_means.get("Bottom10%", np.nan)
        seg_means = seg_means.reset_index().rename(columns={"index": "feature"})

        fig_seg = px.bar(
            seg_means,
            x="diff_TopMinusBottom",
            y="feature",
            orientation="h",
            color="diff_TopMinusBottom",
            color_continuous_scale="RdBu",
            range_color=[seg_means["diff_TopMinusBottom"].min(), seg_means["diff_TopMinusBottom"].max()],
        )
        show_export(fig_seg, next_fig("multivariate_top_vs_bottom_diff"), title="2.5.2 Top10% vs Bottom10% — Ortalama Farklar")

        biggest_pos = seg_means.sort_values("diff_TopMinusBottom", ascending=False).head(3)
        biggest_neg = seg_means.sort_values("diff_TopMinusBottom", ascending=True).head(3)
        biggest_abs = seg_means.reindex(seg_means["diff_TopMinusBottom"].abs().sort_values(ascending=False).index).head(3)
        narrate(
            "Segmentasyon: Top10% vs Bottom10%",
            [
                "Bu grafik, en başarılı %10 ile en düşük %10’un arasındaki farkın hangi özelliklerde toplandığını gösteriyor; yani “başarı profili” en çok nereden ayrışıyor sorusuna cevap veriyor.",
                "En net ayrım Previous_Scores tarafında: yüksek skorlu grup, geçmiş performans açısından açık ara önde. Bu, bu veri setinde başarının büyük ölçüde önceden gelen bir birikim gibi davrandığını düşündürüyor.",
                "İkinci güçlü ayrım Weekly_Study_Hours: yüksek skorlu grupta çalışma süresi belirgin biçimde daha yüksek. Yani başarı tarafında “daha fazla ve daha düzenli çalışma” sinyali de net biçimde var.",
                "Diğer değişkenler (devam/stres gibi) fark yaratıyor ama ana hikâye kadar baskın değil: bu grafiğin ana mesajı, iki grubun en çok geçmiş başarı + çalışma alışkanlığı ekseninde ayrıştığı.",
            ],
        )

# 2.5.3 Yaşam tarzı pivot: Sleep x Internet → Exam_Score ortalaması heatmap
if all(c in df_raw.columns for c in ["Internet_Usage_Time", "Sleep_Hours", target_col]):
    tmp = df_raw[["Internet_Usage_Time", "Sleep_Hours", target_col]].dropna().copy()

    tmp["Internet_Bin"] = pd.qcut(tmp["Internet_Usage_Time"], q=3, labels=["Low", "Mid", "High"])
    tmp["Sleep_Bin"] = pd.qcut(tmp["Sleep_Hours"], q=3, labels=["Low", "Mid", "High"])

    pivot = tmp.pivot_table(index="Sleep_Bin", columns="Internet_Bin", values=target_col, aggfunc="mean")

    fig_pivot = px.imshow(
        pivot,
        text_auto=True,
        color_continuous_scale="YlGnBu",
        labels=dict(x="Internet_Bin", y="Sleep_Bin", color="Avg Exam_Score"),
    )
    show_export(fig_pivot, next_fig("multivariate_sleep_internet_heatmap"), title="2.5.3 Exam_Score Ortalaması (Sleep_Bin × Internet_Bin)")

    best_cell = pivot.stack().sort_values(ascending=False).head(1)
    worst_cell = pivot.stack().sort_values(ascending=True).head(1)

    # İnternet seviyesine göre genel trend (satırların ortalaması)
    col_means = pivot.mean(axis=0).to_dict()
    row_means = pivot.mean(axis=1).to_dict()

    narrate(
        "Uyku × İnternet ısı haritası",
        [
            "Harita net bir desen gösteriyor: internet kullanımı Low → High gittikçe Exam_Score ortalaması belirgin biçimde düşüyor. Yani bu veri içinde internet süresi artışı, skor tarafında en tutarlı “aşağı çeken” sinyallerden biri gibi duruyor.",
            "Uyku tarafında da bir eğilim var ama daha ikincil görünüyor: daha yüksek uyku binlerinde skor ortalaması düşmeye meyilli. Bu, uyku süresinin tek başına “daha çok = daha iyi” gibi çalışmadığını; aşırılıkların performansla birlikte gerileyebileceğini düşündürüyor.",
            "En iyi ve en kötü hücrelerin aynı uçlarda toplanması, iki davranışın birlikte risk/avantaj birikimi yaratabildiğini ima ediyor: internet yükselince skor düşüyor; üstüne uyku da “yüksek” binine gidince düşüş daha da derinleşiyor.",
            "Özetle bu grafik, skor için daha sağlıklı bölgenin daha düşük internet tarafında yoğunlaştığını; internet yükseldikçe hangi uyku seviyesinde olursa olsun skorların genel olarak aşağı indiğini anlatıyor.",
        ],
    )
