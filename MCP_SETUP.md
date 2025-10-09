# Oracle-CLI MCP Server Kurulum Rehberi

Oracle-CLI'yi **MCP (Model Context Protocol)** sunucusu olarak kullanarak Cursor, VS Code, Claude Desktop gibi AI araçlarının Oracle veritabanınıza erişmesini sağlayabilirsiniz.

## 📋 Ön Gereksinimler

1. **Oracle-CLI kurulu olmalı:**
   ```bash
   pipx install git+https://github.com/oguzhankalelioglu/oracle-cli.git
   ```

2. **Veritabanı bağlantısı yapılandırılmış olmalı:**
   ```bash
   oracle-cli configure
   ```

## 🚀 Kurulum Adımları

### 1. MCP Sunucusunu Test Etme

Önce MCP sunucusunun çalıştığını test edin:

```bash
oracle-cli mcp
```

Çalışıyorsa, sunucu stdio üzerinden JSON-RPC mesajları beklemeye başlar.

### 2. Cursor IDE Entegrasyonu

#### Adım 1: Cursor MCP Ayarlarını Açın

1. Cursor IDE'yi açın
2. `Cmd/Ctrl + Shift + P` ile komut paletini açın
3. "MCP: Edit MCP Settings" yazın ve seçin
4. Veya manuel olarak: `~/.cursor/mcp.json` dosyasını düzenleyin

#### Adım 2: Konfigürasyon Ekleyin

`mcp.json` dosyasına aşağıdaki konfigürasyonu ekleyin:

**Yöntem 1: Önceden Yapılandırılmış Config Kullanma**
```json
{
  "mcpServers": {
    "oracle-cli": {
      "command": "oracle-cli",
      "args": ["mcp"]
    }
  }
}
```

Bu yöntemde `oracle-cli configure` ile kaydettiğiniz bilgileri kullanır.

**Yöntem 2: Environment Variables ile**
```json
{
  "mcpServers": {
    "oracle-cli": {
      "command": "oracle-cli",
      "args": ["mcp"],
      "env": {
        "ORACLE_USER": "hr",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "localhost:1521/XEPDB1",
        "ORACLE_SCHEMA": "HR"
      }
    }
  }
}
```

#### Adım 3: Cursor'u Yeniden Başlatın

Konfigürasyon değişikliklerinin etkili olması için Cursor'u yeniden başlatın.

### 3. VS Code Entegrasyonu (Cline Extension ile)

#### Adım 1: Cline Extension'ı Kurun

1. VS Code'da Extensions'a gidin
2. "Cline" extension'ını arayın ve kurun

#### Adım 2: MCP Ayarlarını Yapılandırın

1. VS Code Settings'e gidin (`Cmd/Ctrl + ,`)
2. "MCP" arayın
3. "Edit in settings.json" seçeneğini seçin
4. Aşağıdaki konfigürasyonu ekleyin:

```json
{
  "cline.mcpServers": {
    "oracle-cli": {
      "command": "oracle-cli",
      "args": ["mcp"]
    }
  }
}
```

### 4. Claude Desktop Entegrasyonu

#### Adım 1: Claude Desktop Config Dosyasını Bulun

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

#### Adım 2: Konfigürasyon Ekleyin

Config dosyasını düzenleyin:

```json
{
  "mcpServers": {
    "oracle-cli": {
      "command": "oracle-cli",
      "args": ["mcp"]
    }
  }
}
```

#### Adım 3: Claude Desktop'ı Yeniden Başlatın

## 🛠️ Kullanılabilir MCP Araçları

Oracle-CLI MCP sunucusu şu araçları sunar:

### 1. `list_tables`
Şemadaki tüm tabloları listeler.

**Parametreler:**
- `schema` (opsiyonel): Şema adı

**Örnek kullanım (AI'da):**
```
"List all tables in the HR schema"
```

### 2. `describe_table`
Tablo yapısını gösterir (kolonlar, tipler, constraints).

**Parametreler:**
- `table_name` (gerekli): Tablo adı
- `schema` (opsiyonel): Şema adı

**Örnek kullanım:**
```
"Describe the EMPLOYEES table structure"
```

### 3. `query_table`
Tablodan örnek veri getirir.

**Parametreler:**
- `table_name` (gerekli): Tablo adı
- `limit` (opsiyonel, varsayılan: 10): Maksimum satır sayısı
- `schema` (opsiyonel): Şema adı

**Örnek kullanım:**
```
"Show me first 5 rows from EMPLOYEES table"
```

### 4. `execute_sql`
Özel SQL sorgusu çalıştırır (sadece SELECT).

**Parametreler:**
- `query` (gerekli): SQL sorgusu
- `limit` (opsiyonel, varsayılan: 100): Maksimum satır sayısı

**Örnek kullanım:**
```
"Execute: SELECT * FROM EMPLOYEES WHERE DEPARTMENT_ID = 10"
```

### 5. `list_objects`
PL/SQL objelerini listeler.

**Parametreler:**
- `object_type` (gerekli): PACKAGE, PROCEDURE, FUNCTION, PACKAGE BODY
- `schema` (opsiyonel): Şema adı

**Örnek kullanım:**
```
"List all packages in the schema"
```

### 6. `get_source`
PL/SQL objesinin kaynak kodunu getirir.

**Parametreler:**
- `object_name` (gerekli): Obje adı
- `object_type` (gerekli): Obje tipi
- `schema` (opsiyonel): Şema adı

**Örnek kullanım:**
```
"Show me the source code of GET_EMPLOYEE procedure"
```

### 7. `get_table_stats`
Tablo istatistiklerini getirir (satır sayısı, boyut).

**Parametreler:**
- `table_name` (gerekli): Tablo adı
- `schema` (opsiyonel): Şema adı

**Örnek kullanım:**
```
"What are the statistics for EMPLOYEES table?"
```

## 💡 Kullanım Örnekleri

MCP sunucusu çalıştıktan sonra AI asistanınıza şu tür sorular sorabilirsiniz:

### Tablo Keşfi
```
"List all tables in my Oracle database"
"Show me the structure of EMPLOYEES table"
"What are the primary keys in DEPARTMENTS table?"
```

### Veri Sorgulama
```
"Show me first 10 rows from EMPLOYEES table"
"Find all employees in department 20"
"What is the average salary by department?"
```

### PL/SQL İnceleme
```
"Show me all packages in the schema"
"Display the source code of CALCULATE_BONUS procedure"
"What functions are available in the schema?"
```

### Analiz ve İstatistikler
```
"What are the statistics for SALES table?"
"How many rows are in EMPLOYEES table?"
"Show table size and storage information"
```

## 🔧 Sorun Giderme

### MCP Sunucusu Başlamıyor

**Hata:** `Connection details not found`

**Çözüm:**
```bash
oracle-cli configure
```
Bağlantı bilgilerinizi yeniden girin.

### Bağlantı Hatası

**Hata:** `Connection failed: ORA-12541`

**Çözüm:**
- DSN'in doğru olduğundan emin olun
- Oracle veritabanının çalıştığını kontrol edin
- Firewall ayarlarını kontrol edin

### Cursor/VS Code MCP Sunucusunu Görmüyor

**Çözüm:**
1. `mcp.json` dosyasının doğru konumda olduğundan emin olun
2. JSON syntax'ının geçerli olduğunu kontrol edin
3. IDE'yi tamamen kapatıp yeniden açın
4. MCP sunucusunun yolunun doğru olduğunu kontrol edin:
   ```bash
   which oracle-cli  # macOS/Linux
   where oracle-cli  # Windows
   ```

### Debug Modu

MCP sunucusunu debug modunda çalıştırmak için:

```bash
oracle-cli mcp 2> mcp-debug.log
```

Bu, hata mesajlarını `mcp-debug.log` dosyasına yazar.

## 🔒 Güvenlik Notları

1. **Şifre Güvenliği:**
   - `oracle-cli configure` kullanarak şifreleri güvenli şekilde saklayın
   - MCP config dosyasına şifre yazmaktan kaçının
   - Config dosyalarını version control'e eklemeyin

2. **SQL İnjection Koruması:**
   - MCP sunucusu sadece SELECT sorgularına izin verir
   - Parametrize sorgular kullanılır
   - Tüm girdiler normalize edilir

3. **Erişim Kontrolü:**
   - MCP sunucusu sadece lokal (stdio) erişime izin verir
   - Network üzerinden erişim yoktur
   - Kullanıcı izinleri Oracle veritabanı tarafından kontrol edilir

## 📚 Ek Kaynaklar

- [MCP Specification](https://modelcontextprotocol.io/)
- [Cursor MCP Documentation](https://docs.cursor.com/mcp)
- [Oracle-CLI GitHub](https://github.com/oguzhankalelioglu/oracle-cli)

## 🆘 Yardım

Sorun yaşıyorsanız:

1. [GitHub Issues](https://github.com/oguzhankalelioglu/oracle-cli/issues)
2. [Discussions](https://github.com/oguzhankalelioglu/oracle-cli/discussions)

---

**Not:** MCP özelliği experimental olup, gelecek sürümlerde değişiklik gösterebilir.
