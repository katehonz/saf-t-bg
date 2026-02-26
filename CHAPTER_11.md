# Глава 11: Реални казуси от практиката

## 11.1. Казус: Търговец на едро с 3 склада

### Контекст

Фирма за търговия на едро с бързо оборотни стоки:
- 3 физически склада в различни градове
- 5000+ продукта
- 200+ фактури на ден
- Български клиенти и доставчици от ЕС

### Предизвикателства

1. **Мерни единици**: В един склад "кашон", в друг "кутия", в трети "опаковка"
2. **Продукти със същото име**: "Захар 1кг", "Захар кристална 1кг", "Захар бяла 1кг"
3. **Контрагенти без ЕИК**: Поради стари записи от преди 10 години

### Решение: Rust + Python Pipeline

```rust
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct ProductNormalization {
    pub original_code: String,
    pub original_name: String,
    pub canonical_code: String,
    pub canonical_name: String,
    pub uom_base: String,
    pub uom_standard: String,
    pub conversion_factor: Decimal,
}

pub struct ProductDeduplicator {
    products: Vec<ProductNormalization>,
    name_index: HashMap<String, Vec<usize>>,
}

impl ProductDeduplicator {
    pub fn new() -> Self {
        Self {
            products: Vec::new(),
            name_index: HashMap::new(),
        }
    }
    
    pub fn add_product(&mut self, code: &str, name: &str, uom: &str) -> String {
        let normalized_name = self.normalize_name(name);
        let canonical_code = self.find_or_create_canonical(&normalized_name, code);
        
        let uom_standard = self.normalize_uom(uom);
        
        self.products.push(ProductNormalization {
            original_code: code.to_string(),
            original_name: name.to_string(),
            canonical_code: canonical_code.clone(),
            canonical_name: normalized_name,
            uom_base: uom.to_string(),
            uom_standard,
            conversion_factor: Decimal::ONE,
        });
        
        canonical_code
    }
    
    fn normalize_name(&self, name: &str) -> String {
        let name = name.to_lowercase();
        let name = name.replace(['-', '_', '.'], " ");
        let name = name.split_whitespace().collect::<Vec<_>>().join(" ");
        let name = name.replace("1 кг", "1kg");
        let name = name.replace("килограм", "kg");
        name
    }
    
    fn normalize_uom(&self, uom: &str) -> String {
        let uom_lower = uom.to_lowercase().trim().to_string();
        
        match uom_lower.as_str() {
            "бр" | "бр." | "брой" | "бройки" => "C62",
            "кг" | "кг." | "килограм" | "килограма" => "KGM",
            "л" | "литър" | "литра" | "литри" => "LTR",
            "кашон" | "кашони" => "CT",
            "кутия" | "кутии" => "BX",
            "пакет" | "пакети" => "PA",
            _ => "C62",
        }
    }
    
    fn find_or_create_canonical(&mut self, normalized_name: &str, fallback_code: &str) -> String {
        let existing = self.name_index.get(normalized_name);
        
        match existing {
            Some(indices) if !indices.is_empty() => {
                self.products[indices[0]].canonical_code.clone()
            }
            _ => {
                let code = format!("PROD{:06}", self.products.len() + 1);
                self.name_index
                    .entry(normalized_name.to_string())
                    .or_insert_with(Vec::new)
                    .push(self.products.len());
                code
            }
        }
    }
    
    pub fn generate_mapping_report(&self) -> Vec<(String, String, String, String)> {
        self.products
            .iter()
            .map(|p| {
                (
                    p.original_code.clone(),
                    p.original_name.clone(),
                    p.canonical_code.clone(),
                    p.uom_standard.clone(),
                )
            })
            .collect()
    }
}

pub struct WarehouseConsolidator {
    warehouses: HashMap<String, StockPosition>,
}

#[derive(Debug, Clone)]
pub struct StockPosition {
    pub warehouse_id: String,
    pub product_code: String,
    pub canonical_product_code: String,
    pub quantity: Decimal,
    pub uom: String,
    pub value: Decimal,
}

impl WarehouseConsolidator {
    pub fn new() -> Self {
        Self {
            warehouses: HashMap::new(),
        }
    }
    
    pub fn add_position(
        &mut self,
        warehouse_id: &str,
        product_code: &str,
        canonical_code: &str,
        quantity: Decimal,
        uom: &str,
        value: Decimal,
    ) {
        let key = format!("{}:{}", warehouse_id, canonical_code);
        
        self.warehouses
            .entry(key)
            .and_modify(|pos| {
                pos.quantity += quantity;
                pos.value += value;
            })
            .or_insert(StockPosition {
                warehouse_id: warehouse_id.to_string(),
                product_code: product_code.to_string(),
                canonical_product_code: canonical_code.to_string(),
                quantity,
                uom: uom.to_string(),
                value,
            });
    }
    
    pub fn get_physical_stock(&self) -> Vec<&StockPosition> {
        self.warehouses.values().collect()
    }
    
    pub fn get_total_by_product(&self, canonical_code: &str) -> Decimal {
        self.warehouses
            .values()
            .filter(|p| p.canonical_product_code == canonical_code)
            .map(|p| p.quantity)
            .sum()
    }
}

fn main() {
    let mut dedup = ProductDeduplicator::new();
    
    dedup.add_product("A001", "Захар 1кг", "кг");
    dedup.add_product("B001", "Захар кристална 1кг", "килограм");
    dedup.add_product("C001", "Захар бяла 1 килограм", "КГ.");
    
    dedup.add_product("A002", "Олио 1л", "л");
    dedup.add_product("B002", "Олио слънчогледово 1 литър", "литра");
    
    let report = dedup.generate_mapping_report();
    for (orig_code, orig_name, canon_code, uom) in report {
        println!("{} '{}' → {} [{}]", orig_code, orig_name, canon_code, uom);
    }
}
```

### Python Analysis

```python
import pandas as pd
from collections import defaultdict

def analyze_product_duplicates(products_df: pd.DataFrame) -> dict:
    products_df['normalized_name'] = products_df['name'].str.lower().str.strip()
    products_df['normalized_name'] = products_df['normalized_name'].str.replace(r'[^\w\s]', ' ', regex=True)
    products_df['normalized_name'] = products_df['normalized_name'].str.replace(r'\s+', ' ', regex=True)
    
    name_groups = products_df.groupby('normalized_name')
    
    duplicates = []
    for name, group in name_groups:
        if len(group) > 1:
            duplicates.append({
                'normalized_name': name,
                'original_codes': group['code'].tolist(),
                'original_names': group['name'].tolist(),
                'warehouses': group['warehouse_id'].unique().tolist() if 'warehouse_id' in group.columns else [],
                'total_stock': group['quantity'].sum() if 'quantity' in group.columns else 0
            })
    
    return {
        'total_products': len(products_df),
        'unique_normalized': len(name_groups),
        'duplicate_groups': len(duplicates),
        'duplicates': duplicates[:10],
        'potential_consolidation': len(products_df) - len(name_groups)
    }

def generate_consolidation_plan(products_df: pd.DataFrame) -> pd.DataFrame:
    name_to_canonical = {}
    canonical_counter = 1
    
    results = []
    
    for _, row in products_df.iterrows():
        normalized = row['name'].lower().strip()
        
        if normalized not in name_to_canonical:
            name_to_canonical[normalized] = f"PROD{canonical_counter:06d}"
            canonical_counter += 1
        
        results.append({
            'original_code': row['code'],
            'original_name': row['name'],
            'canonical_code': name_to_canonical[normalized],
            'original_uom': row.get('uom', 'C62'),
            'standard_uom': normalize_uom(row.get('uom', ''))
        })
    
    return pd.DataFrame(results)

def normalize_uom(uom: str) -> str:
    mapping = {
        'бр': 'C62', 'бр.': 'C62', 'брой': 'C62',
        'кг': 'KGM', 'кг.': 'KGM', 'килограм': 'KGM',
        'л': 'LTR', 'литър': 'LTR', 'литра': 'LTR',
        'кашон': 'CT', 'кутия': 'BX', 'пакет': 'PA',
    }
    return mapping.get(uom.lower().strip(), 'C62')
```

## 11.2. Казус: Производствено предприятие с ВОП

### Контекст

Производител на мебели:
- Вътрешнооборотни доставките (ВОП) за ЕС клиенти
- Сложни ДДС схеми (нутриобщностни доставки)
- Многоставъчни фактури с различни ДДС ставки

### Предизвикателства

1. **ДДС кодове**: Разграничаване на вътрешни от вътрешнообщностни доставки
2. **Транзитни движения**: Стоки, които минават през междинни складове
3. **Многостранни сделки**: Тристранични транзакции

### Решение: ДДС Classification Engine

```rust
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum VatTransactionType {
    Domestic,              // Вътрешна доставка
    IntraCommunitySupply,  // Вътрешнообщностна доставка (ВОП)
    IntraCommunityAcquisition, // Вътрешнообщностно придобиване
    Export,                // Износ извън ЕС
    Import,                // Внос извън ЕС
    ReverseCharge,         // Обратно начисляване
    Exempt,                // Освободена доставка
}

#[derive(Debug, Clone)]
pub struct VatClassification {
    pub transaction_type: VatTransactionType,
    pub tax_code: String,
    pub tax_rate: Decimal,
    pub requires_vies_check: bool,
    pub requires_intrastat: bool,
    pub description: String,
}

pub struct VatClassifier {
    eu_countries: Vec<&'static str>,
    vat_rates: HashMap<String, Decimal>,
}

impl VatClassifier {
    pub fn new() -> Self {
        Self {
            eu_countries: vec![
                "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
                "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
                "PL", "PT", "RO", "SK", "SI", "ES", "SE"
            ],
            vat_rates: HashMap::from([
                ("100211".to_string(), Decimal::new(20, 0)),  // 20%
                ("100213".to_string(), Decimal::new(9, 0)),   // 9%
                ("100214".to_string(), Decimal::ZERO),         // 0%
                ("100219".to_string(), Decimal::ZERO),         // Освободени
            ]),
        }
    }
    
    pub fn classify_transaction(
        &self,
        supplier_country: &str,
        customer_country: &str,
        customer_vat: Option<&str>,
        is_vat_registered: bool,
        goods_dispatched: bool,
    ) -> VatClassification {
        let supplier_eu = self.eu_countries.contains(&supplier_country);
        let customer_eu = self.eu_countries.contains(&customer_country);
        
        if supplier_country == customer_country {
            return VatClassification {
                transaction_type: VatTransactionType::Domestic,
                tax_code: "100211".to_string(),
                tax_rate: self.vat_rates.get("100211").copied().unwrap_or(Decimal::ZERO),
                requires_vies_check: false,
                requires_intrastat: false,
                description: "Вътрешна доставка".to_string(),
            };
        }
        
        if supplier_eu && customer_eu && supplier_country != customer_country {
            if goods_dispatched && customer_vat.is_some() {
                return VatClassification {
                    transaction_type: VatTransactionType::IntraCommunitySupply,
                    tax_code: "100219".to_string(),
                    tax_rate: Decimal::ZERO,
                    requires_vies_check: true,
                    requires_intrastat: true,
                    description: "Вътрешнообщностна доставка (ВОП) - чл. 86".to_string(),
                };
            }
            
            if !goods_dispatched && customer_vat.is_some() {
                return VatClassification {
                    transaction_type: VatTransactionType::IntraCommunityAcquisition,
                    tax_code: "100211".to_string(),
                    tax_rate: self.vat_rates.get("100211").copied().unwrap_or(Decimal::ZERO),
                    requires_vies_check: false,
                    requires_intrastat: true,
                    description: "Вътрешнообщностно придобиване (ВОП)".to_string(),
                };
            }
        }
        
        if supplier_eu && !customer_eu {
            return VatClassification {
                transaction_type: VatTransactionType::Export,
                tax_code: "100219".to_string(),
                tax_rate: Decimal::ZERO,
                requires_vies_check: false,
                requires_intrastat: false,
                description: "Износ извън ЕС".to_string(),
            };
        }
        
        if !supplier_eu && customer_eu {
            return VatClassification {
                transaction_type: VatTransactionType::Import,
                tax_code: "100211".to_string(),
                tax_rate: self.vat_rates.get("100211").copied().unwrap_or(Decimal::ZERO),
                requires_vies_check: false,
                requires_intrastat: false,
                description: "Внос извън ЕС".to_string(),
            };
        }
        
        VatClassification {
            transaction_type: VatTransactionType::Domestic,
            tax_code: "100211".to_string(),
            tax_rate: Decimal::ZERO,
            requires_vies_check: false,
            requires_intrastat: false,
            description: "По подразбиране - вътрешна".to_string(),
        }
    }
    
    pub fn generate_tax_table_entry(&self, classification: &VatClassification) -> String {
        format!(
            r#"<nsSAFT:TaxCodeDetails>
    <nsSAFT:TaxCode>{}</nsSAFT:TaxCode>
    <nsSAFT:Description>{}</nsSAFT:Description>
    <nsSAFT:TaxPercentage>{}</nsSAFT:TaxPercentage>
    <nsSAFT:Country>BG</nsSAFT:Country>
</nsSAFT:TaxCodeDetails>"#,
            classification.tax_code,
            classification.description,
            classification.tax_rate
        )
    }
}

fn validate_vies(vat_number: &str, country: &str) -> Result<bool, String> {
    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_domestic_transaction() {
        let classifier = VatClassifier::new();
        let result = classifier.classify_transaction(
            "BG", "BG", Some("123456789"), true, true
        );
        assert_eq!(result.transaction_type, VatTransactionType::Domestic);
        assert_eq!(result.tax_rate, Decimal::new(20, 0));
    }
    
    #[test]
    fn test_intra_community_supply() {
        let classifier = VatClassifier::new();
        let result = classifier.classify_transaction(
            "BG", "DE", Some("DE123456789"), true, true
        );
        assert_eq!(result.transaction_type, VatTransactionType::IntraCommunitySupply);
        assert_eq!(result.tax_rate, Decimal::ZERO);
        assert!(result.requires_vies_check);
    }
    
    #[test]
    fn test_export() {
        let classifier = VatClassifier::new();
        let result = classifier.classify_transaction(
            "BG", "US", None, false, true
        );
        assert_eq!(result.transaction_type, VatTransactionType::Export);
        assert_eq!(result.tax_rate, Decimal::ZERO);
    }
}
```

### Python VIES Integration

```python
import requests
from dataclasses import dataclass
from typing import Optional, Tuple
import re

@dataclass
class ViesResult:
    is_valid: bool
    company_name: Optional[str]
    company_address: Optional[str]
    error: Optional[str]

class ViesValidator:
    VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{}/vat/{}"
    
    @staticmethod
    def validate(vat_number: str, country_code: str) -> ViesResult:
        clean_vat = re.sub(r'[^0-9A-Za-z]', '', vat_number.upper())
        
        if clean_vat.startswith(country_code):
            clean_vat = clean_vat[len(country_code):]
        
        url = ViesValidator.VIES_URL.format(country_code, clean_vat)
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return ViesResult(
                    is_valid=data.get('isValid', False),
                    company_name=data.get('name'),
                    company_address=data.get('address'),
                    error=None
                )
            else:
                return ViesResult(
                    is_valid=False,
                    company_name=None,
                    company_address=None,
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return ViesResult(
                is_valid=False,
                company_name=None,
                company_address=None,
                error=str(e)
            )
    
    @staticmethod
    def batch_validate(vat_list: list) -> dict:
        results = {}
        for vat_info in vat_list:
            vat = vat_info['vat_number']
            country = vat_info['country']
            results[f"{country}{vat}"] = ViesValidator.validate(vat, country)
        return results

def generate_intrastat_report(invoices: list, period: str) -> dict:
    intrastat_lines = []
    
    for inv in invoices:
        if inv.get('transaction_type') in ['intra_community_supply', 'intra_community_acquisition']:
            for line in inv.get('lines', []):
                intrastat_lines.append({
                    'period': period,
                    'flow': 'dispatch' if inv['transaction_type'] == 'intra_community_supply' else 'arrival',
                    'partner_country': inv['counterpart_country'],
                    'product_code': line.get('cn_code', line.get('product_code')),
                    'description': line.get('product_description'),
                    'quantity': line.get('quantity'),
                    'value': line.get('line_total'),
                    'weight_kg': line.get('weight', line.get('quantity')),
                })
    
    summary = {}
    for line in intrastat_lines:
        key = (line['period'], line['flow'], line['partner_country'])
        if key not in summary:
            summary[key] = {'lines': [], 'total_value': 0, 'total_weight': 0}
        summary[key]['lines'].append(line)
        summary[key]['total_value'] += line['value']
        summary[key]['total_weight'] += line['weight_kg']
    
    return {
        'lines': intrastat_lines,
        'summary': summary,
        'total_lines': len(intrastat_lines),
        'total_value': sum(l['value'] for l in intrastat_lines),
    }
```

## 11.3. Казус: Холдинг с множество дружества

### Контекст

Холдинг компания с:
- 5 дъщерни дружества в България
- Вътрешни транзакции между дружествата
- Консолидирана отчетност

### Предизвикателства

1. **Междуфирмени транзакции**: Трябва да се идентифицират и елиминират
2. **Различни сметкопланове**: Всяко дружество има своя номерация
3. **Консолидация**: Обединяване на SAF-T файлове

### Решение: Консолидационен Engine

```rust
use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone)]
pub struct IntercompanyTransaction {
    pub from_company_id: String,
    pub to_company_id: String,
    pub transaction_id: String,
    pub amount: Decimal,
    pub account_debit: String,
    pub account_credit: String,
}

#[derive(Debug, Clone)]
pub struct ConsolidatedSaft {
    pub companies: Vec<String>,
    pub elimination_entries: Vec<JournalEntry>,
    pub consolidated_totals: HashMap<String, Decimal>,
}

pub struct ConsolidationEngine {
    group_companies: HashSet<String>,
    intercompany_accounts: HashSet<String>,
}

impl ConsolidationEngine {
    pub fn new(companies: Vec<String>) -> Self {
        let group_set: HashSet<String> = companies.into_iter().collect();
        
        let ic_accounts: HashSet<String> = [
            "419".to_string(),  // Вътрешни разчети
            "4191".to_string(),
            "4192".to_string(),
        ].into_iter().collect();
        
        Self {
            group_companies: group_set,
            intercompany_accounts: ic_accounts,
        }
    }
    
    pub fn identify_intercompany_transactions(
        &self,
        all_journal_entries: Vec<(String, JournalEntry)>,
        all_counterparts: &HashMap<String, Counterpart>,
    ) -> Vec<IntercompanyTransaction> {
        let mut ic_transactions = Vec::new();
        
        for (company_id, entry) in all_journal_entries {
            for line in &entry.lines {
                if let Some(ref cp_id) = line.counterpart_id {
                    if let Some(cp) = all_counterparts.get(cp_id) {
                        if let Some(ref cp_eik) = cp.eik {
                            let saft_id = format!("10{}", cp_eik);
                            if self.group_companies.contains(&saft_id) {
                                ic_transactions.push(IntercompanyTransaction {
                                    from_company_id: company_id.clone(),
                                    to_company_id: saft_id,
                                    transaction_id: entry.id.clone(),
                                    amount: line.debit.unwrap_or(Decimal::ZERO) 
                                        + line.credit.unwrap_or(Decimal::ZERO),
                                    account_debit: line.account_code.clone(),
                                    account_credit: String::new(),
                                });
                            }
                        }
                    }
                }
            }
        }
        
        ic_transactions
    }
    
    pub fn generate_elimination_entries(
        &self,
        ic_transactions: &[IntercompanyTransaction],
    ) -> Vec<JournalEntry> {
        let mut eliminations = Vec::new();
        let mut by_pair: HashMap<(String, String), Vec<&IntercompanyTransaction>> = HashMap::new();
        
        for t in ic_transactions {
            let key = (t.from_company_id.clone(), t.to_company_id.clone());
            by_pair.entry(key).or_insert_with(Vec::new).push(t);
        }
        
        for ((from, to), transactions) in by_pair {
            let total: Decimal = transactions.iter().map(|t| t.amount).sum();
            
            if total > Decimal::ZERO {
                let elimination = JournalEntry {
                    id: format!("ELIM-{}-{}", from, to),
                    company_id: "CONSOLIDATED".to_string(),
                    entry_number: format!("CONS/{}", eliminations.len() + 1),
                    date: chrono::Utc::now().date_naive(),
                    gl_posting_date: chrono::Utc::now().date_naive(),
                    description: format!("Елиминиране на междуфирмени транзакции {} ↔ {}", from, to),
                    status: EntryStatus::Posted,
                    journal_type: Some("CONS".to_string()),
                    source_id: None,
                    lines: vec![
                        JournalEntryLine {
                            id: format!("ELIM-{}-1", eliminations.len() + 1),
                            account_id: "419".to_string(),
                            account_code: "419".to_string(),
                            counterpart_id: Some(to.clone()),
                            debit: Some(total),
                            credit: None,
                            description: "Елиминиране - вземания".to_string(),
                            tax_code: None,
                            tax_base: None,
                            tax_amount: None,
                        },
                        JournalEntryLine {
                            id: format!("ELIM-{}-2", eliminations.len() + 1),
                            account_id: "419".to_string(),
                            account_code: "419".to_string(),
                            counterpart_id: Some(from.clone()),
                            debit: None,
                            credit: Some(total),
                            description: "Елиминиране - задължения".to_string(),
                            tax_code: None,
                            tax_base: None,
                            tax_amount: None,
                        },
                    ],
                    total_debit: Some(total),
                    total_credit: Some(total),
                };
                
                eliminations.push(elimination);
            }
        }
        
        eliminations
    }
    
    pub fn merge_saft_files(
        &self,
        saft_files: Vec<SaftExportData>,
    ) -> ConsolidatedSaft {
        let mut all_accounts: HashMap<String, Account> = HashMap::new();
        let mut all_entries: Vec<JournalEntry> = Vec::new();
        let mut all_invoices: Vec<Invoice> = Vec::new();
        
        for saft in saft_files {
            let company_id = saft.company.id.clone();
            
            for acc in saft.accounts {
                let key = format!("{}:{}", company_id, acc.code);
                all_accounts.insert(key, acc);
            }
            
            all_entries.extend(saft.journal_entries);
            all_invoices.extend(saft.invoices);
        }
        
        let mut consolidated_totals: HashMap<String, Decimal> = HashMap::new();
        
        for entry in &all_entries {
            for line in &entry.lines {
                let base_code = line.account_code.chars().take(3).collect::<String>();
                let amount = line.debit.unwrap_or(Decimal::ZERO) 
                    - line.credit.unwrap_or(Decimal::ZERO);
                *consolidated_totals.entry(base_code).or_insert(Decimal::ZERO) += amount;
            }
        }
        
        ConsolidatedSaft {
            companies: self.group_companies.iter().cloned().collect(),
            elimination_entries: vec![],
            consolidated_totals,
        }
    }
}
```

## 11.4. Казус: Едноличен търговец с опростен счетоводен отчет

### Контекст

Малък бизнес:
- Едноличен търговец
- До 50 фактури месечно
- Без ДДС регистрация
- Опростен счетоводен отчет

### Предизвикателства

1. **Ограничени ресурси**: Няма счетоводител на пълно работно време
2. **Опростена структура**: По-малко сметки, по-малко детайли
3. **Липсващи данни**: Често липсват ЕИК на малки контрагенти

### Решение: Упростен Pipeline

```python
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
import re

@dataclass
class SimplifiedCounterpart:
    name: str
    eik: Optional[str]
    country: str
    saft_id: str
    is_small_business: bool

class SimplifiedSaftGenerator:
    DEFAULT_TAX_CODE = '100219'
    DEFAULT_UOM = 'C62'
    
    def __init__(self, company_eik: str, company_name: str):
        self.company_eik = company_eik
        self.company_name = company_name
        self.counterparts: dict = {}
        self.sales: list = []
        self.expenses: list = []
    
    def add_counterpart(
        self, 
        name: str, 
        eik: Optional[str] = None,
        country: str = 'BG'
    ) -> str:
        clean_eik = self._clean_eik(eik) if eik else None
        
        is_small = not clean_eik or len(clean_eik) != 9
        
        saft_id = self._generate_saft_id(clean_eik, country)
        
        cp = SimplifiedCounterpart(
            name=name,
            eik=clean_eik,
            country=country,
            saft_id=saft_id,
            is_small_business=is_small
        )
        
        self.counterparts[saft_id] = cp
        return saft_id
    
    def add_sale(
        self,
        counterpart_saft_id: str,
        invoice_number: str,
        date: str,
        amount: Decimal,
        description: str = "Продажба"
    ):
        self.sales.append({
            'counterpart_id': counterpart_saft_id,
            'invoice_number': invoice_number,
            'date': date,
            'amount': amount,
            'description': description,
        })
    
    def add_expense(
        self,
        counterpart_saft_id: str,
        document_number: str,
        date: str,
        amount: Decimal,
        description: str,
        expense_type: str = '602'
    ):
        self.expenses.append({
            'counterpart_id': counterpart_saft_id,
            'document_number': document_number,
            'date': date,
            'amount': amount,
            'description': description,
            'expense_type': expense_type,
        })
    
    def generate_simple_journal(self) -> list:
        entries = []
        
        for i, sale in enumerate(self.sales, 1):
            entries.append({
                'entry_number': f'{i:04d}',
                'date': sale['date'],
                'description': sale['description'],
                'lines': [
                    {'account': '411', 'debit': sale['amount'], 'credit': None, 
                     'counterpart': sale['counterpart_id']},
                    {'account': '702', 'debit': None, 'credit': sale['amount'],
                     'counterpart': sale['counterpart_id']},
                ]
            })
        
        for i, exp in enumerate(self.expenses, len(entries) + 1):
            entries.append({
                'entry_number': f'{i:04d}',
                'date': exp['date'],
                'description': exp['description'],
                'lines': [
                    {'account': exp['expense_type'], 'debit': exp['amount'], 'credit': None,
                     'counterpart': exp['counterpart_id']},
                    {'account': '401', 'debit': None, 'credit': exp['amount'],
                     'counterpart': exp['counterpart_id']},
                ]
            })
        
        return entries
    
    def generate_saft_xml(self, period_start: str, period_end: str) -> str:
        journal_entries = self.generate_simple_journal()
        
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<nsSAFT:AuditFile xmlns:nsSAFT="mf:nra:dgti:dxxxx:declaration:v1">',
            self._generate_header(period_start, period_end),
            self._generate_master_files(),
            self._generate_general_ledger(journal_entries),
            self._generate_source_documents(),
            '</nsSAFT:AuditFile>'
        ]
        
        return '\n'.join(xml_parts)
    
    def _clean_eik(self, eik: str) -> Optional[str]:
        cleaned = re.sub(r'[^0-9]', '', eik)
        if len(cleaned) in [9, 13]:
            return cleaned
        return None
    
    def _generate_saft_id(self, eik: Optional[str], country: str) -> str:
        if country == 'BG' and eik:
            return f"10{eik}"
        if not eik:
            import hashlib
            hash_val = hashlib.md5(str(hash(eik)).encode()).hexdigest()[:10]
            return f"15{hash_val}"
        return f"13{eik}"
    
    def _generate_header(self, period_start: str, period_end: str) -> str:
        return f'''
    <nsSAFT:Header>
        <nsSAFT:TaxAccountingBasis>A</nsSAFT:TaxAccountingBasis>
        <nsSAFT:CompanyName>{self.company_name}</nsSAFT:CompanyName>
        <nsSAFT:CompanyID>10{self.company_eik}</nsSAFT:CompanyID>
        <nsSAFT:DateCreated>{self._today()}</nsSAFT:DateCreated>
        <nsSAFT:CurrencyCode>BGN</nsSAFT:CurrencyCode>
        <nsSAFT:SelectionStartDate>{period_start}</nsSAFT:SelectionStartDate>
        <nsSAFT:SelectionEndDate>{period_end}</nsSAFT:SelectionEndDate>
        <nsSAFT:SoftwareID>SIMPLIFIED</nsSAFT:SoftwareID>
    </nsSAFT:Header>'''
    
    def _generate_master_files(self) -> str:
        parts = ['<nsSAFT:MasterFilesMonthly>']
        
        parts.append('<nsSAFT:GeneralLedgerAccounts>')
        for code, name in [('411', 'Клиенти'), ('401', 'Доставчици'), 
                           ('602', 'Разходи'), ('702', 'Приходи')]:
            parts.append(f'''
            <nsSAFT:Account>
                <nsSAFT:AccountID>{code}</nsSAFT:AccountID>
                <nsSAFT:AccountDescription>{name}</nsSAFT:AccountDescription>
                <nsSAFT:TaxpayerAccountID>{code}</nsSAFT:TaxpayerAccountID>
                <nsSAFT:AccountType>Bifunctional</nsSAFT:AccountType>
            </nsSAFT:Account>''')
        parts.append('</nsSAFT:GeneralLedgerAccounts>')
        
        parts.append('<nsSAFT:Customers>')
        for saft_id, cp in self.counterparts.items():
            parts.append(f'''
            <nsSAFT:Customer>
                <nsSAFT:CustomerID>{saft_id}</nsSAFT:CustomerID>
                <nsSAFT:CompanyStructure>
                    <nsSAFT:Name>{cp.name}</nsSAFT:Name>
                </nsSAFT:CompanyStructure>
                <nsSAFT:AccountID>411</nsSAFT:AccountID>
            </nsSAFT:Customer>''')
        parts.append('</nsSAFT:Customers>')
        
        parts.append('</nsSAFT:MasterFilesMonthly>')
        return '\n'.join(parts)
    
    def _generate_general_ledger(self, entries: list) -> str:
        parts = ['<nsSAFT:GeneralLedgerEntries>']
        
        total_debit = sum(
            float(line.get('debit', 0) or 0) 
            for e in entries for line in e['lines']
        )
        total_credit = sum(
            float(line.get('credit', 0) or 0) 
            for e in entries for line in e['lines']
        )
        
        parts.append(f'<nsSAFT:NumberOfEntries>{len(entries)}</nsSAFT:NumberOfEntries>')
        parts.append(f'<nsSAFT:TotalDebit>{total_debit:.2f}</nsSAFT:TotalDebit>')
        parts.append(f'<nsSAFT:TotalCredit>{total_credit:.2f}</nsSAFT:TotalCredit>')
        
        for entry in entries:
            parts.append('<nsSAFT:Journal>')
            parts.append(f'<nsSAFT:Transaction>')
            parts.append(f'<nsSAFT:TransactionID>{entry["entry_number"]}</nsSAFT:TransactionID>')
            parts.append(f'<nsSAFT:TransactionDate>{entry["date"]}</nsSAFT:TransactionDate>')
            parts.append(f'<nsSAFT:Description>{entry["description"]}</nsSAFT:Description>')
            
            for line in entry['lines']:
                parts.append('<nsSAFT:TransactionLine>')
                parts.append(f'<nsSAFT:AccountID>{line["account"]}</nsSAFT:AccountID>')
                parts.append(f'<nsSAFT:TaxpayerAccountID>{line["account"]}</nsSAFT:TaxpayerAccountID>')
                if line.get('counterpart'):
                    parts.append(f'<nsSAFT:CustomerID>{line["counterpart"]}</nsSAFT:CustomerID>')
                if line.get('debit'):
                    parts.append(f'<nsSAFT:DebitAmount><nsSAFT:Amount>{line["debit"]:.2f}</nsSAFT:Amount></nsSAFT:DebitAmount>')
                if line.get('credit'):
                    parts.append(f'<nsSAFT:CreditAmount><nsSAFT:Amount>{line["credit"]:.2f}</nsSAFT:Amount></nsSAFT:CreditAmount>')
                parts.append('</nsSAFT:TransactionLine>')
            
            parts.append('</nsSAFT:Transaction>')
            parts.append('</nsSAFT:Journal>')
        
        parts.append('</nsSAFT:GeneralLedgerEntries>')
        return '\n'.join(parts)
    
    def _generate_source_documents(self) -> str:
        return '<nsSAFT:SourceDocumentsMonthly><nsSAFT:SalesInvoices></nsSAFT:SalesInvoices></nsSAFT:SourceDocumentsMonthly>'
    
    def _today(self) -> str:
        from datetime import date
        return date.today().isoformat()

if __name__ == '__main__':
    gen = SimplifiedSaftGenerator('123456789', 'Моята фирма')
    
    cp1 = gen.add_counterpart('Клиент ООД', '987654321')
    cp2 = gen.add_counterpart('Малък клиент')  # Без ЕИК
    
    gen.add_sale(cp1, '001', '2026-01-15', Decimal('120.00'))
    gen.add_sale(cp2, '002', '2026-01-20', Decimal('50.00'))
    
    gen.add_expense(cp2, 'R-001', '2026-01-10', Decimal('30.00'), 'Разходи за материали')
    
    xml = gen.generate_saft_xml('2026-01-01', '2026-01-31')
    print(xml[:1000])
```

## 11.5. Резюме на казусите

Всеки казус показва различни аспекти на SAF-T имплементацията:

| Тип фирма | Основно предизвикателство | Ключово решение |
|-----------|--------------------------|-----------------|
| Търговец | Дублирани продукти, UOM | Дедупликация, нормализация |
| Производител | Сложни ДДС схеми | VIES, класификатор |
| Холдинг | Междуфирмени транзакции | Консолидация, елиминации |
| ЕТ | Ограничени ресурси | Опростен pipeline |

## 11.6. Данъчни рискови индикатори: Какво вижда НАП, когато отвори файла

### Защо тази секция е тук

Номенклатурчиците от обучителните центрове обичат да повтарят, че SAF-T е „само административен ангажимент". Не е. SAF-T е **рентген на счетоводната политика** — и НАП ще го чете като рентген, не като декларация. Всяко решение, което счетоводителят е взел през годината — полезен живот на актив, обезценка на вземане, отписване на запас — вече не е скрито в папка на рафта. То е в XML, машинночетимо, сравнимо с десетки хиляди други фирми.

Тази секция не е за това как да „скриете" нещо. Точно обратното — тя е за това **какви сигнали вашите данни излъчват**, за да можете да ги видите преди НАП.

### 11.6.1. Активи и амортизации: Полезният живот като рисков сигнал

Когато НАП отвори `SourceDocuments > AssetTransactions` и `MasterFiles > PhysicalStock`, първото нещо, което алгоритъмът ще направи, е да сравни **счетоводния полезен живот** с **данъчно признатите норми** по чл. 55 от ЗКПО.

**Какво „свети" в червено:**

- Сграда с полезен живот 10 години (данъчна норма: 25 години / 4%)
- Компютър с полезен живот 10 години (данъчна норма: 2 години / 50%)
- Автомобил, амортизиран за 2 години (данъчна норма: ~6.5 години / 15%)
- Напълно амортизирани активи, които все още генерират приходи — класически въпрос „защо активът е на нула, а приходите от него растат?"
- Активи с нулева остатъчна стойност, но без отписване

**Защо е проблем:** Агресивната счетоводна амортизация (по-кратък полезен живот от данъчния) създава **данъчна временна разлика**, която трябва да е отразена в ГДД и в данъчния амортизационен план (ДАП). Ако SAF-T показва счетоводна амортизация 50 000 лв., а ДАП-ът признава 20 000 лв., разликата от 30 000 лв. трябва да увеличи финансовия резултат. Ако не е увеличен — имате проблем.

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class AssetRiskIndicator:
    asset_id: str
    description: str
    accounting_useful_life: int      # Счетоводен полезен живот (месеци)
    tax_useful_life: int             # Данъчен полезен живот (месеци)
    acquisition_value: Decimal
    accumulated_depreciation: Decimal
    annual_depreciation: Decimal
    revenue_generated: Decimal       # Приходи, свързани с актива
    risk_score: int                  # 0-100
    risk_flags: list[str]

# Данъчни амортизационни норми по ЗКПО чл. 55
ZKPO_TAX_RATES = {
    'I':   Decimal('0.04'),    # Сгради, конструкции — 4% (25 г.)
    'II':  Decimal('0.30'),    # Машини, оборудване — 30% (3.3 г.)
    'III': Decimal('0.10'),    # Транспортни средства — 10% (10 г.) / ≤ 15%
    'IV':  Decimal('0.50'),    # Компютри, софтуер — 50% (2 г.)
    'V':   Decimal('0.25'),    # Други — 25% (4 г.)
    'VI':  Decimal('0.15'),    # Автомобили — 15% (6.67 г.)
    'VII': Decimal('0.10'),    # Данъчни амортизируеми нематериални — 10%
}

def analyze_asset_risks(
    assets: list[dict],
    revenue_by_asset: dict[str, Decimal]
) -> list[AssetRiskIndicator]:
    """Анализира активите за рискови индикатори."""

    results = []

    for asset in assets:
        flags = []
        score = 0

        asset_id = asset['asset_id']
        acq_value = Decimal(str(asset['acquisition_value']))
        acc_depr = Decimal(str(asset['accumulated_depreciation']))
        annual_depr = Decimal(str(asset['annual_depreciation']))
        acct_life_months = asset['accounting_useful_life_months']
        tax_category = asset.get('tax_category', 'V')

        # 1. Полезен живот: счетоводен vs данъчен
        tax_rate = ZKPO_TAX_RATES.get(tax_category, Decimal('0.25'))
        tax_life_months = int(12 / float(tax_rate)) if tax_rate > 0 else 600

        if acct_life_months < tax_life_months * 0.5:
            flags.append(f"Агресивна амортизация: счетоводен живот "
                        f"{acct_life_months} мес. < 50% от данъчен {tax_life_months} мес.")
            score += 30
        elif acct_life_months < tax_life_months * 0.75:
            flags.append(f"Ускорена амортизация: {acct_life_months} мес. vs данъчен {tax_life_months} мес.")
            score += 15

        # 2. Напълно амортизиран, но генерира приходи
        net_book_value = acq_value - acc_depr
        revenue = revenue_by_asset.get(asset_id, Decimal('0'))

        if net_book_value <= 0 and revenue > 0:
            flags.append(f"Нулева балансова стойност, но приходи {revenue:.2f} лв.")
            score += 25

        # 3. Напълно амортизиран, но не отписан
        if net_book_value <= 0 and annual_depr == 0 and acq_value > 0:
            flags.append("Напълно амортизиран актив без отписване")
            score += 10

        # 4. Несъответствие между амортизация и отчетени разходи
        expected_annual = acq_value * tax_rate
        if annual_depr > 0 and annual_depr > expected_annual * Decimal('1.5'):
            diff = annual_depr - expected_annual
            flags.append(f"Годишна амортизация {annual_depr:.2f} лв. надвишава "
                        f"данъчно признатата {expected_annual:.2f} лв. с {diff:.2f} лв.")
            score += 20

        if flags:
            results.append(AssetRiskIndicator(
                asset_id=asset_id,
                description=asset.get('description', ''),
                accounting_useful_life=acct_life_months,
                tax_useful_life=tax_life_months,
                acquisition_value=acq_value,
                accumulated_depreciation=acc_depr,
                annual_depreciation=annual_depr,
                revenue_generated=revenue,
                risk_score=min(score, 100),
                risk_flags=flags,
            ))

    results.sort(key=lambda r: r.risk_score, reverse=True)
    return results
```

### 11.6.2. Несъбираеми вземания и „вечни" салда по разчетни сметки

SAF-T съдържа `GeneralLedgerEntries` с пълна хронология по сметки от група 41x (Клиенти) и 40x (Доставчици), заедно с `CustomerID`/`SupplierID`. Когато НАП види, че едно вземане стои 3+ години без движение, автоматично възниква въпрос: **защо не е обезценено?**

**Какво „свети" в червено:**

- Вземания от клиенти на възраст > 3 години без частично плащане
- Задължения към доставчици, висящи 5+ години (защо не са платени? Защо не са отписани?)
- Салда по разчетни сметки с контрагенти, които вече не съществуват (заличени от ТР)
- Обезценка, направена точно преди подаване на ГДД — „козметична" обезценка
- Разчети с „неизвестни" контрагенти (липсващ ЕИК, фиктивен SAF-T ID)

**Данъчният риск:** По чл. 34-37 от ЗКПО, обезценките на вземания не са данъчно признати при начисляването им, а при настъпване на конкретни обстоятелства (изтекъл давностен срок, несъстоятелност, заличаване). „Вечните" салда подсказват или пропусната обезценка (изкривен баланс), или умишлено задържане (избягване на данъчен ефект при отписване).

```python
from datetime import date, timedelta

@dataclass
class StaleBalanceIndicator:
    counterpart_id: str
    counterpart_name: str
    account: str
    balance: Decimal
    last_movement_date: Optional[date]
    age_days: int
    risk_flags: list[str]
    risk_score: int

def analyze_stale_balances(
    ledger_entries: list[dict],
    counterparts: dict[str, dict],
    report_date: date,
) -> list[StaleBalanceIndicator]:
    """Открива „вечни" салда по разчетни сметки."""

    # Групиране по контрагент + сметка
    balances: dict[tuple[str, str], dict] = {}

    RECEIVABLE_ACCOUNTS = {'411', '412', '413', '414', '419'}
    PAYABLE_ACCOUNTS = {'401', '402', '403', '404', '409'}
    WATCHLIST = RECEIVABLE_ACCOUNTS | PAYABLE_ACCOUNTS

    for entry in ledger_entries:
        for line in entry.get('lines', []):
            acct = line.get('account', '')[:3]
            cp_id = line.get('counterpart_id')

            if acct not in WATCHLIST or not cp_id:
                continue

            key = (cp_id, acct)
            if key not in balances:
                balances[key] = {
                    'balance': Decimal('0'),
                    'last_date': None,
                    'movement_count': 0,
                }

            debit = Decimal(str(line.get('debit', 0) or 0))
            credit = Decimal(str(line.get('credit', 0) or 0))
            entry_date = entry.get('date')

            balances[key]['balance'] += debit - credit
            balances[key]['movement_count'] += 1

            if entry_date:
                d = date.fromisoformat(entry_date) if isinstance(entry_date, str) else entry_date
                if balances[key]['last_date'] is None or d > balances[key]['last_date']:
                    balances[key]['last_date'] = d

    results = []

    for (cp_id, acct), data in balances.items():
        if abs(data['balance']) < Decimal('0.01'):
            continue

        flags = []
        score = 0

        last_date = data['last_date']
        age_days = (report_date - last_date).days if last_date else 9999

        # 1. Възраст на салдото
        if age_days > 365 * 5:
            flags.append(f"Салдо без движение > 5 години ({age_days} дни)")
            score += 40
        elif age_days > 365 * 3:
            flags.append(f"Салдо без движение > 3 години ({age_days} дни)")
            score += 25
        elif age_days > 365 * 2:
            flags.append(f"Салдо без движение > 2 години ({age_days} дни)")
            score += 10

        # 2. Контрагент без валиден ЕИК
        cp = counterparts.get(cp_id, {})
        if not cp.get('eik') or cp.get('saft_id', '').startswith('15'):
            flags.append("Контрагент без валиден ЕИК")
            score += 15

        # 3. Значителна сума без движение
        if abs(data['balance']) > Decimal('10000') and age_days > 365:
            flags.append(f"Значително салдо {data['balance']:.2f} лв. без движение > 1 г.")
            score += 20

        # 4. Само едно движение (вероятно начално салдо)
        if data['movement_count'] == 1 and age_days > 365:
            flags.append("Еднократно движение — вероятно нерегулирано начално салдо")
            score += 15

        if flags:
            results.append(StaleBalanceIndicator(
                counterpart_id=cp_id,
                counterpart_name=cp.get('name', 'Неизвестен'),
                account=acct,
                balance=data['balance'],
                last_movement_date=last_date,
                age_days=age_days,
                risk_flags=flags,
                risk_score=min(score, 100),
            ))

    results.sort(key=lambda r: r.risk_score, reverse=True)
    return results
```

### 11.6.3. Запаси: Отписвания, обезценки и „вечни" наличности

SAF-T секция `PhysicalStock` (при On Demand) и `MovementOfGoods` дават пълна картина на складовите наличности. НАП може да сравни:

- Наличности в началото на периода + покупки − продажби = **очаквано крайно салдо**
- Ако реалното крайно салдо е по-ниско — трябва да има **документирано отписване**
- Ако е по-високо — трябва да има **заприходяване** (излишъци)

**Какво „свети" в червено:**

- Запаси, които не са се „мръднали" 12+ месеца — класически кандидат за обезценка по СС 2
- Масови отписвания в края на годината (декемврийски „чистки") — алгоритъмът ще забележи сезонността
- Стоки с отрицателни количества (продадено повече от наличното — липса на складова дисциплина)
- Несъответствие между `PhysicalStock` и сметка 30x в `GeneralLedgerEntries`
- Обезценка на запаси без последващо движение (обезценено, но нито продадено, нито бракувано)

**Данъчният риск:** Отписаните запаси са данъчно признат разход **само** при документална обоснованост (протокол за брак, акт за липси, решение на управителя). Масови отписвания без документация = увеличение на финансовия резултат + ДДС корекция по чл. 79 от ЗДДС.

```python
@dataclass
class InventoryRiskIndicator:
    product_id: str
    product_name: str
    quantity_on_hand: Decimal
    last_movement_date: Optional[date]
    days_without_movement: int
    total_write_offs_year: Decimal
    write_off_months: list[int]       # В кои месеци са отписвани
    ledger_value: Decimal             # Стойност по сметка 30x
    stock_value: Decimal              # Стойност по PhysicalStock
    risk_flags: list[str]
    risk_score: int

def analyze_inventory_risks(
    stock_items: list[dict],
    movements: list[dict],
    ledger_balances: dict[str, Decimal],
    report_date: date,
) -> list[InventoryRiskIndicator]:
    """Анализира складови наличности за рискови индикатори."""

    results = []

    for item in stock_items:
        flags = []
        score = 0
        product_id = item['product_id']
        qty = Decimal(str(item.get('quantity', 0)))
        value = Decimal(str(item.get('value', 0)))

        # Движения за този продукт
        item_movements = [m for m in movements if m.get('product_id') == product_id]

        # Последно движение
        if item_movements:
            dates = [date.fromisoformat(m['date']) if isinstance(m['date'], str)
                     else m['date'] for m in item_movements]
            last_move = max(dates)
            days_idle = (report_date - last_move).days
        else:
            last_move = None
            days_idle = 9999

        # 1. Залежали запаси (без движение)
        if days_idle > 365:
            flags.append(f"Без движение {days_idle} дни — кандидат за обезценка по СС 2")
            score += 25
        if days_idle > 730:
            score += 15  # Допълнително за > 2 години

        # 2. Отрицателни количества
        if qty < 0:
            flags.append(f"Отрицателно количество: {qty} — продадено повече от наличното")
            score += 35

        # 3. Масови отписвания в края на годината
        write_offs = [m for m in item_movements
                      if m.get('movement_type') in ('write_off', 'scrap', 'loss', 'брак', 'липса')]
        write_off_total = sum(Decimal(str(m.get('value', 0))) for m in write_offs)
        write_off_months = []
        for wo in write_offs:
            d = date.fromisoformat(wo['date']) if isinstance(wo['date'], str) else wo['date']
            write_off_months.append(d.month)

        december_write_offs = sum(1 for m in write_off_months if m == 12)
        if december_write_offs > 0 and len(write_offs) > 0:
            dec_ratio = december_write_offs / len(write_offs)
            if dec_ratio > 0.6:
                flags.append(f"Декемврийски чистки: {december_write_offs}/{len(write_offs)} "
                            f"отписвания са в м.12 ({write_off_total:.2f} лв.)")
                score += 20

        # 4. Несъответствие между складова и счетоводна стойност
        ledger_key = f"30x:{product_id}"
        ledger_val = ledger_balances.get(ledger_key, value)
        if abs(value - ledger_val) > Decimal('0.01') and value > 0:
            diff_pct = abs(value - ledger_val) / value * 100
            if diff_pct > 5:
                flags.append(f"Разлика склад/книга: {value:.2f} vs {ledger_val:.2f} "
                            f"({diff_pct:.1f}%)")
                score += 20

        if flags:
            results.append(InventoryRiskIndicator(
                product_id=product_id,
                product_name=item.get('description', ''),
                quantity_on_hand=qty,
                last_movement_date=last_move,
                days_without_movement=days_idle,
                total_write_offs_year=write_off_total,
                write_off_months=write_off_months,
                ledger_value=ledger_val,
                stock_value=value,
                risk_flags=flags,
                risk_score=min(score, 100),
            ))

    results.sort(key=lambda r: r.risk_score, reverse=True)
    return results
```

### 11.6.4. Разходи със смесено ползване: Невидимият капан

Това е може би най-подценяваният риск. В SAF-T всеки разход е свързан със сметка, контрагент и (ако има) данъчен код. Когато фирма осчетоводява **100% от разходите за автомобил, телефон, наем или командировки**, без аналитичност за лично/служебно ползване, алгоритъмът на НАП може да направи проста проверка:

**Какво „свети" в червено:**

- Разходи за горива (сметка 602/601) без пътни листове или GPS данни — пълен данъчен кредит при 100% лично ползване?
- Наем на имот, осчетоводен 100% като разход, но имотът се ползва и за жилище
- Телекомуникационни разходи без разделяне лично/служебно
- Командировъчни разходи без заповеди за командировка
- Представителни разходи над 1% от приходите

**Данъчният риск:** По чл. 204, ал. 1, т. 4 от ЗКПО разходите в натура, свързани с лично ползване, се облагат с данък върху разходите (10%). Ако няма разделяне — НАП може да приеме, че **целият разход е за лично ползване**.

```python
@dataclass
class MixedUseExpenseIndicator:
    account: str
    account_name: str
    total_amount: Decimal
    counterparts: list[str]
    has_analytics: bool          # Има ли аналитичност лично/служебно
    personal_use_ratio: Optional[Decimal]  # Деклариран % лично ползване
    risk_flags: list[str]
    risk_score: int

# Сметки, типично свързани със смесено ползване
MIXED_USE_ACCOUNTS = {
    '6021': 'Горива и смазочни материали',
    '6022': 'Резервни части',
    '602':  'Разходи за материали',
    '609':  'Други разходи за дейността',
    '601':  'Разходи за суровини и материали',
    '614':  'Разходи за телекомуникации',
    '613':  'Разходи за наеми',
    '616':  'Разходи за застраховки',
    '617':  'Разходи за командировки',
    '618':  'Разходи за представителни цели',
}

def analyze_mixed_use_expenses(
    journal_entries: list[dict],
    company_revenue: Decimal,
    analytics_available: dict[str, bool],
) -> list[MixedUseExpenseIndicator]:
    """Идентифицира разходи със смесено ползване без аналитичност."""

    # Агрегиране по сметка
    account_totals: dict[str, dict] = {}

    for entry in journal_entries:
        for line in entry.get('lines', []):
            acct = line.get('account', '')
            # Проверка дали сметката е в списъка (точно съвпадение или по първи 3 цифри)
            matched_acct = None
            if acct in MIXED_USE_ACCOUNTS:
                matched_acct = acct
            elif acct[:3] in MIXED_USE_ACCOUNTS:
                matched_acct = acct[:3]

            if not matched_acct:
                continue

            debit = Decimal(str(line.get('debit', 0) or 0))
            if debit <= 0:
                continue

            if matched_acct not in account_totals:
                account_totals[matched_acct] = {
                    'total': Decimal('0'),
                    'counterparts': set(),
                }

            account_totals[matched_acct]['total'] += debit
            cp = line.get('counterpart_id', '')
            if cp:
                account_totals[matched_acct]['counterparts'].add(cp)

    results = []

    for acct, data in account_totals.items():
        flags = []
        score = 0

        has_analytics = analytics_available.get(acct, False)
        acct_name = MIXED_USE_ACCOUNTS.get(acct, f'Сметка {acct}')

        # 1. Няма аналитичност за лично/служебно
        if not has_analytics:
            flags.append(f"Няма аналитичност лично/служебно за {acct_name}")
            score += 25

        # 2. Представителни разходи > 1% от приходите
        if acct in ('618',) and company_revenue > 0:
            ratio = data['total'] / company_revenue * 100
            if ratio > 1:
                flags.append(f"Представителни разходи {ratio:.2f}% от приходите "
                            f"(над типичния праг)")
                score += 20

        # 3. Горива без аналитичност — висок риск
        if acct in ('6021', '602') and not has_analytics:
            flags.append("Горива без пътни листове / GPS аналитичност")
            score += 20

        # 4. Значителни суми
        if data['total'] > Decimal('50000'):
            flags.append(f"Значителна сума: {data['total']:.2f} лв.")
            score += 10

        if flags:
            results.append(MixedUseExpenseIndicator(
                account=acct,
                account_name=acct_name,
                total_amount=data['total'],
                counterparts=list(data['counterparts'])[:10],
                has_analytics=has_analytics,
                personal_use_ratio=None,
                risk_flags=flags,
                risk_score=min(score, 100),
            ))

    results.sort(key=lambda r: r.risk_score, reverse=True)
    return results
```

### 11.6.5. Обобщен Risk Score: Всичко в едно число

В реалния свят НАП няма да гледа всеки индикатор поотделно. Ще има **композитен risk score** — едно число, което определя дали фирмата влиза в списъка за проверка. Ето как можете да изчислите вашия собствен, преди те да го направят:

```python
@dataclass
class CompanyRiskProfile:
    company_id: str
    company_name: str
    total_risk_score: int
    risk_category: str            # LOW / MEDIUM / HIGH / CRITICAL
    asset_risks: int              # Брой рискови индикатори
    stale_balance_risks: int
    inventory_risks: int
    mixed_use_risks: int
    top_flags: list[str]          # Топ 5 най-тежки сигнали

def calculate_company_risk_profile(
    company_id: str,
    company_name: str,
    asset_indicators: list[AssetRiskIndicator],
    balance_indicators: list[StaleBalanceIndicator],
    inventory_indicators: list[InventoryRiskIndicator],
    expense_indicators: list[MixedUseExpenseIndicator],
) -> CompanyRiskProfile:
    """Обобщен рисков профил на фирмата."""

    # Претеглени средни стойности по категория
    def weighted_avg(indicators, weight):
        if not indicators:
            return 0
        avg = sum(i.risk_score for i in indicators) / len(indicators)
        return int(avg * weight)

    asset_score = weighted_avg(asset_indicators, 0.30)
    balance_score = weighted_avg(balance_indicators, 0.25)
    inventory_score = weighted_avg(inventory_indicators, 0.25)
    expense_score = weighted_avg(expense_indicators, 0.20)

    total = asset_score + balance_score + inventory_score + expense_score

    # Категоризация
    if total >= 70:
        category = "CRITICAL"
    elif total >= 45:
        category = "HIGH"
    elif total >= 25:
        category = "MEDIUM"
    else:
        category = "LOW"

    # Топ 5 сигнали
    all_flags = []
    for ind in asset_indicators:
        all_flags.extend([(ind.risk_score, f) for f in ind.risk_flags])
    for ind in balance_indicators:
        all_flags.extend([(ind.risk_score, f) for f in ind.risk_flags])
    for ind in inventory_indicators:
        all_flags.extend([(ind.risk_score, f) for f in ind.risk_flags])
    for ind in expense_indicators:
        all_flags.extend([(ind.risk_score, f) for f in ind.risk_flags])

    all_flags.sort(key=lambda x: x[0], reverse=True)
    top_flags = [f[1] for f in all_flags[:5]]

    return CompanyRiskProfile(
        company_id=company_id,
        company_name=company_name,
        total_risk_score=min(total, 100),
        risk_category=category,
        asset_risks=len(asset_indicators),
        stale_balance_risks=len(balance_indicators),
        inventory_risks=len(inventory_indicators),
        mixed_use_risks=len(expense_indicators),
        top_flags=top_flags,
    )
```

### 11.6.6. Какво да направите с тази информация

Преди да подадете SAF-T, пуснете горните скриптове върху собствените си данни. Ако виждате `CRITICAL` или `HIGH` — **не подавайте, докато не изчистите**. Не защото ще ви глобят за подаване на верни данни, а защото:

1. **Данните са верни, но картината е изкривена** — агресивна амортизация без данъчна корекция не е счетоводна грешка, а данъчно нарушение.
2. **„Вечните" салда не са технически проблем** — те са индикатор за пропуснати счетоводни операции (обезценки, отписвания), които имат данъчен ефект.
3. **Липсата на аналитичност не е оправдание** — тя е самият проблем. САФ-Т ще покаже, че нямате разделяне, а НАП ще приеме най-лошия за вас вариант.

> **Правило номер едно: Ако не искате НАП да намери проблем, не го създавайте. А ако сте го създали — поправете го преди да го подадете в XML.**

## 11.7. Голямата стратегическа грешка: Каруцата пред коня

В края на този практически преглед е важно да назовем „слона в стаята“ – фундаменталната стратегическа грешка на НАП и Министерството на финансите, която заплашва да превърне SAF-T в дигитален вариант на „битката при Ватерло“.

### Липсващото звено: Електронното фактуриране

Всяка държава, която успешно е внедрила SAF-T (като Италия, Румъния или Полша), следва логическа последователност, която у нас беше прескочена: **първо се въвежда задължително електронно фактуриране (B2B/B2G) през централизиран хъб, а след това – SAF-T.**

Не можеш да искаш от бизнеса да ти даде **детайлен рентген (SAF-T)** на скелета си, преди да си го научил да не си чупи костите при **дишане (фактурирането)**.

1. **Електронната фактура е структуриран носител на данни (XML/UBL)**. Ако тя влиза в системата автоматично, тя попълва номенклатура, данъчна ставка и контрагент с 100% точност. SAF-T тогава е просто един бутон „Export“.
2. **Абсурдът на OCR и ръчното въвеждане**: В момента НАП изисква SAF-T **ред по ред** (Item level detail). В същото време 80% от бизнеса получава фактури на хартия или PDF. Никое AI не може да гарантира 100% точност при сканиране на хиляди редове, а ръчното въвеждане е икономическо самоубийство за счетоводните кантори.

### Дигитален боклук (Digital Garbage)

Понеже няма централизиран хъб за фактури, всяка фирма „твори“ в своя софтуер. Фирма А ще пише „Брашно 1кг“ с един код, а Фирма Б (купувачът) ще го заведе като „Стока“ с друг код. Когато НАП се опита да засече тези два SAF-T файла, те **няма да съвпаднат**. Системата ще гърми с фалшиви сигнали за измами, просто защото данните не са били структурирани в момента на раждането им.

> **„Присъдата е ясна: НАП сложи каруцата пред коня. Опитаха се да построят покрива (SAF-T), преди да са излели основите (Електронното фактуриране). Без централизиран хъб за обмен на структурирани данни, SAF-T остава една невъзможна фантазия, която ще роди само хаос, глоби и празни XML файлове. Докато държавата не разбере, че данните се управляват при източника, а не при отчета, проектът ще бъде паметник на административната некомпетентност.“**

## 11.8. Заключение

Урокът е ясен: **няма едно решение за всички**. SAF-T имплементацията трябва да се адаптира към спецификите на бизнеса, но без здрава основа от структурирани данни, тя остава упражнение по безсмислена бюрокрация.
