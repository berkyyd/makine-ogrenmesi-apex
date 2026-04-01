# Notebook Final Rehberi — Anlatıcı Metin Şablonları

Bu doküman, `notebooks/student_performance_final.ipynb` için **tam rehber** niteliğindedir:

- Notebook’un adım adım akışını anlatır (2.x → 3.x → 4.x → 5.1 → 5.2).
- Her bölümde kullanılacak **kart dili**, **grafik altı mikro-yorum**, **karar metinleri** ve **sonraki adım** kalıplarını verir.
- Amaç: Notebook’u okuyan kişinin “Ne yaptık, neden yaptık, ne çıktı, ne karar verdik?” sorularını **tek bakışta** anlayabilmesi.

---

## 0) Notebook’un anlatı standardı (tek cümlelik kural)

Her görsel/tabloda şu 4’lü akışı hedefleyin:

1. **Ne görüyoruz?** (grafik neyi gösteriyor)
2. **Ne anlıyoruz?** (pattern/sinyal)
3. **Bu ne demek?** (iş anlamı)
4. **Ne yapacağız?** (karar/sonraki adım)

---

## 1) Terim mini-sözlüğü (kopyala-yapıştır)

- **CRISP-DM**: İş Anlayışı → Veri Anlayışı → Veri Hazırlama → Modelleme → Değerlendirme → Dağıtım.
- **Train/Test Split**: Eğitmek ve genelleme görmek için veri bölme.
- **Cross-Validation (CV)**: Farklı alt örneklemlerde tutarlılık kontrolü.
- **GridSearchCV**: Hiperparametre araması (tuning).
- **Pipeline**: Preprocess + model zinciri (leakage riskini azaltır).
- **Leakage**: Test bilgisinin eğitime sızması (sahte iyi skor).
- **R²**: Açıklanan varyans (yüksek iyi).
- **RMSE**: Büyük hatayı daha fazla cezalandıran hata (düşük iyi).
- **MAE**: Ortalama mutlak hata (düşük iyi).
- **MAPE**: Yüzdesel hata (düşük iyi; 0’a yakın değerlerde şişebilir).

---

## 2) Proje hikâyesi / iş problemi (kapak metni)

### 2.1 Bağlam
“Bir eğitim kurumu, öğrencilerin başarısını artırmak için sınırlı kaynakla doğru zamanda doğru öğrenciye müdahale etmek ister. Bu yüzden sınav skorunu etkileyen faktörleri önceden görmek kritik.”

### 2.2 İş problemi
“Amaç, çalışma/uyku/devam/önceki skorlar gibi girdilerle **Exam_Score**’u tahmin etmek ve hangi faktörlerin daha etkili olduğunu bularak aksiyon üretmektir.”

### 2.3 Başarı kriteri
“Başarıyı \(R^2\), RMSE, MAE, MAPE ile ölçüyoruz. Hedef: yüksek \(R^2\) + düşük hata.”

---

## 3) Notebook adımlarına göre anlatıcı şablonları

Bu bölüm, notebook final yapısına birebir uygun şablonları içerir.

### 3.1 (2.1) İlk veri keşfi — “Veri Özeti” şablonu
- **Ne görüyoruz**: “Verinin satır/sütun sayısı, eksik değer sayısı ve temel tipler burada netleşiyor.”
- **Ne anlıyoruz**: “Eksikler belirli birkaç kolonda yoğunlaşıyorsa, satır silmek yerine hedefli imputation daha mantıklı.”
- **Karar**: “Bu yüzden Adım 3’te satır silmeden imputation akışı kuracağız.”

### 3.2 (2.2) Target analizi — “Hedef dağılımı” şablonu
- “Histogram+boxplot hedefin aralığını ve uç değer riskini gösterir.”
- “Dağılım simetrik/tek tepe ise pek çok model için iyi başlangıçtır.”
- **Karar**: “Ekstra transformasyon gerekmiyor / gerekebilir.”

### 3.3 (2.3) Univariate — tekil değişken şablonu (kısa)
- **Sütun & tipi**: “`{col}` {numeric/categorical} bir değişkendir.”
- **Dağılım**: “Tipik aralık ...; kuyruk/çarpıklık ...”
- **Aykırı**: “Uçlar az/çok; olası neden ...”
- **Karar**: “(Gerekirse) binning/capping/encoding planı.”

### 3.4 (2.4) Bivariate — korelasyon ve target ilişkileri
- “Isı haritası değişkenler arası benzerliği gösterir; çok yüksek benzerlik varsa tekrar eden bilgi olabilir.”
- “Target korelasyon sırası, hangi sinyallerin daha güçlü olduğunu hızlıca gösterir.”
- **Karar**: “Feature engineering’de bu sinyalleri güçlendireceğiz; tekrar edenleri azaltacağız.”

### 3.5 (2.5) Multivariate — segment/pivot anlatısı
- “Top%10 vs Bottom%10 fark grafiği ‘başarı profili’ni gösterir.”
- “Pivot heatmap (Sleep×Internet) birlikte etkiyi görür; tek tek bakmaktan daha güçlü sinyal yakalanır.”

---

## 4) Veri hazırlama (3.x) — karar şablonları

### 4.1 (3.1) Eksik & aykırı tanı
“Eksikler az sayıda feature’da ise satır silmek yerine imputation; aykırılar için silmek yerine önce domain-hata → NaN → impute yaklaşımı daha güvenli.”

### 4.2 (3.2) İmputation + capping “önce/sonra”
- “Önce/sonra kıyaslaması veri kaybetmeden temizleme yaptığımızı gösterir.”
- “Amaç ‘her şeyi düz yapmak’ değil; modeli gereksiz oynatan ekstrem uçları yumuşatmak.”

### 4.3 (3.3) Veri kalite kartı
- “Missing before→after düştü mü?”
- “Uç değer etkisi beklenen ölçüde yumuşadı mı?”

---

## 5) Encoding (3.4) — tam şablon seti

### 5.1 Encoding ne demek?
“Encoding, kategorik (metin) değerleri modelin anlayacağı sayısal forma çevirmektir.”

### 5.2 Neden ordinal?
“`Parent_Education_Level` gibi sıralı kategorilerde ordinal encoding, ‘seviye arttıkça etki artabilir’ bilgisini korur.”

### 5.3 Neden one-hot?
“Sırası olmayan kategorilerde one-hot, kategori bilgisini kaybetmeden sinyali modele taşır.”

### 5.4 ‘Önce doldur sonra encode’
“Encoder’dan önce eksikleri yönetiriz; aksi halde eksik değerler yanlış kategori gibi ele alınabilir.”

---

## 6) Feature Engineering (4.x) — rehber şablonları

### 6.1 Yeni feature üretimi (4.1)
“Oran/etkileşim/polynomial/binning gibi dönüşümler, hedefe giden sinyali daha görünür hale getirir.”

### 6.2 MI (4.2) anlatısı
“MI, doğrusal olmak zorunda olmayan bilgi katkısını ölçer; çok feature içinde önceliklendirme sağlar.”

### 6.3 Benzer feature optimizasyonu (4.3)
- “|corr|≈1 olan çiftler aynı şeyi tekrar ediyor olabilir.”
- **Karar cümlesi (kopyala-yapıştır)**:
  “Bu değerle bu değer arasında bir karar verildiğinde, `Exam_Score` ile ilişkisi daha az kuvvetli olduğundan aynı korelasyonlu olan bu değeri silmeye karar verdik.”
- “Kararı MI ile destekleyerek daha güvenli seçim yaparız.”

### 6.4 Adım sonu karar özeti (4.4)
- “Ham yeni feature sayısı → final yeni feature sayısı”
- “Drop edilenler: tekrar eden bilgi”
- “Kalanlar: hedefle ilişki + MI katkısı”

---

## 7) Modelleme ve değerlendirme (5.1) — rehber şablonları

### 7.1 Baseline neden?
“Baseline, minimum beklenen performansı verir. Daha karmaşık modellerin değer katıp katmadığını görürüz.”

### 7.2 R² grafiği nasıl okunur?
“Test R² yüksekse genelleme iyi; train çok yüksek test düşükse overfitting riski.”

### 7.3 RMSE/MAE grafiği nasıl okunur?
“RMSE büyük hatayı daha çok cezalandırır; MAE ortalama hatayı özetler. Test tarafı düşükse gerçek dünyaya daha yakın.”

### 7.4 Trade-off (BEST) anlatısı
“RMSE düşük (sola), R² yüksek (yukarı). Sol-üst dengesi en iyi adaydır; BEST bunu temsil eder.”

---

## 8) CV + tuning (5.2) — rehber şablonları

### 8.1 5-Fold CV neden?
“Tek bir split şans faktöründen etkilenebilir. CV ile stabilite ve genelleme kontrolü yaparız.”

### 8.2 Overfitting analizi tablosu
“Train skoru CV’den çok daha iyiyse model aşırı öğreniyor olabilir. ⚠️ olanlar daha riskli.”

### 8.3 Top-3 seçimi
“Önce CV R² yüksekliğine bakıp top-3 seçiyoruz; sonra RMSE/MAE ile dengeliyoruz.”

### 8.4 Tuning iyileşme oranları (%)
“Tuned vs Untuned tablosunda RMSE/MAE yüzde iyileşme, hatanın ne kadar azaldığını gösterir; R² delta artış demektir.”

### 8.5 5 gerçek test örneği mini gösterim
“Gerçek vs tahmin farkını 5 örnek üzerinden göstermek, modelin pratikte nasıl davrandığını somutlaştırır.”

### 8.6 Final model + pkl kaydı
“Final modeli test skorlarıyla birlikte raporlar ve `models/best_model.pkl` olarak kaydederiz.”

---

## 9) Grafik altı mini kart şablonları (hızlı kopyala-yapıştır)

### 9.1 R² (Train vs Test)
- “Test R² yükseldikçe genelleme iyileşir.”
- “Train–test farkı küçükse overfitting riski düşüktür.”

### 9.2 Hata metrikleri (RMSE/MAE)
- “Düşük RMSE/MAE daha isabetli tahmin demektir.”
- “RMSE büyük hataları daha çok cezalandırır.”

### 9.3 Gerçek vs Tahmin
- “Noktalar diyagonale ne kadar yakınsa tahminler o kadar doğrudur.”
- “Diyagonalin üstü fazla, altı eksik tahmin bölgeleridir.”

---

## 10) Adım sonu change-log şablonu (final özet)

- **Bu adımda yapılanlar**:
  - ...
  - ...
- **Kararlar**:
  - “Şu nedenle ... tercih edildi.”
- **Risk/varsayım**:
  - ...
- **Sonraki adım**:
  - ...

---

## 11) Görsel/Metin Stil Rehberi (Notebook içi)

### 11.1 Mini yorum kartı uzunluğu
- 2–4 madde ideal.
- “Ne gördük?” + “Ne karar verdik?” mutlaka olsun.

### 11.2 Teknik dil seviyesi
- Hedef: teknik terimleri minimumda tutup, **iş anlamına** bağlamak.
- Zorunlu terimler (kısa açıklamasıyla): R², RMSE, CV, tuning, leakage.

### 11.3 Uyarı (⚠️) kullanımı
- “Overfitting riski” / “yüksek train–cv farkı” gibi yerlerde **tek bir sembol** ile görünür kılın.
- Uyarı koyunca mutlaka “ne yapılır?” cümlesi ekleyin:
  - “Bu modeli ele / tuning’i küçült / daha basit model seç / daha fazla veri kontrolü.”

---

## 12) Deployment Ready (kullanım şablonu)

Bu bölüm, final modeli notebook dışına taşıyacağınız zaman (örn. Streamlit) için kısa “kopyala-yapıştır” metin ve akış verir.

### 12.1 Final model ne içeriyor?
- `models/best_model.pkl`: Preprocess (impute/scale/encode) + model birlikte (Pipeline).
- Beklenen çıktı: Yeni bir öğrenci kaydı için `Exam_Score` tahmini.

### 12.2 Nasıl kullanılır? (anlatı metni)
“Modeli `.pkl` olarak kaydetmemizin nedeni, aynı preprocessing adımlarını üretimde de **aynı şekilde** uygulayabilmektir. Böylece eğitimde gördüğümüz performansı gerçek kullanımda daha tutarlı şekilde koruruz.”

### 12.3 Minimal kullanım kontrol listesi
- “Aynı kolon adlarıyla input verdik mi?”
- “Eksik kolon varsa default/boş değer stratejimiz var mı?”
- “Tahmin aralığı mantıklı mı? (0–100 gibi domain kısıtı varsa kontrol)”

### 12.4 Risk notu (kısa)
“Model, eğitim verisinin dağılımına benzer öğrenci profillerinde daha güvenilir çalışır. Çok farklı profillerde skor sapması artabilir; bu durumda veri güncelleme ve yeniden eğitim gerekebilir.”
