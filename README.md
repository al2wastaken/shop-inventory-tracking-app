# Mağaza Stok Takip Sistemi

Modern, kullanıcı dostu ve MongoDB destekli bir mağaza stok ve satış takip uygulaması. Python ve `customtkinter` kullanılarak geliştirilmiş karanlık tema (dark mode) odaklı, şık bir masaüstü arayüzüne sahiptir.

## ✨ Özellikler

- **Ürün Yönetimi:** Ürün ekleme, silme, düzenleme ve listeleme işlemleri.
- **Kategori Sistemi:** Sınırsız kategori oluşturma ve ürünleri kategorilere ayırma.
- **Stok Takibi:** Güncel stok durumu takibi ve belirlediğiniz eşiğe göre otomatik "Kritik Stok" uyarıları.
- **Satış İşlemleri:** Hızlı ve kolay satış yapabilme, stokların otomatik düşmesi.
- **Gelişmiş Arama:** Ürün adı, fiyat aralığı ve kategoriye göre dinamik arama filtreleri.
- **Detaylı Raporlama Sistemi:**
  - Genel Özet (Toplam ürün, kategori, güncel hesaplanan toplam stok değeri)
  - Satış İstatistikleri (Toplam satış geliri, satılan ürün adedi, en çok satılan ürün)
  - Fiyat Analizi (En pahalı ve en ucuz ürünler)
  - Kategori Dağılımı ve kategorilere göre gelir analizleri
  - Kritik stok uyarıları
- **Güçlü Doğrulama:** Regex ile gelişmiş ürün adı doğrulaması.
- **Mock Data Desteği:** Test amaçlı tek tıkla sanal veri oluşturabilme.
- **Esnek Kullanım:** Hem görsel arayüz (`main.py`) hem de terminal arayüzü (`terminal.py`) seçeneği.

## 🛠️ Kullanılan Teknolojiler
- **Python 3.x**
- **CustomTkinter:** Modern ve karanlık tema destekli grafik arayüz kütüphanesi.
- **PyMongo:** MongoDB veritabanı sürücüsü.
- **MongoDB:** Yüksek performanslı NoSQL veritabanı.
- **PyInstaller:** Uygulamayı tek bir `.exe` dosyası haline getirmek için.
- Diğer gereksinimler: `python-dotenv`

## ⚙️ Kurulum ve Çalıştırma

### 1. Gereksinimler
- [Python](https://www.python.org/) yüklü olmalıdır.
- **MongoDB** veritabanına sahip olmalısınız. (`.env` doyasında uzak bir bağlantı adresi tanımlayabilirsiniz).

### 2. Projeyi Klonlama ve Kurulum
Adımları terminalinizde veya PowerShell üzerinden çalıştırabilirsiniz:

```bash
# Projeyi bilgisayarınıza indirin
git clone https://github.com/al2wastaken/shop-inventory-tracking-app.git
cd shop-inventory-tracking-app

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

### 3. Çevresel Değişkenler (.env)
Proje dizininde yer alan `.env.example` dosyasının adını `.env` olarak değiştirerek veritabanı bağlantı bilgilerinizi ayarlayabilirsiniz. Varsayılan ayarlar çalışma ortamı için genellikle yeterlidir.
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=shop_inventory
```

### 4. Uygulamayı Başlatma
Görsel (GUI) arayüz ile başlatmak için:
```bash
python main.py
```

Terminal arayüzü ile başlatmak için:
```bash
python terminal.py
```

## 🏗️ Proje Mimarisi (Modüler Yapı)

- `main.py` -> CustomTkinter tabanlı Ana GUI uygulaması.
- `terminal.py` -> Komut satırı tabanlı alternatif uygulama arayüzü.
- `models.py` -> Uygulamanın veri katmanı. MongoDB bağlantıları, Model sınıfları (`Product`, `Category`, `Sale`) ve Manager sınıfları (`ProductManager`, `CategoryManager`, `SaleManager`, `ReportManager`) burada bulunur.
- `logo.ico` -> Uygulama ve pencere simgesi.
- `requirements.txt` -> Proje kütüphane bağımlılıkları.

## 📦 Uygulamayı Derleme (.exe Yapma)
Uygulamayı Python yüklü olmayan Windows bilgisayarlarda çalıştırmak üzere tek bir `.exe` dosyası haline getirebilirsiniz. Bunun için:

```bash
python -m PyInstaller --onefile --windowed --icon=logo.ico --add-data "logo.ico;." --add-data ".env;." --name "MagazaStokTakip" main.py
```
İşlem tamamlandığında çalıştırılabilir uygulama `dist` klasörü içerisinde yer alacaktır.
