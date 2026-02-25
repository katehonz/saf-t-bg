# Дневник на промените (Changelog)

Всички съществени промени по книгата са документирани тук.

Форматът следва [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.3.0] — 2026-02-26

### Добавено
- `CHAPTER_0.md` — нова пролог глава „Генетични дефекти на масовия БГ софтуер"
- `SUMMARY.md` — резюме на всяка глава на български
- `CONTRIBUTING.md` — ръководство за принос на български
- `LICENSE` — MIT лиценз
- `.gitignore` — покритие за OS, редактори, Python, Rust, генерирани XML файлове
- Резюмета на всички глави в `README.md` таблицата

### Променено
- Ребрандиране: Doxius → baraba.org във всички файлове (10 файла, включително код примери)
- `DOXIUS` → `BARABA` в SoftwareID полета (SQL, SurrealDB, XML примери)
- `README.md` — коригиран git clone URL към `katehonz/saf-t-bg`
- `PLAN.md` — преструктуриран с таблица на глави, резюмета, премахнати `**НОВО**` тагове
- `FULL_BOOK.md` — вмъкната Глава 0 между Манифеста и Глава 1

### Премахнато
- `idea-1.md` — чернова от чат разговор, съдържанието интегрирано в Глава 0

## [0.2.0] — 2026-02-25

### Добавено
- `CHAPTER_8.md` — Data Engineering: ETL pipelines, SurrealDB schema, Rust модели, Python Data Wrangling, PostgreSQL schema, Data Quality Framework
- `CHAPTER_9.md` — SQL vs NoSQL: PostgreSQL vs SurrealDB, Graph relations, хибриден подход, performance optimization, benchmarking
- `CHAPTER_10.md` — Тестване и QA: 5 слоя валидация (XSD, Data Type, Referential Integrity, Cross-module, Business Logic), Pytest, CI/CD
- `CHAPTER_11.md` — Реални казуси: търговец на едро, производител с ВОП, холдинг, ЕТ
- `APPENDICES.md` — таблица на 360 сметки, данъчни кодове, мерни единици, типове движения, SAF-T ID префикси, примерен XML, FAQ

### Променено
- `FULL_BOOK.md` — добавени обобщения на нови глави 8-11 и приложения
- `PLAN.md` — обновен с нови глави

## [0.1.0] — 2026-02-25

### Добавено
- `MANIFESTO.md` — манифест: защо SAF-T не е за адвокати
- `CHAPTER_1.md` — Счетоводителят като Data Engineer
- `CHAPTER_2.md` — XML и Namespaces за счетоводители
- `CHAPTER_3.md` — Счетоводни номенклатури и двойният сметкоплан
- `CHAPTER_4.md` — Материални запаси: On-Demand отчет
- `CHAPTER_5.md` — Номенклатури и кореспонденции
- `CHAPTER_6.md` — Техническа реализация: Rust + SurrealDB (~1300 реда)
- `CHAPTER_7.md` — Епилог: Краят на търговията със страх
- `FULL_BOOK.md` — пълен текст на книгата
- `PLAN.md` — план и структура
- `README.md` — начална страница на проекта
- `saf-t-med.jpg` — корица на книгата
