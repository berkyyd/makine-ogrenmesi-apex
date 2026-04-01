# Anlatıcı Metin Şablonları (Geliştirici Rehberi)

Bu doküman, notebook’u geliştiren ekip için “rubrik uyumlu hikâye anlatımı” şablonları sağlar. Notebook içinde her grafiğin altında kısa yorum bulunur; bu şablonlar ise **neden yaptık / ne gördük / ne anlama geliyor / sonraki adım** dilini hızlı ve tutarlı üretmek içindir.

> Amaç: “Bu grafikte bu değeri elde ettik çünkü ...; GridSearch kullandık çünkü ...” gibi açıklamaları standartlaştırmak.

---

## 0) Terim Mini-Sözlüğü (kısa, kopyala-yapıştır)

- **CRISP-DM**: İş Anlayışı → Veri Anlayışı → Veri Hazırlama → Modelleme → Değerlendirme → Dağıtım. Projeyi bir hikâye gibi uçtan uca anlatma standardı.
- **Train/Test Split**: Modeli eğitmek ve genelleme performansını görmek için veriyi ayırma.
- **Cross-Validation (CV)**: Modelin farklı alt örneklemlerde tutarlı çalışıp çalışmadığını test etme (genelleme kontrolü).
- **GridSearchCV**: Hiperparametre optimizasyonu. Modelin “ayarlarını” sistematik arayarak en iyi kombinasyonu bulma.
- **Pipeline**: Preprocessing + model adımlarını tek bir nesnede birleştirip leakage riskini azaltan yapı.
- **Leakage (veri sızıntısı)**: Test bilgisinin eğitim sürecine yanlışlıkla karışması; performansı sahte yükseltir.
- **R²**: Açıklanan varyans oranı (yüksek daha iyi).
- **RMSE**: Hata büyüklüğünü karekök ölçer (düşük daha iyi).
- **MAE**: Ortalama mutlak hata (düşük daha iyi).
- **MAPE**: Yüzdesel hata (düşük daha iyi).

---

## 1) Proje Hikâyesi / İş Problemi Şablonu

### 1.1 Bağlam (gerçek dünya)
“Bir okul/kurum, öğrencilerin akademik başarısını artırmak için sınırlı kaynaklarla (etüt, mentorluk, rehberlik, ek materyal) doğru öğrencilere doğru zamanda müdahale etmek zorunda. Bu yüzden **sınav sonucunu etkileyen faktörleri** önceden görmek kritik.”

### 1.2 İş problemi
“Amaç, öğrencinin haftalık çalışma, devam, uyku, önceki skorlar ve çevresel faktörleri gibi girdilerle **Exam_Score**’u tahmin etmek ve aynı zamanda hangi faktörlerin daha etkili olduğunu bularak **aksiyon önerileri** üretmektir.”

### 1.3 Başarı kriteri
“Model performansını \(R^2\), RMSE, MAE, MAPE ile ölçüyoruz; hedef \(R^2\\ge 0.80\) ve hata metriklerinde iyileşme.”

---

## 2) Her Grafik İçin Mikro-Yorum Şablonu (3–6 cümle)

Bu şablonu her figür altına uyarlayın.

**Ne görüyoruz:**  
“Bu grafik, \(X\) değişkeninin \(Y\) üzerindeki dağılımını/ilişkisini gösteriyor. X ekseni ..., Y ekseni ...”

**Pattern:**  
“Grafikte şu pattern dikkat çekiyor: (trend/kümelenme/çarpıklık/aykırı değerler/segment farkı).”

**İş anlamı:**  
“Bu bulgu, gerçek dünyada şunu ima ediyor: ... (örn. belirli bir davranışın başarıyı artırması/azaltması).”

**Aksiyon / sonraki adım:**  
“Bu nedenle bir sonraki adımda şu kararı alıyoruz: (transform/encode/capping/impute/feature engineering/model seçimi).”

---

## 3) “Bu Grafiği Neden Yaptık?” Kalıp Cümleleri

- “Bu grafiği, hedef değişkenin dağılımının normaliteye ne kadar yakın olduğunu ve aykırı değer riskini görmek için ürettik.”
- “Bu grafiği, değişkenler arası doğrusal ilişki ve çoklu bağlantı (multicollinearity) ihtimalini değerlendirmek için kullandık.”
- “Bu grafiği, kategorik grupların hedef değişkende anlamlı fark yaratıp yaratmadığını görmek için yaptık.”
- “Bu grafiği, feature engineering sonrası yeni değişkenlerin hedefle ilişkisini ve bilgi katkısını kontrol etmek için ekledik.”

---

## 4) Univariate (Her Sütun) Şablonu

Her sütun için 2–5 cümlelik yorum.

- **Sütun & tipi:** “`{col}` {numeric/categorical} bir değişkendir.”
- **Dağılım:** “Dağılım {sağa/sola çarpık/çok tepeli/dar-geniş} görünüyor…”
- **Aykırılar:** “Aykırı değerler {var/yok}; olası nedeni …”
- **Hedef hipotezi:** “Bu değişkenin `Exam_Score` ile {pozitif/negatif} ilişki göstermesi beklenir çünkü …”
- **Karar:** “Bu yüzden {log/boxcox/binning/onehot/ordinal/impute/capping} uygulamayı planlıyoruz.”

---

## 5) Modelleme Anlatısı Şablonları

### 5.1 Neden 12+ model?
“Farklı model aileleri farklı veri yapılarını daha iyi yakalar. Bu yüzden lineer modeller, ağaç tabanlı yöntemler, ensemble’lar ve distance-based yaklaşımlar dahil 12+ algoritmayı aynı metriklerle kıyasladık.”

### 5.2 Neden CV?
“Tek bir train/test bölünmesi şans faktöründen etkilenebilir. 5-fold CV ile performansın farklı örneklemlerde stabil olup olmadığını test ederek genelleme riskini azaltıyoruz.”

### 5.3 Neden GridSearchCV?
“GridSearchCV bir hiperparametre optimizasyonudur. Modelin öğrenme kapasitesini ve genellemesini etkileyen ayarları sistematik şekilde tarayarak en iyi kombinasyonu bulur; böylece baseline’a göre daha optimal performans hedeflenir.”

### 5.4 Hata analizi (residual)
“Residual plot ve gerçek vs tahmin grafiği, modelin hangi aralıklarda sistematik hata yaptığını (bias) gösterir. Bu, feature engineering veya model seçimi için geri besleme sağlar.”

---

## 6) Adım Sonu Change-log (Geliştirici Notu) Şablonu

Her ana başlık sonunda (1,2,3...) 4–8 maddeyle özet.

- **Bu adımda yapılanlar**:\n  - ...\n  - ...
- **Kararlar**:\n  - “Şu nedenle ... tercih edildi.”
- **Riskler/varsayımlar**:\n  - ...
- **Sonraki adım**:\n  - ...
