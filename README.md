<p align="center">
  <img src="saf-t-med.jpg" alt="SAF-T Bulgaria Book Cover" width="600">
</p>

<h1 align="center">SAF-T в България</h1>
<h3 align="center">Счетоводен и Технически Наръчник за Практици</h3>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Language-Rust-orange?style=for-the-badge&logo=rust" alt="Rust"></a>
  <a href="#"><img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Database-SurrealDB-ff00ff?style=for-the-badge" alt="SurrealDB"></a>
  <a href="#"><img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL"></a>
  <a href="#"><img src="https://img.shields.io/badge/Format-XML-green?style=for-the-badge" alt="XML"></a>
</p>

<p align="center">
  <i>„SAF-T няма да бъде спечелен в съда. Той ще бъде спечелен в базата данни.“</i>
</p>

---

## Защо тази книга?

Тази книга е създадена от екипа на **Doxius** като отговор на нарастващия шум от „правни анализи“ на един чисто технически стандарт. Тук ще намерите:

- **Не тълкуване на закони**, а алгоритми и структури от данни
- **Реален код** на Rust, Python, SQL и NoSQL
- **Практически счетоводни решения** от гледна точка на Data Engineer

---

## Съдържание

### Книга

| Файл | Описание |
|------|----------|
| [**FULL_BOOK.md**](FULL_BOOK.md) | Пълният текст на книгата (всички глави) |
| [**MANIFESTO.md**](MANIFESTO.md) | Манифест: Защо SAF-T не е за адвокати |

### Основни глави

| Глава | Файл | Съдържание |
|-------|------|------------|
| 1 | [CHAPTER_1.md](CHAPTER_1.md) | Счетоводителят като Data Engineer |
| 2 | [CHAPTER_2.md](CHAPTER_2.md) | Техническият скелет: XML и namespaces |
| 3 | [CHAPTER_3.md](CHAPTER_3.md) | Счетоводни номенклатури и двойният сметкоплан |
| 4 | [CHAPTER_4.md](CHAPTER_4.md) | Материални запаси: On-Demand отчет |
| 5 | [CHAPTER_5.md](CHAPTER_5.md) | Номенклатури и кореспонденции |
| 6 | [CHAPTER_6.md](CHAPTER_6.md) | Техническа реализация: Rust + SurrealDB |
| 7 | [CHAPTER_7.md](CHAPTER_7.md) | Епилог: Краят на търговията със страх |

### Разширени глави

| Глава | Файл | Съдържание |
|-------|------|------------|
| 8 | [CHAPTER_8.md](CHAPTER_8.md) | **Data Engineering**: ETL pipelines, типове данни, validation |
| 9 | [CHAPTER_9.md](CHAPTER_9.md) | **SQL vs NoSQL**: PostgreSQL и SurrealDB в сравнение |
| 10 | [CHAPTER_10.md](CHAPTER_10.md) | **Тестване и QA**: 5 слоя валидация, pytest, CI/CD |
| 11 | [CHAPTER_11.md](CHAPTER_11.md) | **Реални казуси**: търговец, производител, холдинг, ЕТ |

### Приложения

| Файл | Съдържание |
|------|------------|
| [APPENDICES.md](APPENDICES.md) | Таблица на 360 сметки, данъчни кодове, UOM, SAF-T ID префикси, пълен XML пример, FAQ |

---

## Технологичен стек

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFT-T BOOK STACK                        │
├─────────────────────────────────────────────────────────────┤
│  Backend    │  Rust (Dioxus 0.7, quick_xml, serde)          │
│  Database   │  SurrealDB, PostgreSQL                        │
│  Processing │  Python (pandas, lxml)                        │
│  Validation │  XSD, Pytest, GitHub Actions                  │
│  Schema     │  BG_SAFT_Schema_V_1.0.1.xsd (НАП)             │
└─────────────────────────────────────────────────────────────┘
```

### Примери за код

| Език | Употреба |
|------|----------|
| **Rust** | Типобезопасни модели, XML streaming generator, validation engine |
| **Python** | Data wrangling, pandas pipelines, XSD validation, VIES integration |
| **SQL** | PostgreSQL schema, triggers, views, аналитични заявки |
| **NoSQL** | SurrealDB DEFINE TABLE, Graph relations, SurrealQL |

---

## Ресурсни файлове

В папката `SAFT_BG/` ще намерите официалните ресурси от НАП:

| Файл | Описание |
|------|----------|
| `BG_SAFT_Schema_V_1.0.1.xsd` | Официална XSD схема |
| `VS_SAMPLE_AuditFile_Monthly_V_1.0.1.xml` | Примерен месечен файл |
| `VS_SAMPLE_AuditFile_Annual_V_1.0.xml` | Примерен годишен файл |
| `VS_SAMPLE_AuditFile_OnDemand_V_1.0.xml` | Примерен On-Demand файл |

---

## За кого е тази книга?

| Аудитория | Какво ще научат |
|-----------|-----------------|
| **Счетоводители** | XML структура, мапинг, номенклатури |
| **Data Engineers** | Счетоводна логика, двойно записване |
| **Разработчици** | SAF-T имплементация, Rust/Python код |
| **IT Мениджъри** | Архитектура, интеграция, CI/CD |

---

## Бърз старт

```bash
git clone https://github.com/your-repo/su-doxius.git
cd su-doxius/SAFT-BOOK
```

Започнете с [FULL_BOOK.md](FULL_BOOK.md) или с [MANIFESTO.md](MANIFESTO.md).

---

## Контрибуция

Тази книга е „жив“ документ. Ако сте счетоводител или разработчик и имате:

- Интересен казус със SAF-T
- Подобрения в кода
- Поправки в текста

Отворете **Issue** или **Pull Request**.

---

## Лиценз

MIT License — свободна за използване и разпространение.

---

<p align="center">
  <i>Издадено от авторите на</i> <b><a href="https://github.com/dimgigov/su-doxius">Doxius</a></b>
</p>
