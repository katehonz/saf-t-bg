# Глава 6: Техническа Реализация — Кодът зад отчетите

## 6.1. Защо Rust + SurrealDB? (Архитектурен избор)

Когато генерирате XML файл за НАП, грешка в типа на данните означава отхвърляне. Rust не позволява такива грешки по време на компилация. SurrealDB дава гъвкавост на NoSQL с мощта на релационни заявки.

**Стекът на baraba.org:**
- **Dioxus 0.7** — fullstack framework (SSR + WASM), едно Rust приложение за сървър и клиент
- **SurrealDB** — документна база данни с Graph заявки и вградени типове
- **quick_xml** — streaming XML writer, който гарантира encoding и escaping
- **Server Functions** (`#[server]`) — кодът за генерация живее на сървъра, клиентът вижда само UI

## 6.2. Моделът на данните (Реален код)

Ето как изглежда `Company` структурата в baraba.org — тя носи всички полета, необходими за SAF-T Header:

```rust
// src/models.rs — Реален код от baraba.org
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Company {
    pub id: Option<String>,
    pub name: String,
    pub eik: String,
    pub vat_number: Option<String>,
    pub address: Option<String>,
    pub city: Option<String>,
    pub country: Option<String>,
    pub post_code: Option<String>,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub manager_name: Option<String>,
    pub street_name: Option<String>,        // SAF-T: отделно улица
    pub building_number: Option<String>,     // SAF-T: отделно номер
    pub region: Option<String>,             // SAF-T: BG-22, BG-23...
    pub tax_accounting_basis: String,       // "A" за начисления
    pub software_company_name: Option<String>, // "baraba.org"
    pub software_id: Option<String>,        // "BARABA"
    pub software_version: Option<String>,   // "1.0"
    pub currency: String,                   // "BGN" или "EUR"
    pub is_vat_registered: bool,
    pub is_part_of_group: Option<String>,
    // ... и още 20 полета
}
```

**Забележете:** Полета като `street_name`, `building_number`, `region` съществуват **специално за SAF-T** — в класическия адрес те са едно поле, но XML схемата ги иска разделени.

## 6.3. Генериране на SAF-T ID (Префикс логика)

Най-критичната функция — как ЕИК/ДДС номер се трансформира в SAF-T идентификатор:

```rust
// src/pages/saft_export.rs — Реален код от baraba.org
fn generate_saft_id(cp: &Counterpart) -> String {
    let country = cp.country.as_deref().unwrap_or("BG");

    // Префикс 10: Български ЕИК
    if let Some(ref eik) = cp.eik {
        if !eik.is_empty() && (country == "BG" || country.is_empty()) {
            return format!("10{}", eik);
        }
    }

    // Префикс 11: ЕС ДДС номер (не-BG)
    if let Some(ref vat) = cp.vat_number {
        if !vat.is_empty() {
            let eu_countries = ["AT","BE","BG","HR","CY","CZ","DK","EE",
                "FI","FR","DE","GR","HU","IE","IT","LV","LT","LU",
                "MT","NL","PL","PT","RO","SK","SI","ES","SE"];
            if eu_countries.contains(&country) && country != "BG" {
                return format!("11{}{}", country, vat);
            }
            // Префикс 12: Извън ЕС
            return format!("12{}{}", country, vat);
        }
    }

    // Префикс 13: Само ЕИК, чуждестранен
    if let Some(ref eik) = cp.eik {
        if !eik.is_empty() {
            return format!("13{}", eik);
        }
    }

    // Префикс 15: Fallback
    format!("15{}", cp.id.as_deref().unwrap_or("0"))
}
```

**Счетоводният аспект:** Тази функция решава проблема с различните типове контрагенти автоматично. Счетоводителят въвежда ЕИК и държава — софтуерът избира правилния SAF-T префикс.

## 6.4. XML генераторът (Streaming подход)

baraba.org не строи XML дърво в паметта. Използваме **streaming writer** — пишем елемент по елемент, което работи за файлове от всякакъв размер:

```rust
// src/pages/saft_export.rs — Реален код от baraba.org

// Помощни функции — елегантни и безопасни
fn w<W: std::io::Write>(writer: &mut quick_xml::Writer<W>,
    name: &str, text: &str) -> Result<(), quick_xml::Error>
{
    use quick_xml::events::{BytesEnd, BytesStart, BytesText, Event};
    writer.write_event(Event::Start(BytesStart::new(name)))?;
    writer.write_event(Event::Text(BytesText::new(text)))?; // auto-escapes &, <, >
    writer.write_event(Event::End(BytesEnd::new(name)))?;
    Ok(())
}

fn open<W: std::io::Write>(writer: &mut quick_xml::Writer<W>,
    name: &str) -> Result<(), quick_xml::Error>
{
    writer.write_event(Event::Start(BytesStart::new(name)))
}

fn close<W: std::io::Write>(writer: &mut quick_xml::Writer<W>,
    name: &str) -> Result<(), quick_xml::Error>
{
    writer.write_event(Event::End(BytesEnd::new(name)))
}
```

С тези 3 функции се изгражда целият 1300-редов SAF-T генератор:

```rust
fn build_saft_xml(data: &SaftData) -> Result<String, quick_xml::Error> {
    use quick_xml::Writer;
    let mut x = Writer::new_with_indent(Cursor::new(Vec::new()), b' ', 2);

    // XML декларация
    x.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), None)))?;

    // Root с namespace на НАП
    let mut root = BytesStart::new("nsSAFT:AuditFile");
    root.push_attribute(("xmlns:nsSAFT", "mf:nra:dgti:dxxxx:declaration:v1"));
    x.write_event(Event::Start(root))?;

    build_header(&mut x, data)?;          // Заглавна част
    build_master_files(&mut x, data)?;     // Сметки, клиенти, доставчици
    build_general_ledger_entries(&mut x, data)?; // Главна книга
    build_source_documents(&mut x, data)?; // Фактури, плащания

    close(&mut x, "nsSAFT:AuditFile")?;
    Ok(String::from_utf8_lossy(&x.into_inner().into_inner()).to_string())
}
```

## 6.5. Двойната идентификация на сметките (Мапинг в действие)

Ето как baraba.org реализира мапването `AccountID` ↔ `TaxpayerAccountID` в реално време:

```rust
// При генериране на всеки ред в Главната книга
for (i, line) in je.lines.iter().enumerate() {
    // Търсим сметката на потребителя
    let standard_code = if let Some(acc) = data.accounts.iter()
        .find(|a| a.id.as_deref() == Some(&line.account_id))
    {
        // Ако има SAF-T mapping — вземаме кода от НАП номенклатурата
        if let Some(ref saft_id) = acc.saft_account_id {
            data.saft_accounts.iter()
                .find(|s| s.id.as_deref() == Some(saft_id))
                .map(|s| s.code.as_str())    // "411" от НАП
                .unwrap_or(&acc.code)         // fallback
        } else {
            &acc.code  // Ако няма mapping — ползваме вашия код
        }
    } else {
        line.account_code.as_deref().unwrap_or(&line.account_id)
    };

    // В XML: AccountID = код на НАП, TaxpayerAccountID = ваш код
    w(x, "nsSAFT:AccountID", standard_code)?;
    // TaxpayerAccountID се попълва от acc.code
}
```

**Счетоводният аспект:** Вашата сметка `411.01.002` отива в `TaxpayerAccountID`. Стандартната `411` отива в `AccountID`. Софтуерът прави превода автоматично, стига сметката да има mapping в настройките.

## 6.6. Трите лица на SAF-T (Monthly / OnDemand / Annual)

baraba.org генерира различен XML в зависимост от типа отчет:

```rust
// Избор на MasterFiles секция според типа
let master_element = match data.report_type.as_str() {
    "annual"   => "nsSAFT:MasterFilesAnnual",    // ДМА + амортизации
    "ondemand" => "nsSAFT:MasterFilesOnDemand",   // Складови наличности
    _          => "nsSAFT:MasterFilesMonthly",     // Стандартен месечен
};

open(x, master_element)?;
build_gl_accounts(x, data)?;    // Сметки — винаги
build_customers(x, data)?;      // Клиенти — винаги
build_suppliers(x, data)?;      // Доставчици — винаги
build_tax_table(x)?;            // Данъчни кодове — винаги
build_uom_table(x)?;            // Мерни единици — винаги

if data.report_type == "ondemand" {
    build_physical_stock(x, data)?;    // Само при On Demand
}
if data.report_type == "annual" {
    build_assets(x, data)?;            // Само при годишен
}
close(x, master_element)?;
```

## 6.7. SurrealDB: Заявките за събиране на данните

Преди генерацията, baraba.org събира всичко необходимо с няколко заявки:

```rust
// Журнални статии С вложени редове (subquery)
let je_sql = format!(
    "SELECT *, \
       (SELECT * FROM journal_entry_line WHERE journal_entry_id = $parent.id) AS lines \
     FROM journal_entry \
     WHERE company_id = '{}' AND status = 'POSTED' AND date CONTAINS '{}' \
     ORDER BY date ASC",
    company_id, period  // period = "2026-01"
);
let entries: Vec<JournalEntry> = query(&je_sql).await?
    .into_iter()
    .filter_map(|v| serde_json::from_value(v).ok())
    .collect();
```

**В класически SQL** това би изисквало JOIN + GROUP BY. В SurrealDB вложената заявка (`$parent.id`) директно връща редовете вътре в записа.

А ето и слоят за комуникация с базата (`src/db.rs`):

```rust
// HTTP клиент към SurrealDB с retry логика
pub async fn query(sql: &str) -> Result<Vec<Value>> {
    let resp = HTTP
        .post(&CONFIG.url)           // http://127.0.0.1:8000/sql
        .basic_auth(&CONFIG.user, Some(&CONFIG.pass))
        .header("surreal-ns", &CONFIG.ns)  // namespace: test
        .header("surreal-db", &CONFIG.db)  // database: test
        .body(sql.to_string())
        .send()
        .await?;
    // ... parse JSON response, handle errors, retry on 5xx
}
```

## 6.8. Валидацията преди експорт (Pre-flight check)

baraba.org не чака НАП да отхвърли файла. Валидацията се случва **преди** генерацията:

```rust
#[server]
async fn validate_saft_export(company_id: String, year: i32, month: i32)
    -> Result<SaftValidationResult, ServerFnError>
{
    let mut errors = Vec::new();
    let mut warnings = Vec::new();

    // 1. Проверка на фирмени данни
    let company: Company = /* fetch from DB */;
    if company.eik.is_empty() {
        errors.push("Компанията няма попълнен ЕИК".into());
    }
    if !company.is_vat_registered {
        warnings.push("Компанията не е регистрирана по ДДС".into());
    }

    // 2. Проверка на сметки без SAF-T mapping
    let accounts: Vec<Account> = /* fetch active accounts */;
    let without_saft = accounts.iter()
        .filter(|a| a.saft_account_id.is_none()).count();
    if without_saft > 0 {
        warnings.push(format!("{} сметки нямат SAF-T mapping", without_saft));
    }

    // 3. Проверка на контрагенти без ЕИК
    let counterparts: Vec<Counterpart> = /* fetch all */;
    let cp_no_id = counterparts.iter()
        .filter(|c| c.eik.is_none() && c.vat_number.is_none()).count();
    if cp_no_id > 0 {
        warnings.push(format!("{} контрагенти нямат ЕИК или ДДС номер", cp_no_id));
    }

    Ok(SaftValidationResult {
        valid: errors.is_empty(),
        errors,
        warnings,
        journal_entries_count: entries.len() as i32,
        invoices_count: invoices.len() as i32,
        counterparts_count: counterparts.len() as i32,
        accounts_count: accounts.len() as i32,
    })
}
```

Потребителят вижда резултата в UI — грешки в червено, предупреждения в жълто, статистика в карти.

## 6.9. Данъчната таблица (Hardcoded номенклатура)

Данъчните кодове са стандартни за всички фирми — вградени са директно в кода:

```rust
fn build_tax_table<W: std::io::Write>(x: &mut quick_xml::Writer<W>)
    -> Result<(), quick_xml::Error>
{
    open(x, "nsSAFT:TaxTable")?;
    open(x, "nsSAFT:TaxTableEntry")?;
    w(x, "nsSAFT:TaxType", "100010")?;     // ДДС
    w(x, "nsSAFT:Description", "ДДС")?;

    let codes = [
        ("100211", "20.00", "ДО със ставка 20%"),
        ("100213",  "9.00", "ДО със ставка 9%"),
        ("100214",  "0.00", "ДО със ставка 0%"),
        ("100219",  "0.00", "Освободени доставки"),
    ];
    for (code, rate, desc) in &codes {
        open(x, "nsSAFT:TaxCodeDetails")?;
        w(x, "nsSAFT:TaxCode", code)?;
        w(x, "nsSAFT:Description", desc)?;
        w(x, "nsSAFT:TaxPercentage", rate)?;
        close(x, "nsSAFT:TaxCodeDetails")?;
    }
    close(x, "nsSAFT:TaxTableEntry")?;
    close(x, "nsSAFT:TaxTable")?;
    Ok(())
}
```

## 6.10. Python за одит на генерирания XML

Преди да „запечатате" месечния отчет, можете да пуснете одитни скриптове. Ето пример как Python проверява дали ДДС-то съответства на данъчната основа:

```python
import xml.etree.ElementTree as ET

def audit_saft_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'ns': 'mf:nra:dgti:dxxxx:declaration:v1'}

    # Проверка 1: Баланс на Главната книга
    total_d = float(root.find('.//ns:GeneralLedgerEntries/ns:TotalDebit', ns).text)
    total_c = float(root.find('.//ns:GeneralLedgerEntries/ns:TotalCredit', ns).text)
    if abs(total_d - total_c) > 0.01:
        print(f"ГРЕШКА: Дебит ({total_d}) != Кредит ({total_c})")

    # Проверка 2: ДДС съответствие
    for line in root.findall('.//ns:TransactionLine', ns):
        tax_info = line.find('.//ns:TaxInformation', ns)
        if tax_info is not None:
            base = float(tax_info.find('ns:TaxBase', ns).text)
            rate = float(tax_info.find('ns:TaxPercentage', ns).text)
            vat = float(tax_info.find('.//ns:TaxAmount/ns:Amount', ns).text)
            expected = round(base * rate / 100, 2)
            if abs(expected - vat) > 0.01:
                rec_id = line.find('ns:RecordID', ns).text
                print(f"ГРЕШКА: Ред {rec_id}: база {base} × {rate}% = {expected}, но ДДС = {vat}")

    # Проверка 3: Всяка фактура има TransactionID
    for inv in root.findall('.//ns:Invoice', ns):
        tid = inv.find('ns:TransactionID', ns)
        if tid is None or not tid.text:
            inv_no = inv.find('ns:InvoiceNo', ns).text
            print(f"ПРЕДУПРЕЖДЕНИЕ: Фактура {inv_no} няма TransactionID")

audit_saft_xml("output_saft.xml")
```

## 6.11. Миграциите (Идемпотентна инициализация)

baraba.org използва SurrealDB миграции, които се изпълняват автоматично при стартиране:

```sql
-- migrations/001_init.surql — 360 сметки от НАП номенклатурата
DEFINE TABLE saft_account SCHEMAFULL;
DEFINE FIELD OVERWRITE code ON saft_account TYPE string;
DEFINE FIELD OVERWRITE name ON saft_account TYPE string;
DEFINE FIELD OVERWRITE account_type ON saft_account TYPE string;
DEFINE INDEX idx_saft_code ON saft_account FIELDS code UNIQUE;

-- Seed: Зареждане на стандартните сметки
UPSERT saft_account:101 SET code = '101', name = 'Основен капитал', account_type = 'Liability';
UPSERT saft_account:411 SET code = '411', name = 'Клиенти', account_type = 'Bifunctional';
UPSERT saft_account:702 SET code = '702', name = 'Приходи от стоки', account_type = 'Sale';
-- ... общо 360 реда
```

**Ключов урок:** Използваме `UPSERT` (не `CREATE`), за да може миграцията да се изпълни многократно без дубликати. `DEFINE FIELD OVERWRITE` гарантира идемпотентност.

## 6.12. Бъдещето: Автоматизация през API

SAF-T не е крайна цел, а само етап. Софтуерът на бъдещето ще предава данните към НАП чрез защитени API канали в реално време. Това ще премахне нуждата от месечни „кампании" по подаване на файлове.

**Извод за техническите лица:** Целият SAF-T генератор на baraba.org е ~1300 реда Rust код. Той покрива Monthly, On Demand и Annual отчети. Всичко е type-safe, streaming, и валидирано преди генерация. Ако вашият софтуер е изграден върху „кръпки", SAF-T ще ги разкрие.
