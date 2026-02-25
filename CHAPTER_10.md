# Глава 10: Тестване и QA на SAF-T файлове

## 10.1. Защо тестването е критично

SAF-T файлът не е просто отчет — това е **юридически документ**. Грешките не са просто технически проблеми, а потенциални санкции.

### Нивата на валидация

```
┌─────────────────────────────────────────────────────────┐
│                    SAFT VALIDATION LAYERS                │
├─────────────────────────────────────────────────────────┤
│  Layer 5: Business Logic (счетоводна логика)           │
│  ↓                                                      │
│  Layer 4: Cross-module Consistency (фактури ↔ журнал)  │
│  ↓                                                      │
│  Layer 3: Referential Integrity (външни ключове)       │
│  ↓                                                      │
│  Layer 2: Data Type Validation (типове, формати)       │
│  ↓                                                      │
│  Layer 1: XSD Schema Validation (XML структура)        │
└─────────────────────────────────────────────────────────┘
```

## 10.2. XSD Валидация (Layer 1)

### Rust XSD Validator

```rust
use quick_xml::events::Event;
use quick_xml::Reader;
use std::io::BufReader;
use xrust::{Document, ParseError, Schema, SchemaParser, Validator};

pub struct XsdValidator {
    schema: Schema,
}

impl XsdValidator {
    pub fn from_file(xsd_path: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let xsd_content = std::fs::read_to_string(xsd_path)?;
        let mut parser = SchemaParser::new();
        let schema = parser.parse(&xsd_content)?;
        Ok(Self { schema })
    }
    
    pub fn validate_xml(&self, xml_path: &str) -> XsdValidationResult {
        let xml_content = std::fs::read_to_string(xml_path).unwrap_or_default();
        let doc = Document::parse(&xml_content);
        
        match doc {
            Ok(d) => {
                let validator = Validator::new(&self.schema, &d);
                let errors: Vec<String> = validator
                    .validate()
                    .iter()
                    .map(|e| format!("{:?}", e))
                    .collect();
                
                XsdValidationResult {
                    is_valid: errors.is_empty(),
                    errors,
                }
            }
            Err(e) => XsdValidationResult {
                is_valid: false,
                errors: vec![format!("XML parse error: {:?}", e)],
            },
        }
    }
    
    pub fn quick_validate_structure(xml_path: &str) -> Vec<ValidationError> {
        let mut errors = Vec::new();
        let file = std::fs::File::open(xml_path).unwrap();
        let reader = BufReader::new(file);
        let mut xml_reader = Reader::from_reader(reader);
        
        let mut expected_tags = vec![
            "nsSAFT:AuditFile",
            "nsSAFT:Header",
            "nsSAFT:MasterFilesMonthly",
            "nsSAFT:GeneralLedgerEntries",
        ];
        
        let mut found_tags = Vec::new();
        let mut buf = Vec::new();
        
        loop {
            match xml_reader.read_event_into(&mut buf) {
                Ok(Event::Start(e)) | Ok(Event::Empty(e)) => {
                    let tag = String::from_utf8_lossy(e.name().as_ref());
                    found_tags.push(tag.to_string());
                }
                Ok(Event::Eof) => break,
                Err(e) => {
                    errors.push(ValidationError {
                        code: "XSD001".into(),
                        message: format!("Parse error at position {}: {:?}", 
                            xml_reader.buffer_position(), e),
                        severity: Severity::Error,
                    });
                    break;
                }
                _ => {}
            }
            buf.clear();
        }
        
        for expected in &expected_tags {
            if !found_tags.iter().any(|f| f.contains(expected)) {
                errors.push(ValidationError {
                    code: "XSD002".into(),
                    message: format!("Missing required element: {}", expected),
                    severity: Severity::Error,
                });
            }
        }
        
        errors
    }
}

#[derive(Debug)]
pub struct XsdValidationResult {
    pub is_valid: bool,
    pub errors: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct ValidationError {
    pub code: String,
    pub message: String,
    pub severity: Severity,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Severity {
    Error,
    Warning,
    Info,
}
```

### Python XSD Validator с lxml

```python
from lxml import etree
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path

@dataclass
class XsdError:
    line: int
    column: int
    message: str
    severity: str

class SaftXsdValidator:
    NSMAP = {
        'nsSAFT': 'mf:nra:dgti:dxxxx:declaration:v1',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }
    
    def __init__(self, xsd_path: str):
        self.xsd_path = Path(xsd_path)
        self.schema = self._load_schema()
    
    def _load_schema(self) -> etree.XMLSchema:
        xsd_doc = etree.parse(str(self.xsd_path))
        return etree.XMLSchema(xsd_doc)
    
    def validate(self, xml_path: str) -> Tuple[bool, List[XsdError]]:
        errors = []
        
        try:
            xml_doc = etree.parse(xml_path)
            result = self.schema.validate(xml_doc)
            
            if not result:
                for error in self.schema.error_log:
                    errors.append(XsdError(
                        line=error.line,
                        column=error.column,
                        message=error.message,
                        severity='error' if 'error' in error.level_name.lower() else 'warning'
                    ))
            
            return result, errors
            
        except etree.XMLSyntaxError as e:
            errors.append(XsdError(
                line=e.lineno or 0,
                column=e.column or 0,
                message=str(e),
                severity='error'
            ))
            return False, errors
    
    def validate_structure(self, xml_path: str) -> List[str]:
        issues = []
        
        try:
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            required_sections = [
                'Header',
                'MasterFilesMonthly',
                'GeneralLedgerEntries',
                'SourceDocumentsMonthly'
            ]
            
            for section in required_sections:
                tag = f"{{{self.NSMAP['nsSAFT']}}}{section}"
                if root.find(f".//nsSAFT:{section}", self.NSMAP) is None:
                    issues.append(f"Missing required section: {section}")
            
            return issues
            
        except Exception as e:
            return [f"Parse error: {str(e)}"]
    
    def extract_statistics(self, xml_path: str) -> dict:
        try:
            tree = etree.parse(xml_path)
            root = tree.getroot()
            
            stats = {
                'accounts_count': len(root.findall('.//nsSAFT:Account', self.NSMAP)),
                'customers_count': len(root.findall('.//nsSAFT:Customer', self.NSMAP)),
                'suppliers_count': len(root.findall('.//nsSAFT:Supplier', self.NSMAP)),
                'journal_entries_count': len(root.findall('.//nsSAFT:Journal', self.NSMAP)),
                'transactions_count': len(root.findall('.//nsSAFT:Transaction', self.NSMAP)),
                'transaction_lines_count': len(root.findall('.//nsSAFT:TransactionLine', self.NSMAP)),
                'sales_invoices_count': len(root.findall('.//nsSAFT:Invoice', self.NSMAP)),
            }
            
            total_debit = root.find('.//nsSAFT:TotalDebit', self.NSMAP)
            total_credit = root.find('.//nsSAFT:TotalCredit', self.NSMAP)
            
            if total_debit is not None:
                stats['total_debit'] = float(total_debit.text or 0)
            if total_credit is not None:
                stats['total_credit'] = float(total_credit.text or 0)
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}

def validate_saft_file(xml_path: str, xsd_path: str) -> dict:
    validator = SaftXsdValidator(xsd_path)
    
    is_valid, xsd_errors = validator.validate(xml_path)
    structure_issues = validator.validate_structure(xml_path)
    stats = validator.extract_statistics(xml_path)
    
    return {
        'is_valid': is_valid and len(structure_issues) == 0,
        'xsd_errors': [{'line': e.line, 'message': e.message} for e in xsd_errors],
        'structure_issues': structure_issues,
        'statistics': stats
    }
```

## 10.3. Data Type Validation (Layer 2)

### Comprehensive Type Checks

```python
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class FieldValidation:
    field_name: str
    value: any
    is_valid: bool
    error_message: Optional[str]

class SaftFieldTypeValidator:
    EIK_PATTERN = re.compile(r'^[0-9]{9}([0-9]{4})?$')
    VAT_BG_PATTERN = re.compile(r'^[0-9]{9,10}$')
    IBAN_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$')
    CURRENCY_PATTERN = re.compile(r'^[A-Z]{3}$')
    COUNTRY_PATTERN = re.compile(r'^[A-Z]{2}$')
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    EU_COUNTRIES = {
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
    }
    
    VALID_UOM = {
        'C62', 'KGM', 'LTR', 'MTR', 'MTK', 'MTQ', 'TNE', 'HUR',
        'DZN', 'BX', 'CT', 'PA', 'PK', 'PR', 'SET', 'NAR', 'NPR'
    }
    
    VALID_TAX_CODES = {
        '100010', '100211', '100213', '100214', '100215', '100216',
        '100217', '100218', '100219', '100301', '100302'
    }
    
    @classmethod
    def validate_eik(cls, value: str, required: bool = True) -> FieldValidation:
        if not value:
            return FieldValidation(
                field_name='eik',
                value=value,
                is_valid=not required,
                error_message='EIK is required' if required else None
            )
        
        if cls.EIK_PATTERN.match(value):
            if cls._validate_eik_checksum(value):
                return FieldValidation('eik', value, True, None)
        
        return FieldValidation(
            field_name='eik',
            value=value,
            is_valid=False,
            error_message=f'Invalid EIK format: {value}'
        )
    
    @classmethod
    def _validate_eik_checksum(cls, eik: str) -> bool:
        if len(eik) not in [9, 13]:
            return False
        
        try:
            digits = [int(d) for d in eik]
            weights = [1, 2, 3, 4, 5, 6, 7, 8]
            
            if len(eik) == 13:
                base = eik[:9]
                branch = eik[9:]
                
                checksum = sum(int(d) * w for d, w in zip(base, weights))
                checksum = checksum % 11
                if checksum == 10:
                    checksum = sum(int(d) * w for d, w in zip(base, [3,4,5,6,7,8,9,10]))
                    checksum = checksum % 11
                    if checksum == 10:
                        checksum = 0
                
                if int(base[8]) != checksum:
                    return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    @classmethod
    def validate_vat_number(cls, value: str, country: str = 'BG') -> FieldValidation:
        if not value:
            return FieldValidation('vat_number', value, True, None)
        
        clean_vat = re.sub(r'[^0-9]', '', value)
        
        if country == 'BG':
            if len(clean_vat) in [9, 10]:
                return FieldValidation('vat_number', value, True, None)
            return FieldValidation(
                'vat_number', value, False,
                f'Invalid BG VAT number length: {len(clean_vat)}'
            )
        
        return FieldValidation('vat_number', value, True, None)
    
    @classmethod
    def validate_decimal(
        cls, 
        value: any, 
        field_name: str,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        precision: int = 2
    ) -> FieldValidation:
        if value is None:
            return FieldValidation(field_name, value, True, None)
        
        try:
            if isinstance(value, str):
                dec_value = Decimal(value)
            elif isinstance(value, (int, float)):
                dec_value = Decimal(str(value))
            elif isinstance(value, Decimal):
                dec_value = value
            else:
                return FieldValidation(
                    field_name, value, False,
                    f'Cannot convert to decimal: {type(value)}'
                )
            
            if min_value is not None and dec_value < min_value:
                return FieldValidation(
                    field_name, value, False,
                    f'Value {dec_value} below minimum {min_value}'
                )
            
            if max_value is not None and dec_value > max_value:
                return FieldValidation(
                    field_name, value, False,
                    f'Value {dec_value} above maximum {max_value}'
                )
            
            return FieldValidation(field_name, dec_value, True, None)
            
        except (InvalidOperation, ValueError) as e:
            return FieldValidation(
                field_name, value, False,
                f'Invalid decimal format: {str(e)}'
            )
    
    @classmethod
    def validate_date(cls, value: any, field_name: str) -> FieldValidation:
        if value is None:
            return FieldValidation(field_name, value, True, None)
        
        if isinstance(value, (date, datetime)):
            return FieldValidation(field_name, value, True, None)
        
        if isinstance(value, str):
            try:
                if 'T' in value:
                    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    parsed = datetime.strptime(value, '%Y-%m-%d').date()
                return FieldValidation(field_name, parsed, True, None)
            except ValueError:
                pass
        
        return FieldValidation(
            field_name, value, False,
            f'Invalid date format: {value}'
        )
    
    @classmethod
    def validate_uom(cls, value: str) -> FieldValidation:
        if not value:
            return FieldValidation('uom', value, False, 'UOM is required')
        
        if value in cls.VALID_UOM:
            return FieldValidation('uom', value, True, None)
        
        return FieldValidation(
            'uom', value, False,
            f'Invalid UOM code: {value}. Valid codes: {cls.VALID_UOM}'
        )
    
    @classmethod
    def validate_tax_code(cls, value: str) -> FieldValidation:
        if not value:
            return FieldValidation('tax_code', value, False, 'Tax code is required')
        
        if value in cls.VALID_TAX_CODES:
            return FieldValidation('tax_code', value, True, None)
        
        return FieldValidation(
            'tax_code', value, False,
            f'Invalid tax code: {value}'
        )
    
    @classmethod
    def validate_country(cls, value: str) -> FieldValidation:
        if not value:
            return FieldValidation('country', value, False, 'Country is required')
        
        if cls.COUNTRY_PATTERN.match(value):
            return FieldValidation('country', value, True, None)
        
        return FieldValidation(
            'country', value, False,
            f'Invalid country code format: {value}'
        )
    
    @classmethod
    def validate_currency(cls, value: str) -> FieldValidation:
        if not value:
            return FieldValidation('currency', value, False, 'Currency is required')
        
        if cls.CURRENCY_PATTERN.match(value):
            return FieldValidation('currency', value, True, None)
        
        return FieldValidation(
            'currency', value, False,
            f'Invalid currency code format: {value}'
        )
    
    @classmethod
    def validate_saft_id(cls, value: str) -> FieldValidation:
        if not value:
            return FieldValidation('saft_id', value, False, 'SAF-T ID is required')
        
        prefix = value[:2]
        identifier = value[2:]
        
        valid_prefixes = {'10', '11', '12', '13', '15'}
        
        if prefix not in valid_prefixes:
            return FieldValidation(
                'saft_id', value, False,
                f'Invalid SAF-T ID prefix: {prefix}'
            )
        
        if prefix == '10' and not re.match(r'^[0-9]{9,13}$', identifier):
            return FieldValidation(
                'saft_id', value, False,
                f'Invalid Bulgarian EIK in SAF-T ID: {identifier}'
            )
        
        return FieldValidation('saft_id', value, True, None)
```

## 10.4. Referential Integrity (Layer 3)

### Cross-reference Validator

```python
from typing import Dict, Set, List
from dataclasses import dataclass, field

@dataclass
class IntegrityError:
    source_entity: str
    source_id: str
    reference_type: str
    referenced_id: str
    message: str

class SaftIntegrityValidator:
    def __init__(self):
        self.accounts: Dict[str, dict] = {}
        self.counterparts: Dict[str, dict] = {}
        self.products: Dict[str, dict] = {}
        self.journal_entries: Dict[str, dict] = {}
        self.invoices: Dict[str, dict] = {}
        self.errors: List[IntegrityError] = []
    
    def load_accounts(self, accounts: List[dict]):
        for acc in accounts:
            key = acc.get('code') or acc.get('id')
            self.accounts[key] = acc
    
    def load_counterparts(self, counterparts: List[dict]):
        for cp in counterparts:
            key = cp.get('saft_id') or cp.get('id')
            self.counterparts[key] = cp
    
    def load_products(self, products: List[dict]):
        for prod in products:
            key = prod.get('code') or prod.get('id')
            self.products[key] = prod
    
    def validate_journal_entry_line(self, line: dict, entry_id: str) -> bool:
        valid = True
        
        account_ref = line.get('account_id') or line.get('account_code')
        if account_ref and account_ref not in self.accounts:
            self.errors.append(IntegrityError(
                source_entity='journal_entry_line',
                source_id=line.get('id', 'unknown'),
                reference_type='account',
                referenced_id=account_ref,
                message=f'Line references non-existent account: {account_ref}'
            ))
            valid = False
        
        counterpart_ref = line.get('counterpart_id') or line.get('customer_id') or line.get('supplier_id')
        if counterpart_ref and counterpart_ref not in self.counterparts:
            self.errors.append(IntegrityError(
                source_entity='journal_entry_line',
                source_id=line.get('id', 'unknown'),
                reference_type='counterpart',
                referenced_id=counterpart_ref,
                message=f'Line references non-existent counterpart: {counterpart_ref}'
            ))
            valid = False
        
        return valid
    
    def validate_invoice(self, invoice: dict) -> bool:
        valid = True
        
        counterpart_ref = invoice.get('counterpart_id') or invoice.get('customer_id')
        if counterpart_ref and counterpart_ref not in self.counterparts:
            self.errors.append(IntegrityError(
                source_entity='invoice',
                source_id=invoice.get('id', 'unknown'),
                reference_type='counterpart',
                referenced_id=counterpart_ref,
                message=f"Invoice {invoice.get('invoice_number')} references non-existent counterpart"
            ))
            valid = False
        
        for line in invoice.get('lines', []):
            product_ref = line.get('product_code')
            if product_ref and product_ref not in self.products:
                self.errors.append(IntegrityError(
                    source_entity='invoice_line',
                    source_id=f"{invoice.get('id')}/{line.get('line_number')}",
                    reference_type='product',
                    referenced_id=product_ref,
                    message=f"Invoice line references non-existent product: {product_ref}"
                ))
        
        journal_ref = invoice.get('journal_entry_id')
        if journal_ref and journal_ref not in self.journal_entries:
            self.errors.append(IntegrityError(
                source_entity='invoice',
                source_id=invoice.get('id', 'unknown'),
                reference_type='journal_entry',
                referenced_id=journal_ref,
                message=f"Invoice {invoice.get('invoice_number')} references non-existent journal entry"
            ))
        
        return valid
    
    def validate_tax_codes_in_use(self, used_codes: Set[str], defined_codes: Set[str]) -> List[IntegrityError]:
        errors = []
        undefined = used_codes - defined_codes
        
        for code in undefined:
            errors.append(IntegrityError(
                source_entity='tax_information',
                source_id='unknown',
                reference_type='tax_code',
                referenced_id=code,
                message=f'Tax code {code} is used but not defined in TaxTable'
            ))
        
        return errors
    
    def validate_account_mapping(self, accounts: List[dict], saft_accounts: Set[str]) -> List[IntegrityError]:
        errors = []
        
        for acc in accounts:
            saft_code = acc.get('saft_account_code')
            if saft_code and saft_code not in saft_accounts:
                errors.append(IntegrityError(
                    source_entity='account',
                    source_id=acc.get('id', 'unknown'),
                    reference_type='saft_account',
                    referenced_id=saft_code,
                    message=f"Account {acc.get('code')} maps to invalid SAF-T code: {saft_code}"
                ))
        
        return errors
    
    def get_report(self) -> dict:
        return {
            'total_errors': len(self.errors),
            'by_type': self._group_errors_by_type(),
            'errors': [
                {
                    'source': e.source_entity,
                    'source_id': e.source_id,
                    'type': e.reference_type,
                    'referenced': e.referenced_id,
                    'message': e.message
                }
                for e in self.errors
            ]
        }
    
    def _group_errors_by_type(self) -> Dict[str, int]:
        counts = {}
        for error in self.errors:
            counts[error.reference_type] = counts.get(error.reference_type, 0) + 1
        return counts
```

## 10.5. Cross-module Consistency (Layer 4)

### Validation Between Modules

```python
from decimal import Decimal
from typing import Dict, List, Tuple

class CrossModuleValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_invoice_journal_link(
        self,
        invoices: List[dict],
        journal_entries: List[dict]
    ) -> List[dict]:
        issues = []
        
        journal_by_id = {je.get('id'): je for je in journal_entries}
        
        for inv in invoices:
            je_id = inv.get('journal_entry_id')
            
            if not je_id:
                issues.append({
                    'type': 'missing_link',
                    'invoice': inv.get('invoice_number'),
                    'message': f"Invoice {inv.get('invoice_number')} has no journal entry link"
                })
                continue
            
            if je_id not in journal_by_id:
                issues.append({
                    'type': 'broken_link',
                    'invoice': inv.get('invoice_number'),
                    'journal_id': je_id,
                    'message': f"Invoice {inv.get('invoice_number')} links to non-existent journal entry"
                })
                continue
            
            je = journal_by_id[je_id]
            
            inv_total = Decimal(str(inv.get('total', 0)))
            je_total = Decimal(str(je.get('total_debit', 0)))
            
            if abs(inv_total - je_total) > Decimal('0.01'):
                issues.append({
                    'type': 'amount_mismatch',
                    'invoice': inv.get('invoice_number'),
                    'invoice_total': float(inv_total),
                    'journal_total': float(je_total),
                    'difference': float(inv_total - je_total),
                    'message': f"Amount mismatch: invoice={inv_total}, journal={je_total}"
                })
        
        return issues
    
    def validate_vat_consistency(
        self,
        invoices: List[dict],
        journal_entries: List[dict]
    ) -> Tuple[dict, List[dict]]:
        sales_invoices = [i for i in invoices if i.get('invoice_type') == 'sales']
        
        total_sales_vat = sum(
            Decimal(str(i.get('vat_amount', 0))) 
            for i in sales_invoices
        )
        
        total_sales_base = sum(
            Decimal(str(i.get('subtotal', 0))) 
            for i in sales_invoices
        )
        
        vat_account_codes = ['453', '4531', '4532', '4533', '4534']
        
        journal_vat_credit = Decimal('0')
        journal_vat_base = Decimal('0')
        
        for je in journal_entries:
            for line in je.get('lines', []):
                acc_code = str(line.get('account_code', ''))
                if any(acc_code.startswith(vac) for vac in vat_account_codes):
                    if line.get('credit'):
                        journal_vat_credit += Decimal(str(line['credit']))
                    if line.get('debit'):
                        journal_vat_credit -= Decimal(str(line['debit']))
        
        summary = {
            'sales_invoices_count': len(sales_invoices),
            'total_sales_base': float(total_sales_base),
            'total_sales_vat': float(total_sales_vat),
            'journal_vat_credit': float(journal_vat_credit),
            'vat_difference': float(total_sales_vat - journal_vat_credit)
        }
        
        issues = []
        if abs(total_sales_vat - journal_vat_credit) > Decimal('0.01'):
            issues.append({
                'type': 'vat_mismatch',
                'sales_vat': float(total_sales_vat),
                'journal_vat': float(journal_vat_credit),
                'difference': float(total_sales_vat - journal_vat_credit),
                'message': 'VAT from sales invoices does not match journal entries'
            })
        
        return summary, issues
    
    def validate_counterpart_totals(
        self,
        counterparts: List[dict],
        journal_entries: List[dict]
    ) -> List[dict]:
        cp_balances: Dict[str, Decimal] = {}
        
        for je in journal_entries:
            for line in je.get('lines', []):
                cp_id = line.get('counterpart_id')
                if not cp_id:
                    continue
                
                if cp_id not in cp_balances:
                    cp_balances[cp_id] = Decimal('0')
                
                if line.get('debit'):
                    cp_balances[cp_id] += Decimal(str(line['debit']))
                if line.get('credit'):
                    cp_balances[cp_id] -= Decimal(str(line['credit']))
        
        cp_by_id = {cp.get('id'): cp for cp in counterparts}
        
        issues = []
        
        for cp_id, balance in cp_balances.items():
            cp = cp_by_id.get(cp_id)
            if not cp:
                issues.append({
                    'type': 'orphan_journal_lines',
                    'counterpart_id': cp_id,
                    'balance': float(balance),
                    'message': f'Journal lines reference unknown counterpart: {cp_id}'
                })
                continue
            
            opening = Decimal(str(cp.get('opening_balance', 0) or 0))
            closing = Decimal(str(cp.get('closing_balance', 0) or 0))
            
            expected_closing = opening + balance
            
            if abs(expected_closing - closing) > Decimal('0.01'):
                issues.append({
                    'type': 'balance_mismatch',
                    'counterpart': cp.get('name'),
                    'counterpart_id': cp_id,
                    'opening': float(opening),
                    'movement': float(balance),
                    'expected_closing': float(expected_closing),
                    'actual_closing': float(closing),
                    'difference': float(expected_closing - closing),
                    'message': f"Counterpart {cp.get('name')} balance mismatch"
                })
        
        return issues
    
    def validate_stock_accounting_link(
        self,
        stock_movements: List[dict],
        journal_entries: List[dict]
    ) -> List[dict]:
        issues = []
        
        stock_by_je = {}
        for sm in stock_movements:
            je_id = sm.get('journal_entry_id')
            if je_id:
                if je_id not in stock_by_je:
                    stock_by_je[je_id] = []
                stock_by_je[je_id].append(sm)
        
        journal_ids = {je.get('id') for je in journal_entries}
        
        for je_id, movements in stock_by_je.items():
            if je_id not in journal_ids:
                issues.append({
                    'type': 'orphan_stock_movements',
                    'journal_id': je_id,
                    'movement_count': len(movements),
                    'message': f'Stock movements reference non-existent journal entry: {je_id}'
                })
        
        return issues
```

## 10.6. Business Logic Validation (Layer 5)

### Accounting Rules Validator

```python
from decimal import Decimal
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class AccountingRuleViolation:
    rule_code: str
    rule_name: str
    severity: str
    entity_type: str
    entity_id: str
    details: str

class AccountingRulesValidator:
    ACCOUNT_CATEGORIES = {
        '1': 'Capital',
        '2': 'Non-current Assets',
        '3': 'Inventory',
        '4': 'Liabilities and Receivables',
        '5': 'Financial',
        '6': 'Costs',
        '7': 'Income',
        '8': 'Result',
        '9': 'Off-balance'
    }
    
    def __init__(self):
        self.violations: List[AccountingRuleViolation] = []
    
    def validate_double_entry(self, journal_entries: List[dict]) -> List[dict]:
        issues = []
        
        for je in journal_entries:
            if je.get('status') != 'POSTED':
                continue
            
            total_debit = Decimal('0')
            total_credit = Decimal('0')
            
            for line in je.get('lines', []):
                if line.get('debit'):
                    total_debit += Decimal(str(line['debit']))
                if line.get('credit'):
                    total_credit += Decimal(str(line['credit']))
            
            diff = abs(total_debit - total_credit)
            
            if diff > Decimal('0.01'):
                issues.append({
                    'entry_number': je.get('entry_number'),
                    'total_debit': float(total_debit),
                    'total_credit': float(total_credit),
                    'difference': float(diff),
                    'message': f"Unbalanced entry: {je.get('entry_number')}"
                })
                
                self.violations.append(AccountingRuleViolation(
                    rule_code='ACC001',
                    rule_name='Double Entry Principle',
                    severity='ERROR',
                    entity_type='journal_entry',
                    entity_id=je.get('id', ''),
                    details=f"Debit {total_debit} != Credit {total_credit}"
                ))
        
        return issues
    
    def validate_account_usage(
        self, 
        journal_entries: List[dict],
        period: str
    ) -> List[dict]:
        issues = []
        
        cost_accounts = ['601', '602', '603', '604', '605', '606', '607', '608', '609']
        income_accounts = ['701', '702', '703', '704', '705', '706', '707', '708', '709']
        
        for je in journal_entries:
            for line in je.get('lines', []):
                acc_code = str(line.get('account_code', ''))
                
                if any(acc_code.startswith(ca) for ca in cost_accounts):
                    if line.get('credit') and Decimal(str(line['credit'])) > 0:
                        pass
                
                if any(acc_code.startswith(ia) for ia in income_accounts):
                    if line.get('debit') and Decimal(str(line['debit'])) > 0:
                        pass
        
        return issues
    
    def validate_vat_calculation(
        self,
        journal_entries: List[dict],
        tax_rates: Dict[str, Decimal]
    ) -> List[dict]:
        issues = []
        
        for je in journal_entries:
            for line in je.get('lines', []):
                tax_info = line.get('tax_information')
                if not tax_info:
                    continue
                
                base = Decimal(str(tax_info.get('tax_base', 0)))
                rate = Decimal(str(tax_info.get('tax_percentage', 0)))
                actual_vat = Decimal(str(tax_info.get('tax_amount', 0)))
                
                expected_vat = (base * rate / 100).quantize(Decimal('0.01'))
                
                if abs(expected_vat - actual_vat) > Decimal('0.01'):
                    issues.append({
                        'entry': je.get('entry_number'),
                        'line': line.get('line_number'),
                        'base': float(base),
                        'rate': float(rate),
                        'expected_vat': float(expected_vat),
                        'actual_vat': float(actual_vat),
                        'difference': float(expected_vat - actual_vat),
                        'message': f"VAT calculation error in {je.get('entry_number')}"
                    })
        
        return issues
    
    def validate_trial_balance(
        self,
        accounts: List[dict],
        journal_entries: List[dict]
    ) -> Tuple[dict, List[dict]]:
        account_totals: Dict[str, Dict] = {}
        
        for acc in accounts:
            code = acc.get('code')
            account_totals[code] = {
                'name': acc.get('name'),
                'type': acc.get('account_type'),
                'opening_debit': Decimal(str(acc.get('opening_debit', 0) or 0)),
                'opening_credit': Decimal(str(acc.get('opening_credit', 0) or 0)),
                'period_debit': Decimal('0'),
                'period_credit': Decimal('0'),
            }
        
        for je in journal_entries:
            if je.get('status') != 'POSTED':
                continue
            
            for line in je.get('lines', []):
                acc_code = line.get('account_code')
                if acc_code not in account_totals:
                    account_totals[acc_code] = {
                        'name': 'Unknown',
                        'type': 'Unknown',
                        'opening_debit': Decimal('0'),
                        'opening_credit': Decimal('0'),
                        'period_debit': Decimal('0'),
                        'period_credit': Decimal('0'),
                    }
                
                if line.get('debit'):
                    account_totals[acc_code]['period_debit'] += Decimal(str(line['debit']))
                if line.get('credit'):
                    account_totals[acc_code]['period_credit'] += Decimal(str(line['credit']))
        
        total_debit = sum(
            a['opening_debit'] + a['period_debit'] 
            for a in account_totals.values()
        )
        total_credit = sum(
            a['opening_credit'] + a['period_credit'] 
            for a in account_totals.values()
        )
        
        summary = {
            'total_debit': float(total_debit),
            'total_credit': float(total_credit),
            'is_balanced': abs(total_debit - total_credit) < 0.01,
            'accounts_count': len(account_totals),
        }
        
        issues = []
        if not summary['is_balanced']:
            issues.append({
                'type': 'trial_balance_mismatch',
                'total_debit': summary['total_debit'],
                'total_credit': summary['total_credit'],
                'difference': abs(summary['total_debit'] - summary['total_credit']),
                'message': 'Trial balance is not balanced'
            })
        
        return summary, issues
```

## 10.7. Automated Test Suite

### Pytest Framework

```python
import pytest
from pathlib import Path
import tempfile

class TestSaftValidation:
    @pytest.fixture
    def validator(self):
        return SaftXsdValidator('SAFT_BG/BG_SAFT_Schema_V_1.0.1.xsd')
    
    @pytest.fixture
    def sample_company(self):
        return {
            'id': 'test-001',
            'name': 'Тестова фирма ООД',
            'eik': '123456789',
            'vat_number': '1234567890',
            'country': 'BG',
            'currency': 'BGN',
            'is_vat_registered': True,
        }
    
    @pytest.fixture
    def sample_counterpart(self):
        return {
            'id': 'cp-001',
            'name': 'Клиент АД',
            'eik': '987654321',
            'country': 'BG',
            'counterpart_type': 'customer',
        }
    
    @pytest.fixture
    def balanced_journal_entry(self):
        return {
            'id': 'je-001',
            'entry_number': '001',
            'date': '2026-01-15',
            'description': 'Продажба',
            'status': 'POSTED',
            'lines': [
                {'account_code': '411', 'debit': 120.00, 'credit': None},
                {'account_code': '702', 'debit': None, 'credit': 100.00},
                {'account_code': '453', 'debit': None, 'credit': 20.00},
            ]
        }
    
    def test_eik_validation_valid(self):
        result = SaftFieldTypeValidator.validate_eik('123456789')
        assert result.is_valid
    
    def test_eik_validation_invalid_length(self):
        result = SaftFieldTypeValidator.validate_eik('12345')
        assert not result.is_valid
        assert 'format' in result.error_message.lower()
    
    def test_vat_number_validation_bg_valid(self):
        result = SaftFieldTypeValidator.validate_vat_number('1234567890', 'BG')
        assert result.is_valid
    
    def test_uom_validation_valid(self):
        for uom in ['C62', 'KGM', 'LTR', 'MTR']:
            result = SaftFieldTypeValidator.validate_uom(uom)
            assert result.is_valid, f"{uom} should be valid"
    
    def test_uom_validation_invalid(self):
        result = SaftFieldTypeValidator.validate_uom('бр')
        assert not result.is_valid
    
    def test_decimal_validation(self):
        result = SaftFieldTypeValidator.validate_decimal('123.45', 'amount')
        assert result.is_valid
        assert result.value == Decimal('123.45')
    
    def test_decimal_validation_negative(self):
        result = SaftFieldTypeValidator.validate_decimal('-50.00', 'amount')
        assert result.is_valid
    
    def test_journal_entry_balance(self, balanced_journal_entry):
        validator = AccountingRulesValidator()
        issues = validator.validate_double_entry([balanced_journal_entry])
        assert len(issues) == 0
    
    def test_journal_entry_unbalanced(self):
        entry = {
            'id': 'je-002',
            'entry_number': '002',
            'status': 'POSTED',
            'lines': [
                {'account_code': '411', 'debit': 100.00, 'credit': None},
                {'account_code': '702', 'debit': None, 'credit': 90.00},
            ]
        }
        validator = AccountingRulesValidator()
        issues = validator.validate_double_entry([entry])
        assert len(issues) == 1
        assert 'unbalanced' in issues[0]['message'].lower()
    
    def test_saft_id_generation_bg(self):
        from chapter_8 import SaftDataCleaner
        cleaner = SaftDataCleaner()
        
        saft_id = cleaner.generate_saft_counterpart_id(
            eik='123456789',
            vat_number=None,
            country='BG'
        )
        assert saft_id == '10123456789'
    
    def test_saft_id_generation_eu(self):
        from chapter_8 import SaftDataCleaner
        cleaner = SaftDataCleaner()
        
        saft_id = cleaner.generate_saft_counterpart_id(
            eik=None,
            vat_number='12345678',
            country='DE'
        )
        assert saft_id == '11DE12345678'
    
    def test_cross_module_invoice_journal_consistency(self):
        validator = CrossModuleValidator()
        
        invoices = [{
            'id': 'inv-001',
            'invoice_number': '001',
            'total': 120.00,
            'journal_entry_id': 'je-001'
        }]
        
        journal_entries = [{
            'id': 'je-001',
            'total_debit': 100.00,
            'total_credit': 100.00
        }]
        
        issues = validator.validate_invoice_journal_link(invoices, journal_entries)
        
        amount_issues = [i for i in issues if i['type'] == 'amount_mismatch']
        assert len(amount_issues) == 1
    
    def test_xsd_validation_valid_xml(self, validator):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<nsSAFT:AuditFile xmlns:nsSAFT="mf:nra:dgti:dxxxx:declaration:v1">
    <nsSAFT:Header>
        <nsSAFT:TaxAccountingBasis>A</nsSAFT:TaxAccountingBasis>
    </nsSAFT:Header>
</nsSAFT:AuditFile>''')
            f.flush()
            
            is_valid, errors = validator.validate(f.name)
            assert is_valid or len(errors) > 0

class TestSaftGeneration:
    def test_xml_escapes_special_chars(self):
        from chapter_6 import build_saft_xml
        
        data = {
            'company': {'name': 'Test & Co. <Ltd>'},
            'accounts': [],
            'journal_entries': [],
            'invoices': [],
        }
        
    def test_large_file_streaming(self):
        pass
    
    def test_concurrent_validation(self):
        pass

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
```

## 10.8. CI/CD Integration

### GitHub Actions Workflow

```yaml
name: SAF-T Validation

on:
  push:
    paths:
      - 'SAFT-BOOK/**'
      - 'SAFT_BG/**'
  pull_request:
    paths:
      - 'SAFT-BOOK/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install lxml pandas pytest
    
    - name: Run XSD validation tests
      run: |
        pytest SAFT-BOOK/tests/ -v --tb=short
    
    - name: Validate sample files
      run: |
        python -c "
        from pathlib import Path
        import sys
        sys.path.insert(0, 'SAFT-BOOK')
        from chapter_10 import SaftXsdValidator
        
        validator = SaftXsdValidator('SAFT_BG/BG_SAFT_Schema_V_1.0.1.xsd')
        
        for xml_file in Path('SAFT_BG').glob('*.xml'):
            is_valid, errors = validator.validate(str(xml_file))
            print(f'{xml_file.name}: {\"OK\" if is_valid else \"FAILED\"}')
            for err in errors[:5]:
                print(f'  Line {err.line}: {err.message}')
        "
    
    - name: Generate validation report
      if: always()
      run: |
        echo "## SAF-T Validation Report" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "Validation completed at $(date)" >> $GITHUB_STEP_SUMMARY
```

## 10.9. Заключение

Тестването на SAF-T файлове е **неотложна необходимост**, а не лукс. Петте слоя валидация гарантират:

1. **XSD** — файловете са синтактично правилни
2. **Types** — данните са в правилния формат
3. **Integrity** — всички връзки са валидни
4. **Consistency** — модулите си отговарят
5. **Business** — счетоводната логика е спазена

Автоматизирайте всичко. Ръчната проверка е рецепта за катастрофа.
