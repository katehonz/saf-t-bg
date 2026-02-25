# SAF-T в България: Счетоводен и Технически Наръчник за Практици

*Как да превърнем хаоса от данни в структуриран XML, без да се налага да ставаме юристи.*

---

## Структура на книгата

### Основни файлове
- `FULL_BOOK.md` — Пълният текст на книгата (всички глави)
- `PLAN.md` — Този план и структура
- `MANIFESTO.md` — Манифест и философия

### Глави (отделни файлове)
- `CHAPTER_1.md` — Новата реалност: Счетоводителят като Data Engineer
- `CHAPTER_2.md` — Техническият скелет: XML и namespaces
- `CHAPTER_3.md` — Счетоводни Номенклатури и Двойният Сметкоплан
- `CHAPTER_4.md` — Материални запаси: On-Demand отчет
- `CHAPTER_5.md` — Номенклатури и Кореспонденции
- `CHAPTER_6.md` — Техническа Реализация: Rust + SurrealDB
- `CHAPTER_7.md` — Епилог: Краят на търговията със страх
- `CHAPTER_8.md` — **НОВО** Data Engineering: ETL pipelines, типове данни
- `CHAPTER_9.md` — **НОВО** SQL vs NoSQL: PostgreSQL и SurrealDB
- `CHAPTER_10.md` — **НОВО** Тестване и QA: 5 слоя валидация
- `CHAPTER_11.md` — **НОВО** Реални казуси от практиката
- `APPENDICES.md` — **НОВО** Приложения: таблици, примери, FAQ

### Ресурсни файлове (SAFT_BG/)
- `BG_SAFT_Schema_V_1.0.1.xsd` — Официална XSD схема на НАП
- `VS_SAMPLE_AuditFile_Monthly_V_1.0.1.xml` — Примерен месечен файл
- `VS_SAMPLE_AuditFile_Annual_V_1.0.xml` — Примерен годишен файл
- `VS_SAMPLE_AuditFile_OnDemand_V_1.0.xml` — Примерен On-Demand файл
- `Structure_Definition_V_1.0.1.xlsx` — Дефиниция на структурата
- `SAF-T_BG_Format_Reporting+(Приложение+3).pdf` — Официална документация

---

## Обобщение на съдържанието

### Част I: Философията зад SAF-T
**Глава 1**
- История на SAF-T (OECD модел)
- Българската адаптация v1.0.1
- Счетоводителят като Data Engineer
- Data Cleansing процес

### Част II: Техническият скелет
**Глава 2**
- XML основи за счетоводители
- Namespaces (nsSAFT:)
- Структура: Header, MasterFiles, GeneralLedgerEntries, SourceDocuments
- XSD валидация

### Част III: Счетоводни Номенклатури
**Глава 3**
- Национален сметкоплан (360 сметки)
- AccountID vs TaxpayerAccountID
- Мапване (mapping) на сметки
- TaxTable данъчни кодове

### Част IV: Склад и Материални запаси
**Глава 4**
- Monthly vs OnDemand vs Annual
- PhysicalStock секция
- MovementOfGoods
- UOM конверсии

### Част V: Кореспонденции
**Глава 5**
- Movement Types
- Автоматизация на мапинга
- SurrealQL примери
- Python data wrangling

### Част VI: Техническа Реализация
**Глава 6**
- Rust + SurrealDB архитектура
- Company, Account, JournalEntry модели
- XML streaming generator
- SAF-T ID префикси логика
- Pre-flight validation
- Python одитни скриптове

### Част VII: Епилог
**Глава 7**
- Краят на търговията със страх
- Счетоводителят на бъдещето

### Част VIII: **НОВО** Data Engineering
**Глава 8**
- ETL pipeline архитектура
- SurrealDB schema (DEFINE TABLE)
- Rust типобезопасен модел
- Python data wrangling класове
- PostgreSQL schema
- Data Quality Framework
- Async ETL pipeline

### Част IX: **НОВО** SQL vs NoSQL
**Глава 9**
- PostgreSQL vs SurrealDB сравнение
- Пълен SQL schema с triggers/views
- SurrealDB Graph relations
- Хибриден подход
- Performance optimization
- Benchmarking

### Част X: **НОВО** Тестване и QA
**Глава 10**
- 5 слоя валидация
- XSD валидация (Rust/Python)
- Data Type validation
- Referential Integrity
- Cross-module Consistency
- Business Logic validation
- Pytest framework
- CI/CD integration

### Част XI: **НОВО** Реални казуси
**Глава 11**
- Търговец на едро (дедупликация на продукти)
- Производител с ВОП (VIES, ДДС класификация)
- Холдинг (консолидация, елиминации)
- Едноличен търговец (опростен pipeline)

### Приложения
**APPENDICES.md**
- А: Таблица на 360 SAF-T сметки
- Б: Данъчни кодове (TaxTable)
- В: Мерни единици (UOM)
- Г: Типове движения (On Demand)
- Д: Префикси за SAF-T ID
- Е: Примерен пълен XML
- Ж: Rust boilerplate код
- З: FAQ

---

## Технологичен стек

| Категория | Технологии |
|-----------|-----------|
| Backend | Rust (Dioxus 0.7, quick_xml) |
| Database | SurrealDB, PostgreSQL |
| Data Processing | Python (pandas, lxml) |
| Validation | XSD, Pytest |
| Deployment | Docker, GitHub Actions |

---

## Целева аудитория

1. **Счетоводители** — разбират счетоводството, искат да разберат технологията
2. **Data Engineers** — разбират технологията, искат да разберат счетоводството
3. **Software Developers** — изграждат SAF-T имплементации
4. **IT Managers** — планират SAF-T интеграция в организации

---

*Допълнения за разписване с помощта на AI:*
- *Приложения с реални примери (XML снипети срещу счетоводни Т-сметки).*
- *Таблици за мапване на най-често срещаните сметки.*
- *Казуси от практиката (напр. фирма с клонове, ВОП доставки).*
