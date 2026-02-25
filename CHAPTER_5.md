# Глава 5: Номенклатури и Счетоводни Кореспонденции — Логическият център

## 5.1. Какво са „Кореспонденции“ в света на SAF-T?
В класическото счетоводство кореспонденцията е връзката между две сметки (Дебит 601 / Кредит 301). В SAF-T обаче НАП иска да знае **защо** се случва това движение. За целта се използват т.нар. **Movement Types** (Типове движения).

Пример за номенклатура на НАП за склад (On Demand):
- **10** — Покупка
- **30** — Продажба
- **50** — Вътрешно преместване

## 5.2. Автоматизация на мапинга (The Mapping Engine)
За да не се налага счетоводителят ръчно да избира код за всяка хилядна фактура, в baraba.org използваме „Мапинг двигател“. Ето как изглежда логиката му, описана чрез **SurrealQL (NoSQL)**:

```surrealql
-- Дефинираме правило: Всяко движение от тип 'Продажба' 
-- автоматично кореспондира с определени сметки
DEFINE TABLE saft_correspondence SCHEMAFULL;
DEFINE FIELD movement_type ON saft_correspondence TYPE string; -- Код 30
DEFINE FIELD debit_account ON saft_correspondence TYPE record<account>; -- 411
DEFINE FIELD credit_account ON saft_correspondence TYPE record<account>; -- 702

-- Търсене на правилото чрез Graph Relation
SELECT ->rules_for_saft->(saft_account WHERE code = '702') 
FROM movement_type:sale;
```

**Счетоводният аспект:** Софтуерът трябва да знае, че ако изпишем стока с код „Продажба“, той трябва да потърси в SAF-T номенклатурата съответствието за приходи. Ако счетоводителят промени своята сметка 702 на 7021, мапингът в настройките трябва автоматично да се актуализира.

## 5.3. Настройки на фирмата (System Settings)
SAF-T изисква и много не-счетоводни настройки, които обаче променят XML структурата. 
Пример в **Rust** за управление на тези настройки:

```rust
#[derive(Serialize, Deserialize)]
pub struct SaftSettings {
    pub tax_accounting_basis: String, // 'A' за Търговски предприятия
    pub uom_map: HashMap<String, String>, // Локално 'бр.' -> SAF-T 'C62'
}

// В baraba.org проверяваме настройките преди експорт
pub fn validate_uom(local_unit: &str, settings: &SaftSettings) -> String {
    settings.uom_map.get(local_unit)
        .cloned()
        .unwrap_or_else(|| "C62".to_string()) // Fallback към 'Units'
}
```

## 5.4. Казусът с „Мерните единици“
Това е техническият кошмар на всеки счетоводител. Вие имате „кг“, „килограма“, „КГ.“. НАП признава само „KGM“. 
Тук идва ролята на **Python** за предварителна обработка на данни (Data Wrangling):

```python
# Python скрипт за уеднаквяване на мерни единици преди импорт в baraba.org
import pandas as pd

def clean_uom(value):
    mapping = {
        'кг': 'KGM',
        'бр': 'C62',
        'л': 'LTR'
    }
    return mapping.get(value.lower().strip(), 'C62')

df = pd.read_excel("sklad.xlsx")
df['SAFT_UOM'] = df['Merna_Edinica'].apply(clean_uom)
```

**Извод:** Номенклатурите не са просто списъци. Те са релационни масиви, които трябва да бъдат синхронизирани между вашата база данни и изискванията на НАП. Адвокатите виждат списъка, счетоводителят вижда работата, а програмистът вижда алгоритъма.
