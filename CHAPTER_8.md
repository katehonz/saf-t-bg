# Глава 8: Data Engineering — От хаоса към структурирани данни

## 8.1. Счетоводителят като Data Engineer

SAF-T трансформира счетоводството от "цифрова писане" в "данъчен ETL процес". Всяка фирма вече трябва да има **Data Pipeline**:

```
[Източници] → [Extract] → [Transform] → [Validate] → [Load] → [SAF-T Export]
     ↑            ↑            ↑            ↑           ↑           ↑
   ERP/CRM     API/SQL      Mapping      XSD         Local       НАП
   Excel       Files        Cleansing    Schema      DB         Portal
```

### Инструменталната кутия на модерния счетоводител

| Класическо счетоводство | Data Engineering подход |
|------------------------|------------------------|
| Ръчно въвеждане на фактури | OCR + автоматичен импорт |
| Excel таблици | Релационни бази данни |
| Печат на дневници | XML експорт |
| Ревизия на хартия | Логове и одитни следи |
| Месечен отчет | Real-time streaming |

## 8.2. Архитектура на данните за SAF-T

### Концептуален модел (ER Diagram)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  COMPANY    │────<│   ACCOUNT    │>────│ SAFT_ACCOUNT│
│  (Фирма)    │     │  (Сметка)    │     │ (НАП код)   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │
       │                   │
       ▼                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│COUNTERPART  │────<│JOURNAL_ENTRY │>────│ ENTRY_LINE  │
│(Контрагент) │     │(Счет. статия)│     │  (Ред)      │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  INVOICE    │     │   PAYMENT    │     │TAX_INFO     │
│ (Фактура)   │     │ (Плащане)    │     │  (ДДС)      │
└─────────────┘     └──────────────┘     └─────────────┘
```

### SurrealDB Schema (NoSQL + Graph)

```sql
DEFINE TABLE company SCHEMAFULL;
DEFINE FIELD name ON company TYPE string;
DEFINE FIELD eik ON company TYPE string ASSERT string::len($value) >= 9;
DEFINE FIELD vat_number ON company TYPE option<string>;
DEFINE FIELD currency ON company TYPE string DEFAULT 'BGN';
DEFINE FIELD tax_accounting_basis ON company TYPE string DEFAULT 'A';
DEFINE FIELD is_vat_registered ON company TYPE bool DEFAULT false;

DEFINE TABLE counterpart SCHEMAFULL;
DEFINE FIELD name ON counterpart TYPE string;
DEFINE FIELD eik ON counterpart TYPE option<string>;
DEFINE FIELD vat_number ON counterpart TYPE option<string>;
DEFINE FIELD country ON counterpart TYPE string DEFAULT 'BG';
DEFINE FIELD counterpart_type ON counterpart TYPE string 
    ASSERT $value IN ['customer', 'supplier', 'both'];

DEFINE TABLE account SCHEMAFULL;
DEFINE FIELD code ON account TYPE string;
DEFINE FIELD name ON account TYPE string;
DEFINE FIELD account_type ON account TYPE string 
    ASSERT $value IN ['Active', 'Passive', 'Bifunctional'];
DEFINE FIELD company_id ON account TYPE record<company>;
DEFINE FIELD saft_account_id ON account TYPE option<record<saft_account>>;

DEFINE TABLE saft_account SCHEMAFULL;
DEFINE FIELD code ON saft_account TYPE string;
DEFINE FIELD name ON saft_account TYPE string;
DEFINE FIELD account_type ON saft_account TYPE string;
DEFINE INDEX idx_saft_code ON saft_account FIELDS code UNIQUE;

DEFINE TABLE journal_entry SCHEMAFULL;
DEFINE FIELD company_id ON journal_entry TYPE record<company>;
DEFINE FIELD date ON journal_entry TYPE datetime;
DEFINE FIELD description ON journal_entry TYPE string;
DEFINE FIELD status ON journal_entry TYPE string DEFAULT 'DRAFT'
    ASSERT $value IN ['DRAFT', 'POSTED', 'REVERSED'];
DEFINE FIELD total_debit ON journal_entry TYPE decimal DEFAULT 0.00;
DEFINE FIELD total_credit ON journal_entry TYPE decimal DEFAULT 0.00;

DEFINE TABLE journal_entry_line SCHEMAFULL;
DEFINE FIELD journal_entry_id ON journal_entry_line TYPE record<journal_entry>;
DEFINE FIELD account_id ON journal_entry_line TYPE record<account>;
DEFINE FIELD counterpart_id ON journal_entry_line TYPE option<record<counterpart>>;
DEFINE FIELD debit ON journal_entry_line TYPE option<decimal>;
DEFINE FIELD credit ON journal_entry_line TYPE option<decimal>;
DEFINE FIELD description ON journal_entry_line TYPE option<string>;

DEFINE TABLE invoice SCHEMAFULL;
DEFINE FIELD company_id ON invoice TYPE record<company>;
DEFINE FIELD counterpart_id ON invoice TYPE record<counterpart>;
DEFINE FIELD invoice_type ON invoice TYPE string 
    ASSERT $value IN ['sales', 'purchase'];
DEFINE FIELD invoice_number ON invoice TYPE string;
DEFINE FIELD invoice_date ON invoice TYPE datetime;
DEFINE FIELD due_date ON invoice TYPE option<datetime>;
DEFINE FIELD subtotal ON invoice TYPE decimal;
DEFINE FIELD vat_amount ON invoice TYPE decimal DEFAULT 0.00;
DEFINE FIELD total ON invoice TYPE decimal;
DEFINE FIELD journal_entry_id ON invoice TYPE option<record<journal_entry>>;
```

## 8.3. Rust: Типобезопасен модел на данните

Rust е идеален за SAF-T, защото компилаторът гарантира коректност на данните **преди** да стартирате програмата.

```rust
use serde::{Deserialize, Serialize};
use rust_decimal::Decimal;
use chrono::NaiveDate;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AccountType {
    Active,
    Passive,
    Bifunctional,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EntryStatus {
    Draft,
    Posted,
    Reversed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InvoiceType {
    Sales,
    Purchase,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CounterpartType {
    Customer,
    Supplier,
    Both,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Company {
    pub id: String,
    pub name: String,
    pub eik: String,
    pub vat_number: Option<String>,
    pub currency: String,
    pub tax_accounting_basis: String,
    pub is_vat_registered: bool,
    pub country: String,
    pub region: Option<String>,
    pub street_name: Option<String>,
    pub building_number: Option<String>,
    pub city: Option<String>,
    pub postal_code: Option<String>,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub software_id: String,
    pub software_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SaftAccount {
    pub code: String,
    pub name: String,
    pub account_type: AccountType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Account {
    pub id: String,
    pub code: String,
    pub name: String,
    pub account_type: AccountType,
    pub company_id: String,
    pub saft_account_id: Option<String>,
    pub opening_balance: Option<Decimal>,
    pub closing_balance: Option<Decimal>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Counterpart {
    pub id: String,
    pub name: String,
    pub eik: Option<String>,
    pub vat_number: Option<String>,
    pub country: String,
    pub counterpart_type: CounterpartType,
    pub street_name: Option<String>,
    pub building_number: Option<String>,
    pub city: Option<String>,
    pub postal_code: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JournalEntryLine {
    pub id: String,
    pub account_id: String,
    pub account_code: String,
    pub counterpart_id: Option<String>,
    pub debit: Option<Decimal>,
    pub credit: Option<Decimal>,
    pub description: String,
    pub tax_code: Option<String>,
    pub tax_base: Option<Decimal>,
    pub tax_amount: Option<Decimal>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JournalEntry {
    pub id: String,
    pub company_id: String,
    pub entry_number: String,
    pub date: NaiveDate,
    pub gl_posting_date: NaiveDate,
    pub description: String,
    pub status: EntryStatus,
    pub journal_type: String,
    pub source_id: Option<String>,
    pub lines: Vec<JournalEntryLine>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub total_debit: Option<Decimal>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub total_credit: Option<Decimal>,
}

impl JournalEntry {
    pub fn calculate_totals(&mut self) {
        let debit: Decimal = self.lines.iter()
            .filter_map(|l| l.debit)
            .sum();
        let credit: Decimal = self.lines.iter()
            .filter_map(|l| l.credit)
            .sum();
        self.total_debit = Some(debit);
        self.total_credit = Some(credit);
    }
    
    pub fn is_balanced(&self) -> bool {
        match (self.total_debit, self.total_credit) {
            (Some(d), Some(c)) => (d - c).abs() < Decimal::new(1, 2),
            _ => false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvoiceLine {
    pub product_code: String,
    pub product_description: String,
    pub quantity: Decimal,
    pub unit_price: Decimal,
    pub uom: String,
    pub line_total: Decimal,
    pub tax_code: String,
    pub tax_percentage: Decimal,
    pub tax_amount: Decimal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Invoice {
    pub id: String,
    pub company_id: String,
    pub counterpart_id: String,
    pub invoice_type: InvoiceType,
    pub invoice_number: String,
    pub invoice_date: NaiveDate,
    pub due_date: Option<NaiveDate>,
    pub lines: Vec<InvoiceLine>,
    pub subtotal: Decimal,
    pub vat_amount: Decimal,
    pub total: Decimal,
    pub journal_entry_id: Option<String>,
}

#[derive(Debug, Clone)]
pub struct SaftExportData {
    pub company: Company,
    pub accounts: Vec<Account>,
    pub saft_accounts: Vec<SaftAccount>,
    pub counterparts: Vec<Counterpart>,
    pub journal_entries: Vec<JournalEntry>,
    pub invoices: Vec<Invoice>,
    pub period_start: NaiveDate,
    pub period_end: NaiveDate,
    pub report_type: SaftReportType,
}

#[derive(Debug, Clone)]
pub enum SaftReportType {
    Monthly,
    OnDemand,
    Annual,
}
```

## 8.4. Python: Data Wrangling и анализ

Python е незаменим за почистване и анализ на данни преди експорт.

### Data Cleansing Pipeline

```python
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import date
import re

@dataclass
class CounterpartData:
    name: str
    eik: Optional[str]
    vat_number: Optional[str]
    country: str

@dataclass
class AccountMapping:
    local_code: str
    saft_code: str
    name: str
    account_type: str

class SaftDataCleaner:
    UOM_MAPPING = {
        'бр': 'C62', 'бр.': 'C62', 'бройки': 'C62', 'брой': 'C62',
        'кг': 'KGM', 'килограм': 'KGM', 'килограми': 'KGM', 'кг.': 'KGM',
        'л': 'LTR', 'литър': 'LTR', 'литра': 'LTR', 'литри': 'LTR',
        'м': 'MTR', 'метър': 'MTR', 'метра': 'MTR', 'метри': 'MTR',
        'м2': 'MTK', 'кв.м': 'MTK', 'кв. м': 'MTK',
        'м3': 'MTQ', 'куб.м': 'MTQ', 'куб. м': 'MTQ',
        'т': 'TNE', 'тон': 'TNE', 'тона': 'TNE',
        'ч': 'HUR', 'час': 'HUR', 'часа': 'HUR',
        'дк': 'DZN', 'дузина': 'DZN', 'дузини': 'DZN',
        'пакет': 'PA', 'пакети': 'PA',
        'кутия': 'BX', 'кутии': 'BX', 'кашон': 'CT', 'кашони': 'CT',
    }
    
    EU_COUNTRIES = [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
    ]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def clean_eik(self, eik: str) -> Optional[str]:
        if not eik or pd.isna(eik):
            return None
        cleaned = re.sub(r'[^0-9]', '', str(eik))
        if len(cleaned) == 9 or len(cleaned) == 13:
            return cleaned
        self.warnings.append(f"Невалиден ЕИК: {eik} (очаквани 9 или 13 цифри)")
        return None
    
    def clean_vat_number(self, vat: str, country: str = 'BG') -> Optional[str]:
        if not vat or pd.isna(vat):
            return None
        cleaned = re.sub(r'[^0-9A-Za-z]', '', str(vat).upper())
        if cleaned.startswith(country):
            cleaned = cleaned[len(country):]
        if country == 'BG' and len(cleaned) not in [9, 10]:
            self.warnings.append(f"Невалиден BG ДДС номер: {vat}")
            return None
        return cleaned
    
    def generate_saft_counterpart_id(
        self, 
        eik: Optional[str], 
        vat_number: Optional[str], 
        country: str
    ) -> str:
        if country == 'BG' or country == '':
            if eik:
                return f"10{eik}"
        if vat_number and country in self.EU_COUNTRIES and country != 'BG':
            return f"11{country}{vat_number}"
        if vat_number:
            return f"12{country}{vat_number}"
        if eik and country != 'BG':
            return f"13{eik}"
        return "15000000000"
    
    def normalize_uom(self, uom: str) -> str:
        if not uom or pd.isna(uom):
            return 'C62'
        key = str(uom).lower().strip()
        return self.UOM_MAPPING.get(key, 'C62')
    
    def round_decimal(self, value: float, places: int = 2) -> Decimal:
        d = Decimal(str(value))
        return d.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
    
    def validate_journal_balance(
        self, 
        df: pd.DataFrame, 
        debit_col: str = 'debit', 
        credit_col: str = 'credit'
    ) -> Dict:
        total_debit = df[debit_col].sum()
        total_credit = df[credit_col].sum()
        diff = abs(total_debit - total_credit)
        
        return {
            'total_debit': total_debit,
            'total_credit': total_credit,
            'difference': diff,
            'is_balanced': diff < 0.01,
            'balanced': diff < 0.01
        }

class CounterpartImporter:
    def __init__(self, cleaner: SaftDataCleaner):
        self.cleaner = cleaner
    
    def import_from_excel(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        required = ['name', 'country']
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Липсват колони: {missing}")
        
        df['eik_clean'] = df['eik'].apply(self.cleaner.clean_eik)
        df['vat_clean'] = df.apply(
            lambda r: self.cleaner.clean_vat_number(
                r.get('vat_number', ''), r['country']
            ), axis=1
        )
        df['saft_id'] = df.apply(
            lambda r: self.cleaner.generate_saft_counterpart_id(
                r['eik_clean'], r['vat_clean'], r['country']
            ), axis=1
        )
        
        missing_id = df[df['saft_id'] == '15000000000']
        if not missing_id.empty:
            self.cleaner.warnings.append(
                f"{len(missing_id)} контрагенти без идентификатор"
            )
        
        return df
    
    def import_from_nap_registry(self, eik_list: List[str]) -> pd.DataFrame:
        results = []
        for eik in eik_list:
            result = self._query_nap_registry(eik)
            results.append(result)
        return pd.DataFrame(results)
    
    def _query_nap_registry(self, eik: str) -> Dict:
        return {
            'eik': eik,
            'name': 'Търсене в регистър...',
            'status': 'active'
        }

class AccountMapper:
    STANDARD_MAPPING = {
        '101': '101', '102': '102', '104': '104',
        '201': '201', '202': '202', '203': '203', '204': '204',
        '301': '301', '302': '302', '303': '303', '304': '304',
        '401': '401', '411': '411', '412': '412', '421': '421',
        '501': '501', '502': '502', '503': '503',
        '601': '601', '602': '602', '603': '603', '604': '604',
        '701': '701', '702': '702', '703': '703', '704': '704',
    }
    
    def __init__(self):
        self.custom_mapping: Dict[str, str] = {}
    
    def auto_map(self, local_code: str) -> str:
        base = local_code.split('.')[0][:3]
        if base in self.STANDARD_MAPPING:
            return self.STANDARD_MAPPING[base]
        if local_code in self.custom_mapping:
            return self.custom_mapping[local_code]
        return base
    
    def add_custom_mapping(self, local_code: str, saft_code: str):
        self.custom_mapping[local_code] = saft_code
    
    def export_mapping_report(self, accounts: List[str]) -> pd.DataFrame:
        data = []
        for acc in accounts:
            saft = self.auto_map(acc)
            data.append({
                'local_code': acc,
                'saft_code': saft,
                'auto_mapped': acc not in self.custom_mapping
            })
        return pd.DataFrame(data)

def process_journal_entries(df: pd.DataFrame) -> Dict:
    cleaner = SaftDataCleaner()
    
    df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
    df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
    
    validation = cleaner.validate_journal_balance(df)
    
    if not validation['is_balanced']:
        cleaner.errors.append(
            f"Небалансирани статии: разлика {validation['difference']:.2f}"
        )
    
    df['line_total'] = df['debit'] + df['credit']
    
    by_entry = df.groupby('entry_id').agg({
        'debit': 'sum',
        'credit': 'sum',
        'line_total': 'count'
    }).rename(columns={'line_total': 'line_count'})
    
    unbalanced = by_entry[
        abs(by_entry['debit'] - by_entry['credit']) > 0.01
    ]
    
    return {
        'validation': validation,
        'by_entry': by_entry,
        'unbalanced_entries': unbalanced,
        'errors': cleaner.errors,
        'warnings': cleaner.warnings
    }

def analyze_vat_reconciliation(
    sales_df: pd.DataFrame, 
    journal_df: pd.DataFrame
) -> Dict:
    sales_vat = sales_df['vat_amount'].sum()
    
    vat_accounts = ['453', '4531', '4532', '4533']
    journal_vat = journal_df[
        journal_df['account_code'].str.startswith(tuple(vat_accounts))
    ]['credit'].sum()
    
    diff = abs(sales_vat - journal_vat)
    
    return {
        'sales_vat_total': sales_vat,
        'journal_vat_total': journal_vat,
        'difference': diff,
        'reconciled': diff < 0.01,
        'status': 'OK' if diff < 0.01 else 'DISCREPANCY'
    }
```

## 8.5. SQL: Релационен подход за анализ

### Стандартен PostgreSQL Schema

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    eik VARCHAR(13) NOT NULL UNIQUE,
    vat_number VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'BGN',
    tax_accounting_basis VARCHAR(10) DEFAULT 'A',
    is_vat_registered BOOLEAN DEFAULT FALSE,
    country VARCHAR(2) DEFAULT 'BG',
    region VARCHAR(10),
    street_name VARCHAR(255),
    building_number VARCHAR(20),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    phone VARCHAR(50),
    email VARCHAR(255),
    software_id VARCHAR(50) DEFAULT 'BARABA',
    software_version VARCHAR(20) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saft_accounts (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('Active', 'Passive', 'Bifunctional')),
    section INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    saft_account_code VARCHAR(10) REFERENCES saft_accounts(code),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, code)
);

CREATE INDEX idx_accounts_saft ON accounts(saft_account_code);
CREATE INDEX idx_accounts_company ON accounts(company_id);

CREATE TABLE counterparts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    eik VARCHAR(20),
    vat_number VARCHAR(30),
    country VARCHAR(2) DEFAULT 'BG',
    counterpart_type VARCHAR(20) NOT NULL CHECK (counterpart_type IN ('customer', 'supplier', 'both')),
    street_name VARCHAR(255),
    building_number VARCHAR(20),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, COALESCE(eik, id::text))
);

CREATE INDEX idx_counterparts_eik ON counterparts(eik);
CREATE INDEX idx_counterparts_vat ON counterparts(vat_number);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    entry_number VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    gl_posting_date DATE NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'POSTED', 'REVERSED')),
    journal_type VARCHAR(20),
    source_id VARCHAR(50),
    system_entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_debit DECIMAL(18, 2) DEFAULT 0,
    total_credit DECIMAL(18, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, entry_number)
);

CREATE INDEX idx_journal_entries_date ON journal_entries(date);
CREATE INDEX idx_journal_entries_company ON journal_entries(company_id);

CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    line_number INT NOT NULL,
    account_id UUID NOT NULL REFERENCES accounts(id),
    account_code VARCHAR(50) NOT NULL,
    counterpart_id UUID REFERENCES counterparts(id),
    debit DECIMAL(18, 2),
    credit DECIMAL(18, 2),
    description TEXT,
    source_document_id VARCHAR(50),
    value_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_lines_entry ON journal_entry_lines(journal_entry_id);
CREATE INDEX idx_journal_lines_account ON journal_entry_lines(account_id);

CREATE TABLE tax_information (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_line_id UUID NOT NULL REFERENCES journal_entry_lines(id) ON DELETE CASCADE,
    tax_type VARCHAR(10) NOT NULL,
    tax_code VARCHAR(10) NOT NULL,
    tax_base DECIMAL(18, 2) NOT NULL,
    tax_percentage DECIMAL(5, 2) NOT NULL,
    tax_amount DECIMAL(18, 2) NOT NULL,
    country VARCHAR(2) DEFAULT 'BG',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    counterpart_id UUID NOT NULL REFERENCES counterparts(id),
    invoice_type VARCHAR(20) NOT NULL CHECK (invoice_type IN ('sales', 'purchase')),
    invoice_number VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    subtotal DECIMAL(18, 2) NOT NULL,
    vat_amount DECIMAL(18, 2) DEFAULT 0,
    total DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BGN',
    journal_entry_id UUID REFERENCES journal_entries(id),
    transaction_id VARCHAR(50),
    is_self_billing BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, invoice_type, invoice_number)
);

CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_counterpart ON invoices(counterpart_id);

CREATE TABLE invoice_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    line_number INT NOT NULL,
    product_code VARCHAR(50),
    product_description TEXT NOT NULL,
    quantity DECIMAL(18, 4) NOT NULL,
    unit_price DECIMAL(18, 4) NOT NULL,
    uom VARCHAR(10) NOT NULL,
    line_total DECIMAL(18, 2) NOT NULL,
    tax_code VARCHAR(10),
    tax_percentage DECIMAL(5, 2),
    tax_amount DECIMAL(18, 2),
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(18, 2) DEFAULT 0
);

CREATE INDEX idx_invoice_lines_invoice ON invoice_lines(invoice_id);
```

### Аналитични заявки за SAF-T

```sql
WITH account_balances AS (
    SELECT 
        a.id AS account_id,
        a.code AS local_code,
        a.name AS account_name,
        sa.code AS saft_code,
        sa.name AS saft_name,
        sa.account_type,
        COALESCE(SUM(CASE 
            WHEN jel.debit IS NOT NULL THEN jel.debit 
            ELSE 0 
        END), 0) AS total_debit,
        COALESCE(SUM(CASE 
            WHEN jel.credit IS NOT NULL THEN jel.credit 
            ELSE 0 
        END), 0) AS total_credit
    FROM accounts a
    LEFT JOIN saft_accounts sa ON a.saft_account_code = sa.code
    LEFT JOIN journal_entry_lines jel ON jel.account_id = a.id
    LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id 
        AND je.status = 'POSTED'
    WHERE a.company_id = $1
    GROUP BY a.id, a.code, a.name, sa.code, sa.name, sa.account_type
)
SELECT 
    saft_code,
    saft_name,
    account_type,
    SUM(total_debit) AS period_debit,
    SUM(total_credit) AS period_credit,
    SUM(total_debit) - SUM(total_credit) AS net_change
FROM account_balances
GROUP BY saft_code, saft_name, account_type
ORDER BY saft_code;

WITH counterpart_exposure AS (
    SELECT 
        c.id,
        c.name,
        c.eik,
        c.country,
        c.counterpart_type,
        COALESCE(SUM(jel.debit), 0) AS total_debit,
        COALESCE(SUM(jel.credit), 0) AS total_credit,
        COALESCE(SUM(jel.debit), 0) - COALESCE(SUM(jel.credit), 0) AS balance
    FROM counterparts c
    LEFT JOIN journal_entry_lines jel ON jel.counterpart_id = c.id
    LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id 
        AND je.status = 'POSTED'
    WHERE c.company_id = $1
    GROUP BY c.id, c.name, c.eik, c.country, c.counterpart_type
)
SELECT 
    name,
    eik,
    country,
    counterpart_type,
    balance,
    CASE 
        WHEN balance > 0 THEN 'Debit'
        WHEN balance < 0 THEN 'Credit'
        ELSE 'Zero'
    END AS balance_type,
    ABS(balance) AS exposure
FROM counterpart_exposure
ORDER BY ABS(balance) DESC
LIMIT 20;

SELECT 
    je.id,
    je.entry_number,
    je.date,
    je.total_debit,
    je.total_credit,
    je.total_debit - je.total_credit AS diff,
    CASE 
        WHEN ABS(je.total_debit - je.total_credit) < 0.01 THEN 'OK'
        ELSE 'UNBALANCED'
    END AS status
FROM journal_entries je
WHERE je.company_id = $1 
    AND je.status = 'POSTED'
    AND ABS(je.total_debit - je.total_credit) >= 0.01
ORDER BY ABS(je.total_debit - je.total_credit) DESC;

WITH sales_vat AS (
    SELECT 
        tax_code,
        tax_percentage,
        SUM(tax_base) AS total_base,
        SUM(tax_amount) AS total_vat
    FROM invoices i
    JOIN invoice_lines il ON il.invoice_id = i.id
    WHERE i.company_id = $1 
        AND i.invoice_type = 'sales'
        AND i.invoice_date BETWEEN $2 AND $3
    GROUP BY tax_code, tax_percentage
),
journal_vat AS (
    SELECT 
        ti.tax_code,
        ti.tax_percentage,
        SUM(ti.tax_base) AS total_base,
        SUM(ti.tax_amount) AS total_vat
    FROM tax_information ti
    JOIN journal_entry_lines jel ON jel.id = ti.journal_entry_line_id
    JOIN journal_entries je ON je.id = jel.journal_entry_id
    WHERE je.company_id = $1 
        AND je.date BETWEEN $2 AND $3
        AND je.status = 'POSTED'
    GROUP BY ti.tax_code, ti.tax_percentage
)
SELECT 
    COALESCE(s.tax_code, j.tax_code) AS tax_code,
    COALESCE(s.tax_percentage, j.tax_percentage) AS rate,
    COALESCE(s.total_base, 0) AS sales_base,
    COALESCE(j.total_base, 0) AS journal_base,
    COALESCE(s.total_base, 0) - COALESCE(j.total_base, 0) AS base_diff,
    COALESCE(s.total_vat, 0) AS sales_vat,
    COALESCE(j.total_vat, 0) AS journal_vat,
    COALESCE(s.total_vat, 0) - COALESCE(j.total_vat, 0) AS vat_diff
FROM sales_vat s
FULL OUTER JOIN journal_vat j ON s.tax_code = j.tax_code;

SELECT 
    c.id,
    c.name,
    c.eik,
    c.vat_number,
    c.country,
    COUNT(DISTINCT i.id) AS invoice_count,
    SUM(i.total) AS total_volume,
    MIN(i.invoice_date) AS first_transaction,
    MAX(i.invoice_date) AS last_transaction
FROM counterparts c
JOIN invoices i ON i.counterpart_id = c.id
WHERE i.company_id = $1
GROUP BY c.id, c.name, c.eik, c.vat_number, c.country
ORDER BY total_volume DESC;
```

## 8.6. Data Quality Framework

### Rust валидационен engine

```rust
use std::collections::HashMap;

pub struct ValidationError {
    pub code: String,
    pub message: String,
    pub severity: ValidationSeverity,
    pub entity_type: String,
    pub entity_id: String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ValidationSeverity {
    Error,
    Warning,
    Info,
}

pub struct SaftValidator {
    errors: Vec<ValidationError>,
}

impl SaftValidator {
    pub fn new() -> Self {
        Self { errors: Vec::new() }
    }
    
    pub fn validate_company(&mut self, company: &Company) -> bool {
        let mut valid = true;
        
        if company.eik.is_empty() {
            self.errors.push(ValidationError {
                code: "COMP001".into(),
                message: "Липсва ЕИК на фирмата".into(),
                severity: ValidationSeverity::Error,
                entity_type: "Company".into(),
                entity_id: company.id.clone(),
            });
            valid = false;
        }
        
        if company.eik.len() != 9 && company.eik.len() != 13 {
            self.errors.push(ValidationError {
                code: "COMP002".into(),
                message: format!("Невалидна дължина на ЕИК: {}", company.eik.len()),
                severity: ValidationSeverity::Error,
                entity_type: "Company".into(),
                entity_id: company.id.clone(),
            });
            valid = false;
        }
        
        if company.is_vat_registered && company.vat_number.is_none() {
            self.errors.push(ValidationError {
                code: "COMP003".into(),
                message: "Фирмата е регистрирана по ДДС, но няма ДДС номер".into(),
                severity: ValidationSeverity::Warning,
                entity_type: "Company".into(),
                entity_id: company.id.clone(),
            });
        }
        
        valid
    }
    
    pub fn validate_counterpart(&mut self, cp: &Counterpart) -> bool {
        let mut valid = true;
        
        if cp.eik.is_none() && cp.vat_number.is_none() {
            self.errors.push(ValidationError {
                code: "CP001".into(),
                message: format!("Контрагент '{}' няма ЕИК или ДДС номер", cp.name),
                severity: ValidationSeverity::Warning,
                entity_type: "Counterpart".into(),
                entity_id: cp.id.clone(),
            });
        }
        
        if let Some(ref eik) = cp.eik {
            if eik.len() != 9 && eik.len() != 13 {
                self.errors.push(ValidationError {
                    code: "CP002".into(),
                    message: format!("Невалиден ЕИК на контрагент: {}", eik),
                    severity: ValidationSeverity::Warning,
                    entity_type: "Counterpart".into(),
                    entity_id: cp.id.clone(),
                });
            }
        }
        
        valid
    }
    
    pub fn validate_journal_entry(&mut self, entry: &JournalEntry) -> bool {
        let mut valid = true;
        
        if entry.lines.is_empty() {
            self.errors.push(ValidationError {
                code: "JE001".into(),
                message: format!("Счетоводна статия {} няма редове", entry.entry_number),
                severity: ValidationSeverity::Error,
                entity_type: "JournalEntry".into(),
                entity_id: entry.id.clone(),
            });
            return false;
        }
        
        let total_debit: Decimal = entry.lines.iter()
            .filter_map(|l| l.debit)
            .sum();
        let total_credit: Decimal = entry.lines.iter()
            .filter_map(|l| l.credit)
            .sum();
        
        let diff = (total_debit - total_credit).abs();
        if diff > Decimal::new(1, 2) {
            self.errors.push(ValidationError {
                code: "JE002".into(),
                message: format!(
                    "Небалансирана статия {}: Дебит={}, Кредит={}, Разлика={}",
                    entry.entry_number, total_debit, total_credit, diff
                ),
                severity: ValidationSeverity::Error,
                entity_type: "JournalEntry".into(),
                entity_id: entry.id.clone(),
            });
            valid = false;
        }
        
        for (i, line) in entry.lines.iter().enumerate() {
            if line.debit.is_none() && line.credit.is_none() {
                self.errors.push(ValidationError {
                    code: "JE003".into(),
                    message: format!("Ред {} няма дебит или кредит", i + 1),
                    severity: ValidationSeverity::Error,
                    entity_type: "JournalEntryLine".into(),
                    entity_id: line.id.clone(),
                });
                valid = false;
            }
            
            if line.debit.is_some() && line.credit.is_some() {
                self.errors.push(ValidationError {
                    code: "JE004".into(),
                    message: format!("Ред {} има и дебит, и кредит", i + 1),
                    severity: ValidationSeverity::Warning,
                    entity_type: "JournalEntryLine".into(),
                    entity_id: line.id.clone(),
                });
            }
        }
        
        valid
    }
    
    pub fn validate_account_mapping(
        &mut self, 
        account: &Account, 
        saft_accounts: &HashMap<String, SaftAccount>
    ) -> bool {
        if let Some(ref saft_id) = account.saft_account_id {
            if !saft_accounts.contains_key(saft_id) {
                self.errors.push(ValidationError {
                    code: "ACC001".into(),
                    message: format!(
                        "Сметка {} сочи към несъществуващ SAF-T код: {}",
                        account.code, saft_id
                    ),
                    severity: ValidationSeverity::Error,
                    entity_type: "Account".into(),
                    entity_id: account.id.clone(),
                });
                return false;
            }
        } else {
            self.errors.push(ValidationError {
                code: "ACC002".into(),
                message: format!("Сметка {} няма SAF-T mapping", account.code),
                severity: ValidationSeverity::Warning,
                entity_type: "Account".into(),
                entity_id: account.id.clone(),
            });
        }
        true
    }
    
    pub fn validate_invoice(&mut self, invoice: &Invoice) -> bool {
        let mut valid = true;
        
        let calculated_subtotal: Decimal = invoice.lines.iter()
            .map(|l| l.line_total)
            .sum();
        
        if (calculated_subtotal - invoice.subtotal).abs() > Decimal::new(1, 2) {
            self.errors.push(ValidationError {
                code: "INV001".into(),
                message: format!(
                    "Фактура {}: сума на редове ({}) != subtotal ({})",
                    invoice.invoice_number, calculated_subtotal, invoice.subtotal
                ),
                severity: ValidationSeverity::Error,
                entity_type: "Invoice".into(),
                entity_id: invoice.id.clone(),
            });
            valid = false;
        }
        
        let calculated_vat: Decimal = invoice.lines.iter()
            .map(|l| l.tax_amount)
            .sum();
        
        if (calculated_vat - invoice.vat_amount).abs() > Decimal::new(1, 2) {
            self.errors.push(ValidationError {
                code: "INV002".into(),
                message: format!(
                    "Фактура {}: ДДС на редове ({}) != общо ДДС ({})",
                    invoice.invoice_number, calculated_vat, invoice.vat_amount
                ),
                severity: ValidationSeverity::Warning,
                entity_type: "Invoice".into(),
                entity_id: invoice.id.clone(),
            });
        }
        
        valid
    }
    
    pub fn validate_all(&mut self, data: &SaftExportData) -> SaftValidationReport {
        self.errors.clear();
        
        self.validate_company(&data.company);
        
        let saft_map: HashMap<String, SaftAccount> = data.saft_accounts.iter()
            .map(|a| (a.code.clone(), a.clone()))
            .collect();
        
        for acc in &data.accounts {
            self.validate_account_mapping(acc, &saft_map);
        }
        
        for cp in &data.counterparts {
            self.validate_counterpart(cp);
        }
        
        for entry in &data.journal_entries {
            self.validate_journal_entry(entry);
        }
        
        for inv in &data.invoices {
            self.validate_invoice(inv);
        }
        
        SaftValidationReport {
            is_valid: !self.errors.iter().any(|e| e.severity == ValidationSeverity::Error),
            error_count: self.errors.iter().filter(|e| e.severity == ValidationSeverity::Error).count(),
            warning_count: self.errors.iter().filter(|e| e.severity == ValidationSeverity::Warning).count(),
            errors: self.errors.clone(),
        }
    }
    
    pub fn get_errors(&self) -> &[ValidationError] {
        &self.errors
    }
}

#[derive(Debug)]
pub struct SaftValidationReport {
    pub is_valid: bool,
    pub error_count: usize,
    pub warning_count: usize,
    pub errors: Vec<ValidationError>,
}

impl SaftValidationReport {
    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(self).unwrap_or_default()
    }
}
```

## 8.7. ETL Pipeline с Python

```python
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ETLResult:
    success: bool
    records_processed: int
    records_failed: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0

class Extractor(ABC):
    @abstractmethod
    async def extract(self) -> List[Dict[str, Any]]:
        pass

class Transformer(ABC):
    @abstractmethod
    async def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

class Loader(ABC):
    @abstractmethod
    async def load(self, data: List[Dict[str, Any]]) -> int:
        pass

class ExcelExtractor(Extractor):
    def __init__(self, file_path: str, sheet_name: str = None):
        self.file_path = file_path
        self.sheet_name = sheet_name
    
    async def extract(self) -> List[Dict[str, Any]]:
        import pandas as pd
        logger.info(f"Extracting from {self.file_path}")
        
        if self.sheet_name:
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        else:
            df = pd.read_excel(self.file_path)
        
        df = df.where(pd.notnull(df), None)
        records = df.to_dict('records')
        logger.info(f"Extracted {len(records)} records")
        return records

class CounterpartTransformer(Transformer):
    def __init__(self, cleaner: 'SaftDataCleaner'):
        self.cleaner = cleaner
    
    async def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        
        for record in data:
            try:
                name = record.get('name') or record.get('ime') or record.get('наименование')
                if not name:
                    continue
                
                eik_raw = str(record.get('eik') or record.get('ЕИК') or '')
                vat_raw = str(record.get('vat_number') or record.get('ДДС_номер') or '')
                country = str(record.get('country') or record.get('държава') or 'BG').upper()
                
                eik_clean = self.cleaner.clean_eik(eik_raw)
                vat_clean = self.cleaner.clean_vat_number(vat_raw, country)
                saft_id = self.cleaner.generate_saft_counterpart_id(
                    eik_clean, vat_clean, country
                )
                
                transformed.append({
                    'name': name.strip(),
                    'eik': eik_clean,
                    'vat_number': vat_clean,
                    'country': country,
                    'saft_id': saft_id,
                    'counterpart_type': self._determine_type(record),
                    'street_name': record.get('street') or record.get('улица'),
                    'city': record.get('city') or record.get('град'),
                })
            except Exception as e:
                logger.warning(f"Transform error for record: {e}")
        
        return transformed
    
    def _determine_type(self, record: Dict) -> str:
        typ = record.get('type') or record.get('вид') or ''
        if 'доставчик' in typ.lower() or 'supplier' in typ.lower():
            return 'supplier'
        if 'клиент' in typ.lower() or 'customer' in typ.lower():
            return 'customer'
        return 'both'

class SurrealDBLoader(Loader):
    def __init__(self, connection_url: str, namespace: str, database: str):
        self.connection_url = connection_url
        self.namespace = namespace
        self.database = database
        self.client = None
    
    async def connect(self):
        import httpx
        self.client = httpx.AsyncClient(
            base_url=self.connection_url,
            headers={
                'surreal-ns': self.namespace,
                'surreal-db': self.database,
            }
        )
    
    async def load(self, data: List[Dict[str, Any]], table: str = 'counterpart') -> int:
        if not self.client:
            await self.connect()
        
        loaded = 0
        for record in data:
            try:
                query = f"CREATE {table} CONTENT {record}"
                response = await self.client.post('/sql', content=query)
                if response.status_code == 200:
                    loaded += 1
                else:
                    logger.warning(f"Load failed: {response.text}")
            except Exception as e:
                logger.error(f"Load error: {e}")
        
        return loaded

class ETLPipeline:
    def __init__(
        self, 
        extractor: Extractor, 
        transformer: Transformer, 
        loader: Loader
    ):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
    
    async def run(self) -> ETLResult:
        start_time = datetime.now()
        errors = []
        warnings = []
        
        try:
            raw_data = await self.extractor.extract()
            
            if not raw_data:
                return ETLResult(
                    success=False,
                    records_processed=0,
                    records_failed=0,
                    errors=["No data extracted"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            transformed = await self.transformer.transform(raw_data)
            
            if hasattr(self.transformer, 'cleaner'):
                warnings.extend(self.transformer.cleaner.warnings)
            
            loaded = await self.loader.load(transformed)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return ETLResult(
                success=True,
                records_processed=loaded,
                records_failed=len(transformed) - loaded,
                warnings=warnings,
                duration_seconds=duration
            )
        except Exception as e:
            errors.append(str(e))
            return ETLResult(
                success=False,
                records_processed=0,
                records_failed=0,
                errors=errors,
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )

async def run_counterpart_import(file_path: str, db_url: str):
    cleaner = SaftDataCleaner()
    
    pipeline = ETLPipeline(
        extractor=ExcelExtractor(file_path),
        transformer=CounterpartTransformer(cleaner),
        loader=SurrealDBLoader(db_url, 'production', 'accounting')
    )
    
    result = await pipeline.run()
    
    print(f"Success: {result.success}")
    print(f"Records: {result.records_processed}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    
    if result.warnings:
        print(f"Warnings: {len(result.warnings)}")
        for w in result.warnings[:5]:
            print(f"  - {w}")
    
    if result.errors:
        print(f"Errors: {result.errors}")
    
    return result

if __name__ == '__main__':
    asyncio.run(run_counterpart_import(
        'counterparts.xlsx',
        'http://localhost:8000'
    ))
```

## 8.8. Заключение

Data Engineering не е просто "техническа работа" — това е **новата грамотност** за счетоводителите. SAF-T изисква:

1. **Структурирано мислене** — данните не са просто числа, а релационни обекти
2. **Типова безопасност** — ЕИК е string с pattern, сума е decimal с precision
3. **Валидационна култура** — проверка преди изпращане, не след отхвърляне
4. **Pipeline манталитет** — extract → transform → validate → load → export

Счетоводителят, който разбира тези концепции, вече не е "оператор", а **архитект на данни**.
