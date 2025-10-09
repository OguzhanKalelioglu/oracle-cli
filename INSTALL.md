# Oracle CLI TUI - Kurulum Rehberi

## Sisteme Yükleme

### 1. Development Mode (Geliştirme için önerilir)

Projeyi development modunda yüklerseniz, kodda değişiklik yaptığınızda yeniden yüklemeye gerek kalmaz:

```bash
cd /Users/oguz-mac-mini/Documents/Cursor\ Projects/toad2025
pip install -e .
```

### 2. Normal Kurulum

Projeyi kalıcı olarak sisteme yüklemek için:

```bash
cd /Users/oguz-mac-mini/Documents/Cursor\ Projects/toad2025
pip install .
```

### 3. Virtual Environment ile Kurulum (Önerilir)

Sistem Python'unu kirletmemek için virtual environment kullanın:

```bash
# Virtual environment oluştur
cd /Users/oguz-mac-mini/Documents/Cursor\ Projects/toad2025
python3 -m venv .venv

# Aktive et
source .venv/bin/activate  # macOS/Linux
# veya
.venv\Scripts\activate  # Windows

# Yükle
pip install -e .
```

## Kullanım

Yükleme tamamlandıktan sonra herhangi bir terminalde şu komutları kullanabilirsiniz:

```bash
# TUI arayüzünü başlat (varsayılan davranış)
oracle-cli

# veya açıkça belirterek
oracle-cli tui

# Bağlantı bilgilerini kaydet
oracle-cli configure

# Tabloları listele
oracle-cli list-tables

# Tablo detaylarını göster
oracle-cli describe-table TABLO_ADI

# Tablo verilerini önizle
oracle-cli preview-table TABLO_ADI --limit 10

# Yardım
oracle-cli --help
```

## Kısayollar (TUI)

| Kısayol | Açıklama |
|---------|----------|
| **Ctrl+S** | Arama |
| **Ctrl+P** | Procedures |
| **Ctrl+K** | Packages |
| **Ctrl+E** | SQL Çalıştır |
| **R** | Yenile |
| **Q** | Çıkış |
| **ESC** | İptal |

## Kaldırma

```bash
pip uninstall oracle-cli-tui
```

## Sorun Giderme

### "oracle-cli komutu bulunamadı" hatası

Eğer yükleme sonrası komut bulunamazsa, Python'un scripts dizininin PATH'inizde olduğundan emin olun:

```bash
# Kurulum yerini kontrol et
pip show oracle-cli-tui

# Python scripts dizinini PATH'e ekle (macOS/Linux için ~/.zshrc veya ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Virtual environment içinde kurulum

Eğer virtual environment içinde kurduysanız, komutu çalıştırırken önce venv'i aktive etmelisiniz:

```bash
source .venv/bin/activate
oracle-cli  # Direkt TUI açılır
# veya
oracle-cli tui  # Aynı sonuç
```

