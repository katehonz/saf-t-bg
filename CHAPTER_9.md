# Глава 9: SQL vs NoSQL — Избор на база данни за SAF-T

## 9.1. Дилемата на архитектора

При изграждане на счетоводна система за SAF-T стоим пред класическия избор:

| Критерий | SQL (PostgreSQL) | NoSQL (SurrealDB/MongoDB) |
|----------|------------------|---------------------------|
| Схема | Строга, предварителна | Гъвкава, еволюираща |
| Транзакции | ACID гаранции | Различни нива |
| Сложни заявки | JOIN, подзаявки | Aggregation pipeline |
| Скалируемост | Вертикална + хоризонтална | Предимно хоризонтална |
| Типове данни | Релационни | Документи, графове |
| Крива на учене | Позната на повечето | Нужда от нови умения |

**За SAF-T препоръчваме:** SurrealDB защото комбинира гъвкавостта на NoSQL с мощта на релационни заявки и GRAPH traversal.

## 9.2. PostgreSQL: Релационният стандарт

### Пълен схематичен модел

```sql
CREATE TYPE account_type_enum AS ENUM ('Active', 'Passive', 'Bifunctional');
CREATE TYPE entry_status_enum AS ENUM ('DRAFT', 'POSTED', 'REVERSED');
CREATE TYPE invoice_type_enum AS ENUM ('sales', 'purchase');
CREATE TYPE counterpart_type_enum AS ENUM ('customer', 'supplier', 'both');

CREATE TABLE tax_codes (
    code VARCHAR(10) PRIMARY KEY,
    tax_type VARCHAR(10) NOT NULL,
    description VARCHAR(255) NOT NULL,
    percentage DECIMAL(5, 2) NOT NULL,
    country VARCHAR(2) DEFAULT 'BG',
    effective_from DATE,
    expires_on DATE,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO tax_codes (code, tax_type, description, percentage) VALUES
    ('100211', '100010', 'Облагаеми доставки 20%', 20.00),
    ('100213', '100010', 'Облагаеми доставки 9%', 9.00),
    ('100214', '100010', 'Облагаеми доставки 0%', 0.00),
    ('100219', '100010', 'Освободени доставки', 0.00);

CREATE TABLE uom_codes (
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    description_bg VARCHAR(255)
);

INSERT INTO uom_codes (code, description, description_bg) VALUES
    ('C62', 'Unit', 'брой'),
    ('KGM', 'Kilogram', 'килограм'),
    ('LTR', 'Litre', 'литър'),
    ('MTR', 'Metre', 'метър'),
    ('MTK', 'Square metre', 'квадратен метър'),
    ('MTQ', 'Cubic metre', 'кубичен метър'),
    ('TNE', 'Tonne', 'тон'),
    ('HUR', 'Hour', 'час'),
    ('DZN', 'Dozen', 'дузина'),
    ('BX', 'Box', 'кутия'),
    ('CT', 'Carton', 'кашон'),
    ('PA', 'Pack', 'пакет');

CREATE OR REPLACE FUNCTION generate_saft_counterpart_id(
    p_eik VARCHAR,
    p_vat VARCHAR,
    p_country VARCHAR
) RETURNS VARCHAR AS $$
DECLARE
    v_eu_countries VARCHAR[] := ARRAY['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE'];
BEGIN
    IF p_country = 'BG' OR p_country IS NULL OR p_country = '' THEN
        IF p_eik IS NOT NULL AND p_eik != '' THEN
            RETURN '10' || p_eik;
        END IF;
    END IF;
    
    IF p_vat IS NOT NULL AND p_vat != '' THEN
        IF p_country = ANY(v_eu_countries) AND p_country != 'BG' THEN
            RETURN '11' || p_country || p_vat;
        END IF;
        RETURN '12' || p_country || p_vat;
    END IF;
    
    IF p_eik IS NOT NULL AND p_eik != '' AND p_country != 'BG' THEN
        RETURN '13' || p_eik;
    END IF;
    
    RETURN '15000000000';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION update_journal_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE journal_entries
    SET 
        total_debit = (
            SELECT COALESCE(SUM(debit), 0) 
            FROM journal_entry_lines 
            WHERE journal_entry_id = NEW.journal_entry_id
        ),
        total_credit = (
            SELECT COALESCE(SUM(credit), 0) 
            FROM journal_entry_lines 
            WHERE journal_entry_id = NEW.journal_entry_id
        )
    WHERE id = NEW.journal_entry_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_journal_totals
AFTER INSERT OR UPDATE OR DELETE ON journal_entry_lines
FOR EACH ROW EXECUTE FUNCTION update_journal_totals();

CREATE MATERIALIZED VIEW mv_account_balances AS
SELECT 
    a.company_id,
    a.id AS account_id,
    a.code AS local_code,
    COALESCE(sa.code, a.code) AS saft_code,
    COALESCE(sa.name, a.name) AS saft_name,
    COALESCE(SUM(jel.debit), 0) AS total_debit,
    COALESCE(SUM(jel.credit), 0) AS total_credit,
    COALESCE(SUM(jel.debit), 0) - COALESCE(SUM(jel.credit), 0) AS net_balance
FROM accounts a
LEFT JOIN saft_accounts sa ON a.saft_account_code = sa.code
LEFT JOIN journal_entry_lines jel ON jel.account_id = a.id
LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id AND je.status = 'POSTED'
GROUP BY a.company_id, a.id, a.code, sa.code, sa.name;

CREATE MATERIALIZED VIEW mv_counterpart_balances AS
SELECT 
    c.company_id,
    c.id AS counterpart_id,
    c.name,
    c.eik,
    c.vat_number,
    c.country,
    generate_saft_counterpart_id(c.eik, c.vat_number, c.country) AS saft_id,
    COALESCE(SUM(jel.debit), 0) AS total_debit,
    COALESCE(SUM(jel.credit), 0) AS total_credit,
    COALESCE(SUM(jel.debit), 0) - COALESCE(SUM(jel.credit), 0) AS balance
FROM counterparts c
LEFT JOIN journal_entry_lines jel ON jel.counterpart_id = c.id
LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id AND je.status = 'POSTED'
GROUP BY c.company_id, c.id, c.name, c.eik, c.vat_number, c.country;

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_account_balances;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_counterpart_balances;

CREATE OR REPLACE FUNCTION sp_saft_export_monthly(
    p_company_id UUID,
    p_year INT,
    p_month INT
) RETURNS TABLE (
    header JSONB,
    accounts JSONB,
    counterparts JSONB,
    journal_entries JSONB,
    invoices JSONB,
    validation_errors JSONB
) AS $$
DECLARE
    v_start_date DATE := make_date(p_year, p_month, 1);
    v_end_date DATE := (v_start_date + INTERVAL '1 month - 1 day')::DATE;
    v_errors JSONB := '[]'::JSONB;
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT jsonb_agg(row_to_json(c.*)) FROM companies c WHERE c.id = p_company_id) AS header,
        
        (SELECT jsonb_agg(
            jsonb_build_object(
                'AccountID', COALESCE(sa.code, a.code),
                'TaxpayerAccountID', a.code,
                'AccountDescription', a.name,
                'AccountType', a.account_type,
                'OpeningDebitBalance', NULL,
                'ClosingDebitBalance', NULL
            )
        ) FROM accounts a 
        LEFT JOIN saft_accounts sa ON a.saft_account_code = sa.code
        WHERE a.company_id = p_company_id AND a.is_active = TRUE) AS accounts,
        
        (SELECT jsonb_agg(
            jsonb_build_object(
                'CustomerID', generate_saft_counterpart_id(c.eik, c.vat_number, c.country),
                'Name', c.name,
                'EIK', c.eik,
                'VATNumber', c.vat_number,
                'Country', c.country
            )
        ) FROM counterparts c 
        WHERE c.company_id = p_company_id AND c.is_active = TRUE) AS counterparts,
        
        (SELECT jsonb_agg(
            jsonb_build_object(
                'TransactionID', je.entry_number,
                'TransactionDate', je.date,
                'Description', je.description,
                'Lines', (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'RecordID', jel.line_number,
                            'AccountID', jel.account_code,
                            'DebitAmount', jel.debit,
                            'CreditAmount', jel.credit,
                            'Description', jel.description
                        )
                    ) FROM journal_entry_lines jel 
                    WHERE jel.journal_entry_id = je.id
                )
            )
        ) FROM journal_entries je
        WHERE je.company_id = p_company_id 
            AND je.date BETWEEN v_start_date AND v_end_date
            AND je.status = 'POSTED') AS journal_entries,
        
        (SELECT jsonb_agg(
            jsonb_build_object(
                'InvoiceNo', i.invoice_number,
                'InvoiceDate', i.invoice_date,
                'CustomerID', generate_saft_counterpart_id(c.eik, c.vat_number, c.country),
                'TransactionID', i.transaction_id,
                'Lines', (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'ProductCode', il.product_code,
                            'Description', il.product_description,
                            'Quantity', il.quantity,
                            'UnitPrice', il.unit_price,
                            'TaxCode', il.tax_code
                        )
                    ) FROM invoice_lines il WHERE il.invoice_id = i.id
                )
            )
        ) FROM invoices i
        JOIN counterparts c ON c.id = i.counterpart_id
        WHERE i.company_id = p_company_id 
            AND i.invoice_date BETWEEN v_start_date AND v_end_date) AS invoices,
        
        v_errors AS validation_errors;
END;
$$ LANGUAGE plpgsql;
```

### Сложни аналитични заявки

```sql
WITH RECURSIVE account_hierarchy AS (
    SELECT 
        code,
        name,
        account_type,
        code AS root_code,
        1 AS level
    FROM saft_accounts
    WHERE LENGTH(code) = 3
    
    UNION ALL
    
    SELECT 
        sa.code,
        sa.name,
        sa.account_type,
        ah.root_code,
        ah.level + 1
    FROM saft_accounts sa
    JOIN account_hierarchy ah ON LEFT(sa.code, 3) = ah.root_code
    WHERE LENGTH(sa.code) > 3
),
trial_balance AS (
    SELECT 
        COALESCE(sa.code, a.code) AS saft_code,
        COALESCE(sa.name, a.name) AS account_name,
        sa.account_type,
        COALESCE(ab.opening_debit, 0) AS opening_debit,
        COALESCE(ab.opening_credit, 0) AS opening_credit,
        COALESCE(SUM(jel.debit), 0) AS period_debit,
        COALESCE(SUM(jel.credit), 0) AS period_credit,
        COALESCE(ab.closing_debit, 0) AS closing_debit,
        COALESCE(ab.closing_credit, 0) AS closing_credit
    FROM accounts a
    LEFT JOIN saft_accounts sa ON a.saft_account_code = sa.code
    LEFT JOIN account_balances ab ON ab.account_id = a.id
    LEFT JOIN journal_entry_lines jel ON jel.account_id = a.id
    LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id 
        AND je.date BETWEEN '2026-01-01' AND '2026-01-31'
        AND je.status = 'POSTED'
    WHERE a.company_id = '00000000-0000-0000-0000-000000000001'
    GROUP BY sa.code, a.code, sa.name, a.name, sa.account_type,
             ab.opening_debit, ab.opening_credit, 
             ab.closing_debit, ab.closing_credit
)
SELECT 
    saft_code,
    account_name,
    account_type,
    opening_debit,
    opening_credit,
    period_debit,
    period_credit,
    closing_debit,
    closing_credit,
    CASE 
        WHEN account_type = 'Active' AND closing_debit > closing_credit 
            THEN closing_debit - closing_credit
        WHEN account_type = 'Passive' AND closing_credit > closing_debit 
            THEN closing_credit - closing_debit
        ELSE 0
    END AS final_balance,
    CASE 
        WHEN closing_debit >= closing_credit THEN 'Debit'
        ELSE 'Credit'
    END AS balance_type
FROM trial_balance
ORDER BY saft_code;

WITH counterpart_activity AS (
    SELECT 
        c.id,
        c.name,
        c.eik,
        c.country,
        c.counterpart_type,
        je.date,
        jel.debit,
        jel.credit,
        COALESCE(jel.debit, 0) - COALESCE(jel.credit, 0) AS net_movement
    FROM counterparts c
    JOIN journal_entry_lines jel ON jel.counterpart_id = c.id
    JOIN journal_entries je ON je.id = jel.journal_entry_id
    WHERE c.company_id = '00000000-0000-0000-0000-000000000001'
        AND je.status = 'POSTED'
),
running_balances AS (
    SELECT 
        id,
        name,
        eik,
        country,
        counterpart_type,
        date,
        net_movement,
        SUM(net_movement) OVER (
            PARTITION BY id 
            ORDER BY date 
            ROWS UNBOUNDED PRECEDING
        ) AS running_balance
    FROM counterpart_activity
)
SELECT 
    name,
    eik,
    country,
    counterpart_type,
    date,
    net_movement,
    running_balance,
    CASE 
        WHEN running_balance > 0 THEN 'Owed to us'
        WHEN running_balance < 0 THEN 'We owe'
        ELSE 'Settled'
    END AS relationship_status
FROM running_balances
ORDER BY name, date;

WITH vat_analysis AS (
    SELECT 
        je.date,
        jel.account_code,
        ti.tax_code,
        ti.tax_percentage,
        ti.tax_base,
        ti.tax_amount,
        CASE 
            WHEN jel.debit IS NOT NULL THEN 'Debit'
            ELSE 'Credit'
        END AS movement_type
    FROM journal_entry_lines jel
    JOIN journal_entries je ON je.id = jel.journal_entry_id
    JOIN tax_information ti ON ti.journal_entry_line_id = jel.id
    WHERE je.company_id = '00000000-0000-0000-0000-000000000001'
        AND je.status = 'POSTED'
)
SELECT 
    DATE_TRUNC('month', date) AS month,
    tax_code,
    tax_percentage,
    SUM(CASE WHEN movement_type = 'Credit' THEN tax_base ELSE 0 END) AS sales_base,
    SUM(CASE WHEN movement_type = 'Credit' THEN tax_amount ELSE 0 END) AS output_vat,
    SUM(CASE WHEN movement_type = 'Debit' THEN tax_base ELSE 0 END) AS purchases_base,
    SUM(CASE WHEN movement_type = 'Debit' THEN tax_amount ELSE 0 END) AS input_vat,
    SUM(CASE WHEN movement_type = 'Credit' THEN tax_amount 
             ELSE -tax_amount END) AS net_vat
FROM vat_analysis
GROUP BY DATE_TRUNC('month', date), tax_code, tax_percentage
ORDER BY month, tax_code;
```

## 9.3. SurrealDB: Документен + Графов подход

### Schema Definition

```sql
DEFINE TABLE company SCHEMAFULL;
DEFINE FIELD name ON company TYPE string ASSERT string::len($value) > 0;
DEFINE FIELD eik ON company TYPE string ASSERT string::len($value) >= 9;
DEFINE FIELD vat_number ON company TYPE option<string>;
DEFINE FIELD currency ON company TYPE string DEFAULT 'BGN';
DEFINE FIELD country ON company TYPE string DEFAULT 'BG';
DEFINE FIELD tax_accounting_basis ON company TYPE string DEFAULT 'A';
DEFINE FIELD is_vat_registered ON company TYPE bool DEFAULT false;
DEFINE FIELD software_id ON company TYPE string DEFAULT 'DOXIUS';
DEFINE FIELD software_version ON company TYPE string DEFAULT '1.0';
DEFINE FIELD created_at ON company TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON company TYPE datetime DEFAULT time::now();

DEFINE TABLE saft_account SCHEMAFULL;
DEFINE FIELD code ON saft_account TYPE string;
DEFINE FIELD name ON saft_account TYPE string;
DEFINE FIELD name_en ON saft_account TYPE option<string>;
DEFINE FIELD account_type ON saft_account TYPE string 
    ASSERT $value IN ['Active', 'Passive', 'Bifunctional', 'Sale', 'Cost'];
DEFINE FIELD section ON saft_account TYPE option<int>;
DEFINE INDEX idx_saft_code ON saft_account FIELDS code UNIQUE;

DEFINE TABLE account SCHEMAFULL;
DEFINE FIELD company ON account TYPE record<company>;
DEFINE FIELD code ON account TYPE string;
DEFINE FIELD name ON account TYPE string;
DEFINE FIELD account_type ON account TYPE string;
DEFINE FIELD saft_account ON account TYPE option<record<saft_account>>;
DEFINE FIELD opening_debit ON account TYPE option<decimal>;
DEFINE FIELD opening_credit ON account TYPE option<decimal>;
DEFINE FIELD is_active ON account TYPE bool DEFAULT true;
DEFINE INDEX idx_account_company_code ON account FIELDS company, code UNIQUE;

DEFINE TABLE counterpart SCHEMAFULL;
DEFINE FIELD company ON counterpart TYPE record<company>;
DEFINE FIELD name ON counterpart TYPE string;
DEFINE FIELD eik ON counterpart TYPE option<string>;
DEFINE FIELD vat_number ON counterpart TYPE option<string>;
DEFINE FIELD country ON counterpart TYPE string DEFAULT 'BG';
DEFINE FIELD counterpart_type ON counterpart TYPE string 
    ASSERT $value IN ['customer', 'supplier', 'both'];
DEFINE FIELD address ON counterpart TYPE option<object>;
DEFINE FIELD is_active ON counterpart TYPE bool DEFAULT true;
DEFINE INDEX idx_cp_eik ON counterpart FIELDS eik;
DEFINE INDEX idx_cp_company ON counterpart FIELDS company;

DEFINE TABLE journal_entry SCHEMAFULL;
DEFINE FIELD company ON journal_entry TYPE record<company>;
DEFINE FIELD entry_number ON journal_entry TYPE string;
DEFINE FIELD date ON journal_entry TYPE datetime;
DEFINE FIELD gl_posting_date ON journal_entry TYPE datetime;
DEFINE FIELD description ON journal_entry TYPE option<string>;
DEFINE FIELD status ON journal_entry TYPE string DEFAULT 'DRAFT'
    ASSERT $value IN ['DRAFT', 'POSTED', 'REVERSED'];
DEFINE FIELD journal_type ON journal_entry TYPE option<string>;
DEFINE FIELD source_id ON journal_entry TYPE option<string>;
DEFINE FIELD lines ON journal_entry TYPE array<object>;
DEFINE FIELD total_debit ON journal_entry TYPE decimal DEFAULT 0;
DEFINE FIELD total_credit ON journal_entry TYPE decimal DEFAULT 0;
DEFINE FIELD created_at ON journal_entry TYPE datetime DEFAULT time::now();
DEFINE INDEX idx_je_date ON journal_entry FIELDS date;
DEFINE INDEX idx_je_company ON journal_entry FIELDS company;

DEFINE TABLE invoice SCHEMAFULL;
DEFINE FIELD company ON invoice TYPE record<company>;
DEFINE FIELD counterpart ON invoice TYPE record<counterpart>;
DEFINE FIELD invoice_type ON invoice TYPE string 
    ASSERT $value IN ['sales', 'purchase'];
DEFINE FIELD invoice_number ON invoice TYPE string;
DEFINE FIELD invoice_date ON invoice TYPE datetime;
DEFINE FIELD due_date ON invoice TYPE option<datetime>;
DEFINE FIELD lines ON invoice TYPE array<object>;
DEFINE FIELD subtotal ON invoice TYPE decimal;
DEFINE FIELD vat_amount ON invoice TYPE decimal DEFAULT 0;
DEFINE FIELD total ON invoice TYPE decimal;
DEFINE FIELD journal_entry ON invoice TYPE option<record<journal_entry>>;
DEFINE FIELD transaction_id ON invoice TYPE option<string>;
DEFINE INDEX idx_inv_date ON invoice FIELDS invoice_date;
DEFINE INDEX idx_inv_counterpart ON invoice FIELDS counterpart;

DEFINE TABLE product SCHEMAFULL;
DEFINE FIELD company ON product TYPE record<company>;
DEFINE FIELD code ON product TYPE string;
DEFINE FIELD name ON product TYPE string;
DEFINE FIELD uom_base ON product TYPE string;
DEFINE FIELD uom_standard ON product TYPE string;
DEFINE FIELD uom_conversion_factor ON product TYPE decimal DEFAULT 1;
DEFINE FIELD goods_services_id ON product TYPE option<string>;
DEFINE INDEX idx_product_code ON product FIELDS company, code UNIQUE;

DEFINE TABLE warehouse SCHEMAFULL;
DEFINE FIELD company ON warehouse TYPE record<company>;
DEFINE FIELD code ON warehouse TYPE string;
DEFINE FIELD name ON warehouse TYPE string;
DEFINE FIELD location ON warehouse TYPE option<string>;

DEFINE TABLE stock_movement SCHEMAFULL;
DEFINE FIELD company ON stock_movement TYPE record<company>;
DEFINE FIELD warehouse ON stock_movement TYPE record<warehouse>;
DEFINE FIELD product ON stock_movement TYPE record<product>;
DEFINE FIELD movement_type ON stock_movement TYPE string;
DEFINE FIELD quantity ON stock_movement TYPE decimal;
DEFINE FIELD unit_price ON stock_movement TYPE decimal;
DEFINE FIELD movement_date ON stock_movement TYPE datetime;
DEFINE FIELD journal_entry ON stock_movement TYPE option<record<journal_entry>>;
DEFINE FIELD source_document ON stock_movement TYPE option<string>;
DEFINE INDEX idx_sm_product ON stock_movement FIELDS product;
DEFINE INDEX idx_sm_date ON stock_movement FIELDS movement_date;
```

### Graph Relations за автоматични кореспонденции

```sql
DEFINE TABLE correspondence_rule SCHEMAFULL;
DEFINE FIELD name ON correspondence_rule TYPE string;
DEFINE FIELD description ON correspondence_rule TYPE option<string>;
DEFINE FIELD debit_account ON correspondence_rule TYPE record<saft_account>;
DEFINE FIELD credit_account ON correspondence_rule TYPE record<saft_account>;
DEFINE FIELD movement_type ON correspondence_rule TYPE option<string>;
DEFINE FIELD is_active ON correspondence_rule TYPE bool DEFAULT true;

RELATE correspondence_rule:sales_cash->applies_to->saft_account:411;
RELATE correspondence_rule:sales_cash->applies_to->saft_account:702;

SELECT 
    out.applies_to.code AS account_code,
    out.applies_to.name AS account_name
FROM correspondence_rule:sales_cash;

SELECT 
    ->applies_to->saft_account.code AS involved_accounts
FROM correspondence_rule
WHERE movement_type = 'sale';

LET $sale = CREATE journal_entry SET 
    company = company:main,
    date = '2026-01-15',
    description = 'Продажба на стоки',
    status = 'DRAFT';

LET $rule = SELECT * FROM correspondence_rule WHERE name = 'sales_cash';

RELATE $sale.id->uses_rule->$rule.id;

SELECT 
    entry.description,
    entry.date,
    rule.debit_account.code AS debit_code,
    rule.credit_account.code AS credit_code
FROM journal_entry entry
WHERE entry->uses_rule->correspondence_rule;
```

### Мощни SurrealQL заявки

```sql
LET $company = company:main;
LET $start = '2026-01-01T00:00:00Z';
LET $end = '2026-01-31T23:59:59Z';

SELECT 
    code,
    name,
    account_type,
    math::sum(lines.map(|l| $l.debit OR 0)) AS total_debit,
    math::sum(lines.map(|l| $l.credit OR 0)) AS total_credit
FROM account
WHERE company = $company
    AND is_active = true
ORDER BY code;

SELECT 
    id,
    entry_number,
    date,
    description,
    total_debit,
    total_credit,
    (total_debit - total_credit).abs() AS diff,
    IF (total_debit - total_credit).abs() < 0.01 THEN 'balanced' ELSE 'unbalanced' END AS status
FROM journal_entry
WHERE company = $company
    AND date >= $start
    AND date <= $end
    AND status = 'POSTED'
ORDER BY date;

SELECT 
    counterpart.name,
    counterpart.eik,
    counterpart.country,
    math::sum(lines.map(|l| 
        IF $l.counterpart = counterpart.id THEN 
            ($l.debit OR 0) - ($l.credit OR 0) 
        ELSE 0 
        END
    )) AS balance
FROM counterpart, journal_entry
WHERE company = $company
    AND journal_entry.company = $company
    AND journal_entry.status = 'POSTED'
GROUP BY counterpart
ORDER BY balance DESC;

SELECT 
    product.code AS product_code,
    product.name AS product_name,
    warehouse.name AS warehouse_name,
    math::sum(IF movement_type IN ['10', 'purchase'] THEN quantity ELSE -quantity END) AS current_stock,
    math::sum(IF movement_type IN ['10', 'purchase'] THEN quantity * unit_price ELSE 0 END) -
    math::sum(IF movement_type = '30' THEN quantity * unit_price ELSE 0 END) AS stock_value
FROM stock_movement
WHERE company = $company
    AND movement_date <= $end
GROUP BY product, warehouse
HAVING current_stock != 0
ORDER BY product_code;

DEFINE FUNCTION fn::generate_saft_id($eik, $vat, $country) {
    LET $eu = ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE'];
    
    RETURN IF $country = 'BG' AND $eik THEN '10' + $eik
        ELSE IF $vat AND $country IN $eu AND $country != 'BG' THEN '11' + $country + $vat
        ELSE IF $vat THEN '12' + $country + $vat
        ELSE IF $eik AND $country != 'BG' THEN '13' + $eik
        ELSE '15000000000'
    END;
};

SELECT 
    id,
    name,
    eik,
    vat_number,
    country,
    fn::generate_saft_id(eik, vat_number, country) AS saft_id
FROM counterpart
WHERE company = $company;

LET $mappings = SELECT 
    code,
    saft_account.code AS saft_code
FROM account
WHERE company = $company AND saft_account IS NOT NONE;

SELECT 
    entry.entry_number,
    line.account_code,
    $mappings.find(|m| $m.code = line.account_code).saft_code AS saft_account,
    line.debit,
    line.credit
FROM journal_entry entry, line IN entry.lines
WHERE entry.company = $company
    AND entry.date >= $start
ORDER BY entry.date, entry.entry_number;
```

## 9.4. Хибриден подход: Най-доброто от двата свята

### Архитектура с синхронизация

```rust
use serde::{Deserialize, Serialize};
use sqlx::postgres::PgPool;
use reqwest::Client;
use std::collections::HashMap;

pub struct HybridDataStore {
    pg_pool: PgPool,
    surreal_client: Client,
    surreal_url: String,
    surreal_ns: String,
    surreal_db: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SyncResult {
    pub table_name: String,
    pub records_synced: usize,
    pub errors: Vec<String>,
}

impl HybridDataStore {
    pub async fn sync_accounts_to_surreal(&self, company_id: &str) -> Result<SyncResult, sqlx::Error> {
        let accounts = sqlx::query_as!(
            AccountRow,
            r#"
            SELECT 
                a.id,
                a.code,
                a.name,
                a.account_type,
                sa.code as saft_code,
                sa.name as saft_name
            FROM accounts a
            LEFT JOIN saft_accounts sa ON a.saft_account_code = sa.code
            WHERE a.company_id = $1 AND a.is_active = true
            "#,
            uuid::Uuid::parse_str(company_id).unwrap()
        )
        .fetch_all(&self.pg_pool)
        .await?;
        
        let mut synced = 0;
        let mut errors = Vec::new();
        
        for acc in accounts {
            let surql = format!(
                "CREATE account SET \
                    id = type::thing('account', '{}'), \
                    code = '{}', \
                    name = '{}', \
                    account_type = '{}', \
                    saft_account = IF '{}' != '' THEN type::thing('saft_account', '{}') ELSE NONE END",
                acc.id,
                acc.code,
                acc.name.replace("'", "''"),
                acc.account_type,
                acc.saft_code.as_deref().unwrap_or(""),
                acc.saft_code.as_deref().unwrap_or("")
            );
            
            let response = self.surreal_client
                .post(format!("{}/sql", self.surreal_url))
                .header("surreal-ns", &self.surreal_ns)
                .header("surreal-db", &self.surreal_db)
                .body(surql)
                .send()
                .await;
            
            match response {
                Ok(resp) if resp.status().is_success() => synced += 1,
                Ok(resp) => errors.push(format!("SurrealDB error: {}", resp.status())),
                Err(e) => errors.push(format!("Connection error: {}", e)),
            }
        }
        
        Ok(SyncResult {
            table_name: "accounts".into(),
            records_synced: synced,
            errors,
        })
    }
    
    pub async fn generate_saft_from_surreal(
        &self,
        company_id: &str,
        period_start: &str,
        period_end: &str,
    ) -> Result<String, Box<dyn std::error::Error>> {
        let query = format!(
            r#"
            LET $company = type::thing('company', '{}');
            LET $start = '{}T00:00:00Z';
            LET $end = '{}T23:59:59Z';
            
            SELECT 
                code, name, account_type
            FROM account
            WHERE company = $company;
            
            SELECT 
                fn::generate_saft_id(eik, vat_number, country) AS saft_id,
                name, eik, vat_number, country
            FROM counterpart
            WHERE company = $company;
            
            SELECT 
                entry_number, date, description, total_debit, total_credit,
                lines
            FROM journal_entry
            WHERE company = $company
                AND date >= $start
                AND date <= $end
                AND status = 'POSTED'
            ORDER BY date;
            "#,
            company_id, period_start, period_end
        );
        
        let response = self.surreal_client
            .post(format!("{}/sql", self.surreal_url))
            .header("surreal-ns", &self.surreal_ns)
            .header("surreal-db", &self.surreal_db)
            .body(query)
            .send()
            .await?
            .text()
            .await?;
        
        Ok(response)
    }
}

#[derive(Debug, sqlx::FromRow)]
struct AccountRow {
    id: uuid::Uuid,
    code: String,
    name: String,
    account_type: String,
    saft_code: Option<String>,
    saft_name: Option<String>,
}
```

## 9.5. Performance Optimization

### PostgreSQL Indexing Strategy

```sql
CREATE INDEX CONCURRENTLY idx_je_company_date_status 
    ON journal_entries(company_id, date, status);

CREATE INDEX CONCURRENTLY idx_jel_account_debit 
    ON journal_entry_lines(account_id) 
    WHERE debit IS NOT NULL;

CREATE INDEX CONCURRENTLY idx_jel_counterpart 
    ON journal_entry_lines(counterpart_id) 
    WHERE counterpart_id IS NOT NULL;

CREATE INDEX CONCURRENTLY idx_inv_type_date 
    ON invoices(company_id, invoice_type, invoice_date);

CREATE INDEX CONCURRENTLY idx_ti_tax_code 
    ON tax_information(tax_code, tax_base, tax_amount);

CREATE INDEX CONCURRENTLY idx_account_saft 
    ON accounts(company_id, saft_account_code);

VACUUM ANALYZE journal_entries;
VACUUM ANALYZE journal_entry_lines;
VACUUM ANALYZE invoices;

SET work_mem = '256MB';
SET shared_buffers = '2GB';
SET effective_cache_size = '6GB';
SET random_page_cost = 1.1;
SET effective_io_concurrency = 200;

SET enable_seqscan = off;
SET enable_indexscan = on;
SET enable_bitmapscan = on;

EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM journal_entries 
WHERE company_id = 'xxx' 
    AND date BETWEEN '2026-01-01' AND '2026-01-31';
```

### SurrealDB Optimization

```sql
DEFINE INDEX idx_je_company_date ON journal_entry FIELDS company, date;
DEFINE INDEX idx_je_status_date ON journal_entry FIELDS status, date;
DEFINE INDEX idx_inv_company_type ON invoice FIELDS company, invoice_type;
DEFINE INDEX idx_inv_date_range ON invoice FIELDS invoice_date;

SELECT * FROM journal_entry 
WHERE company = $company 
    AND date >= $start 
    AND date <= $end
    AND status = 'POSTED'
PARALLEL;

SELECT count() FROM journal_entry 
WHERE company = $company GROUP ALL;

LET $company = company:main;
SELECT 
    count() AS total,
    math::sum(total_debit) AS grand_debit,
    math::sum(total_credit) AS grand_credit
FROM journal_entry
WHERE company = $company 
    AND date >= '2026-01-01' 
    AND status = 'POSTED';
```

## 9.6. Benchmarking

### Rust Performance Test

```rust
use std::time::Instant;

pub async fn benchmark_saft_generation(data: &SaftExportData) -> BenchmarkResult {
    let mut results = Vec::new();
    
    let start = Instant::now();
    let mut validator = SaftValidator::new();
    let validation = validator.validate_all(data);
    results.push(("validation", start.elapsed()));
    
    let start = Instant::now();
    let accounts_xml = generate_accounts_xml(&data.accounts, &data.saft_accounts);
    results.push(("accounts_xml", start.elapsed()));
    
    let start = Instant::now();
    let entries_xml = generate_journal_entries_xml(&data.journal_entries);
    results.push(("entries_xml", start.elapsed()));
    
    let start = Instant::now();
    let invoices_xml = generate_invoices_xml(&data.invoices, &data.counterparts);
    results.push(("invoices_xml", start.elapsed()));
    
    let start = Instant::now();
    let full_xml = assemble_full_xml(data);
    results.push(("full_assembly", start.elapsed()));
    
    BenchmarkResult {
        validation_errors: validation.error_count,
        validation_warnings: validation.warning_count,
        timing: results,
        total_size_bytes: full_xml.len(),
    }
}

#[derive(Debug)]
pub struct BenchmarkResult {
    pub validation_errors: usize,
    pub validation_warnings: usize,
    pub timing: Vec<(&'static str, std::time::Duration)>,
    pub total_size_bytes: usize,
}
```

## 9.7. Заключение

Изборът между SQL и NoSQL не е binary decision. За SAF-T:

1. **PostgreSQL** е по-добър за:
   - Строга ACID съответствие
   - Сложни JOIN и агрегации
   - Зрели екипи с SQL опит

2. **SurrealDB** е по-добър за:
   - Гъвкав схематичен модел
   - Graph relations между сметки
   - Embedded/Mobile deployments
   - Real-time sync

3. **Хибриден подход** дава:
   - SQL за отчети и анализи
   - NoSQL за бърз достъп и експорт
   - Sync layer между двете
