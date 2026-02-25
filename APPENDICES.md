# Приложения

## Приложение А: Пълна таблица на SAF-T сметките

| Код | Име | Тип | Раздел |
|-----|-----|-----|--------|
| 101 | Основен капитал | Passive | 1 - Капитал |
| 102 | Премии от емисия на акции | Passive | 1 - Капитал |
| 104 | Резерв от предишни години | Passive | 1 - Капитал |
| 105 | Неразпределена печалба | Passive | 1 - Капитал |
| 106 | Непокрита загуба | Active | 1 - Капитал |
| 107 | Текуща година | Bifunctional | 1 - Капитал |
| 201 | Дълготрайни материални активи | Active | 2 - ДМА |
| 202 | Амортизация на ДМА | Active | 2 - ДМА |
| 203 | Нематериални активи | Active | 2 - ДМА |
| 204 | Дългосрочни финансови активи | Active | 2 - ДМА |
| 301 | Материали | Active | 3 - Материални запаси |
| 302 | Производство | Active | 3 - Материални запаси |
| 303 | Готова продукция | Active | 3 - Материални запаси |
| 304 | Стоки | Active | 3 - Материални запаси |
| 401 | Доставчици | Bifunctional | 4 - Разчети |
| 411 | Клиенти | Bifunctional | 4 - Разчети |
| 412 | Вземания по сделки | Bifunctional | 4 - Разчети |
| 421 | Персонал | Bifunctional | 4 - Разчети |
| 422 | Данъци и такси | Bifunctional | 4 - Разчети |
| 453 | ДДС | Bifunctional | 4 - Разчети |
| 499 | Други задължения | Bifunctional | 4 - Разчети |
| 501 | Каса | Active | 5 - Финанси |
| 502 | Валута | Active | 5 - Финанси |
| 503 | Банкови сметки | Active | 5 - Финанси |
| 601 | Разходи за материали | Active | 6 - Разходи |
| 602 | Разходи за външни услуги | Active | 6 - Разходи |
| 603 | Разходи за персонал | Active | 6 - Разходи |
| 604 | Разходи за амортизация | Active | 6 - Разходи |
| 605 | Разходи за социални осигуровки | Active | 6 - Разходи |
| 606 | Финансови разходи | Active | 6 - Разходи |
| 701 | Приходи от продажба на готова продукция | Passive | 7 - Приходи |
| 702 | Приходи от продажба на стоки | Passive | 7 - Приходи |
| 703 | Приходи от предоставени услуги | Passive | 7 - Приходи |
| 704 | Други приходи от продажби | Passive | 7 - Приходи |
| 705 | Финансови приходи | Passive | 7 - Приходи |

## Приложение Б: Данъчни кодове (TaxTable)

| Код | Ставка | Описание |
|-----|--------|----------|
| 100010 | - | Общ код за ДДС |
| 100211 | 20.00% | Облагаеми доставки със стандартна ставка |
| 100213 | 9.00% | Облагаеми доставки с намалена ставка |
| 100214 | 0.00% | Облагаеми доставки с нулева ставка |
| 100215 | 0.00% | Доставки с право на приспадане на данъчен кредит |
| 100216 | 0.00% | ВОП (вътрешнообщностни доставки) |
| 100217 | 0.00% | Износ |
| 100218 | 0.00% | Доставки, облагаеми на мястото на получателя |
| 100219 | 0.00% | Освободени доставки |
| 100301 | - | Възвръщаем ДДС |
| 100302 | - | Невъзвръщаем ДДС |

## Приложение В: Мерни единици (UOM)

| Код | Описание EN | Описание BG |
|-----|-------------|-------------|
| C62 | Unit | брой |
| KGM | Kilogram | килограм |
| LTR | Litre | литър |
| MTR | Metre | метър |
| MTK | Square metre | квадратен метър |
| MTQ | Cubic metre | кубичен метър |
| TNE | Tonne | тон |
| HUR | Hour | час |
| DZN | Dozen | дузина |
| BX | Box | кутия |
| CT | Carton | кашон |
| PA | Pack | пакет |
| PK | Package | пакет |
| PR | Pair | чифт |
| SET | Set | комплект |
| NAR | Number of articles | брой артикули |
| NPR | Number of pairs | брой чифтове |
| MIL | Millimetre | милиметър |
| CMT | Centimetre | сантиметър |
| KTM | Kilometre | километър |
| GRM | Gram | грам |
| LBR | Pound | паунд |
| ONZ | Ounce | унция |
| GAL | Gallon | галон |
| INH | Inch | инч |
| FOT | Foot | фут |
| YRD | Yard | ярд |

## Приложение Г: Типове движения за склад (On Demand)

| Код | Описание |
|-----|----------|
| 10 | Покупка |
| 20 | Връщане на покупка |
| 30 | Продажба |
| 40 | Връщане на продажба |
| 50 | Вътрешно преместване (трансфер) |
| 60 | Приспособяване (инвентаризация) |
| 70 | Брак / Повреда |
| 80 | Технологични загуби |
| 90 | Използване в производство |
| 95 | Извършена услуга |

## Приложение Д: Префикси за SAF-T ID

| Префикс | Тип контрагент | Формат | Пример |
|---------|----------------|--------|--------|
| 10 | Българско лице с ЕИК | 10 + ЕИК (9 или 13 цифри) | 10123456789 |
| 11 | Чуждестранно лице от ЕС с ДДС номер | 11 + Държава + ДДС номер | 11DE123456789 |
| 12 | Чуждестранно лице извън ЕС с ДДС номер | 12 + Държава + ДДС номер | 12US123456789 |
| 13 | Чуждестранно лице само с ЕИК | 13 + ЕИК | 13987654321 |
| 14 | Липсващи данни - ЕС | 14 + Държава + ID | 14DE001 |
| 15 | Липсващи данни - извън ЕС | 15 + ID | 1500001 |

## Приложение Е: Примерен SAF-T XML (Monthly)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<nsSAFT:AuditFile xmlns:nsSAFT="mf:nra:dgti:dxxxx:declaration:v1">
    <nsSAFT:Header>
        <nsSAFT:TaxAccountingBasis>A</nsSAFT:TaxAccountingBasis>
        <nsSAFT:CompanyName>Тестова фирма ООД</nsSAFT:CompanyName>
        <nsSAFT:CompanyID>101234567890</nsSAFT:CompanyID>
        <nsSAFT:VATRegistrationNumber>BG123456789</nsSAFT:VATRegistrationNumber>
        <nsSAFT:TaxRegistrationNumber>1234567890</nsSAFT:TaxRegistrationNumber>
        <nsSAFT:Address>
            <nsSAFT:StreetName>ул. Тестова</nsSAFT:StreetName>
            <nsSAFT:BuildingNumber>15</nsSAFT:BuildingNumber>
            <nsSAFT:City>София</nsSAFT:City>
            <nsSAFT:PostalCode>1000</nsSAFT:PostalCode>
            <nsSAFT:Region>BG-22</nsSAFT:Region>
            <nsSAFT:Country>BG</nsSAFT:Country>
        </nsSAFT:Address>
        <nsSAFT:Contact>
            <nsSAFT:ContactPerson>Иван Иванов</nsSAFT:ContactPerson>
            <nsSAFT:Telephone>+359 2 123 4567</nsSAFT:Telephone>
            <nsSAFT:Email>office@test.bg</nsSAFT:Email>
        </nsSAFT:Contact>
        <nsSAFT:DateCreated>2026-02-01</nsSAFT:DateCreated>
        <nsSAFT:TaxYear>2026</nsSAFT:TaxYear>
        <nsSAFT:DateFrom>2026-01-01</nsSAFT:DateFrom>
        <nsSAFT:DateTo>2026-01-31</nsSAFT:DateTo>
        <nsSAFT:CurrencyCode>BGN</nsSAFT:CurrencyCode>
        <nsSAFT:SelectionStartDate>2026-01-01</nsSAFT:SelectionStartDate>
        <nsSAFT:SelectionEndDate>2026-01-31</nsSAFT:SelectionEndDate>
        <nsSAFT:SoftwareID>BARABA</nsSAFT:SoftwareID>
        <nsSAFT:SoftwareDescription>baraba.org Accounting System</nsSAFT:SoftwareDescription>
        <nsSAFT:SoftwareVersion>1.0.0</nsSAFT:SoftwareVersion>
    </nsSAFT:Header>
    
    <nsSAFT:MasterFilesMonthly>
        <nsSAFT:GeneralLedgerAccounts>
            <nsSAFT:Account>
                <nsSAFT:AccountID>411</nsSAFT:AccountID>
                <nsSAFT:AccountDescription>Клиенти</nsSAFT:AccountDescription>
                <nsSAFT:TaxpayerAccountID>411.01</nsSAFT:TaxpayerAccountID>
                <nsSAFT:AccountType>Bifunctional</nsSAFT:AccountType>
                <nsSAFT:OpeningDebitBalance>5000.00</nsSAFT:OpeningDebitBalance>
                <nsSAFT:ClosingDebitBalance>6200.00</nsSAFT:ClosingDebitBalance>
            </nsSAFT:Account>
            <nsSAFT:Account>
                <nsSAFT:AccountID>702</nsSAFT:AccountID>
                <nsSAFT:AccountDescription>Приходи от продажби</nsSAFT:AccountDescription>
                <nsSAFT:TaxpayerAccountID>702.01</nsSAFT:TaxpayerAccountID>
                <nsSAFT:AccountType>Passive</nsSAFT:AccountType>
                <nsSAFT:OpeningCreditBalance>0.00</nsSAFT:OpeningCreditBalance>
                <nsSAFT:ClosingCreditBalance>10000.00</nsSAFT:ClosingCreditBalance>
            </nsSAFT:Account>
            <nsSAFT:Account>
                <nsSAFT:AccountID>453</nsSAFT:AccountID>
                <nsSAFT:AccountDescription>ДДС</nsSAFT:AccountDescription>
                <nsSAFT:TaxpayerAccountID>453.01</nsSAFT:TaxpayerAccountID>
                <nsSAFT:AccountType>Bifunctional</nsSAFT:AccountType>
                <nsSAFT:OpeningCreditBalance>0.00</nsSAFT:OpeningCreditBalance>
                <nsSAFT:ClosingCreditBalance>2000.00</nsSAFT:ClosingCreditBalance>
            </nsSAFT:Account>
        </nsSAFT:GeneralLedgerAccounts>
        
        <nsSAFT:Customers>
            <nsSAFT:Customer>
                <nsSAFT:CustomerID>109876543210</nsSAFT:CustomerID>
                <nsSAFT:CompanyStructure>
                    <nsSAFT:Name>Клиент АД</nsSAFT:Name>
                    <nsSAFT:Address>
                        <nsSAFT:StreetName>бул. Витоша</nsSAFT:StreetName>
                        <nsSAFT:BuildingNumber>100</nsSAFT:BuildingNumber>
                        <nsSAFT:City>София</nsSAFT:City>
                        <nsSAFT:Country>BG</nsSAFT:Country>
                    </nsSAFT:Address>
                </nsSAFT:CompanyStructure>
                <nsSAFT:SelfBillingIndicator>N</nsSAFT:SelfBillingIndicator>
                <nsSAFT:AccountID>411</nsSAFT:AccountID>
                <nsSAFT:OpeningDebitBalance>5000.00</nsSAFT:OpeningDebitBalance>
                <nsSAFT:ClosingDebitBalance>6200.00</nsSAFT:ClosingDebitBalance>
            </nsSAFT:Customer>
        </nsSAFT:Customers>
        
        <nsSAFT:Suppliers>
            <nsSAFT:Supplier>
                <nsSAFT:SupplierID>101111111111</nsSAFT:SupplierID>
                <nsSAFT:CompanyStructure>
                    <nsSAFT:Name>Доставчик ООД</nsSAFT:Name>
                    <nsSAFT:Address>
                        <nsSAFT:City>Пловдив</nsSAFT:City>
                        <nsSAFT:Country>BG</nsSAFT:Country>
                    </nsSAFT:Address>
                </nsSAFT:CompanyStructure>
                <nsSAFT:SelfBillingIndicator>N</nsSAFT:SelfBillingIndicator>
                <nsSAFT:AccountID>401</nsSAFT:AccountID>
                <nsSAFT:OpeningCreditBalance>3000.00</nsSAFT:OpeningCreditBalance>
                <nsSAFT:ClosingCreditBalance>3500.00</nsSAFT:ClosingCreditBalance>
            </nsSAFT:Supplier>
        </nsSAFT:Suppliers>
        
        <nsSAFT:TaxTable>
            <nsSAFT:TaxTableEntry>
                <nsSAFT:TaxType>100010</nsSAFT:TaxType>
                <nsSAFT:Description>ДДС</nsSAFT:Description>
                <nsSAFT:TaxCodeDetails>
                    <nsSAFT:TaxCode>100211</nsSAFT:TaxCode>
                    <nsSAFT:Description>Облагаеми доставки 20%</nsSAFT:Description>
                    <nsSAFT:TaxPercentage>20.00</nsSAFT:TaxPercentage>
                    <nsSAFT:Country>BG</nsSAFT:Country>
                </nsSAFT:TaxCodeDetails>
                <nsSAFT:TaxCodeDetails>
                    <nsSAFT:TaxCode>100219</nsSAFT:TaxCode>
                    <nsSAFT:Description>Освободени доставки</nsSAFT:Description>
                    <nsSAFT:TaxPercentage>0.00</nsSAFT:TaxPercentage>
                    <nsSAFT:Country>BG</nsSAFT:Country>
                </nsSAFT:TaxCodeDetails>
            </nsSAFT:TaxTableEntry>
        </nsSAFT:TaxTable>
        
        <nsSAFT:UOMTable>
            <nsSAFT:UOMTableEntry>
                <nsSAFT:UnitOfMeasure>C62</nsSAFT:UnitOfMeasure>
                <nsSAFT:Description>брой</nsSAFT:Description>
            </nsSAFT:UOMTableEntry>
            <nsSAFT:UOMTableEntry>
                <nsSAFT:UnitOfMeasure>KGM</nsSAFT:UnitOfMeasure>
                <nsSAFT:Description>килограм</nsSAFT:Description>
            </nsSAFT:UOMTableEntry>
        </nsSAFT:UOMTable>
        
        <nsSAFT:Products>
            <nsSAFT:Product>
                <nsSAFT:ProductCode>PROD001</nsSAFT:ProductCode>
                <nsSAFT:GoodsServicesID>01</nsSAFT:GoodsServicesID>
                <nsSAFT:Description>Стока А</nsSAFT:Description>
                <nsSAFT:ProductCommodityCode>12345678</nsSAFT:ProductCommodityCode>
                <nsSAFT:UOMBase>C62</nsSAFT:UOMBase>
                <nsSAFT:UOMStandard>C62</nsSAFT:UOMStandard>
                <nsSAFT:UOMToUOMBaseConversionFactor>1.00</nsSAFT:UOMToUOMBaseConversionFactor>
            </nsSAFT:Product>
        </nsSAFT:Products>
    </nsSAFT:MasterFilesMonthly>
    
    <nsSAFT:GeneralLedgerEntries>
        <nsSAFT:NumberOfEntries>2</nsSAFT:NumberOfEntries>
        <nsSAFT:TotalDebit>12000.00</nsSAFT:TotalDebit>
        <nsSAFT:TotalCredit>12000.00</nsSAFT:TotalCredit>
        
        <nsSAFT:Journal>
            <nsSAFT:JournalID>GL</nsSAFT:JournalID>
            <nsSAFT:Description>Главен журнал</nsSAFT:Description>
            
            <nsSAFT:Transaction>
                <nsSAFT:TransactionID>JE-2026-001</nsSAFT:TransactionID>
                <nsSAFT:Period>1</nsSAFT:Period>
                <nsSAFT:PeriodYear>2026</nsSAFT:PeriodYear>
                <nsSAFT:TransactionDate>2026-01-15</nsSAFT:TransactionDate>
                <nsSAFT:SourceID>USER</nsSAFT:SourceID>
                <nsSAFT:Description>Продажба на стоки</nsSAFT:Description>
                <nsSAFT:BatchID>BATCH-001</nsSAFT:BatchID>
                <nsSAFT:SystemEntryDate>2026-01-15</nsSAFT:SystemEntryDate>
                <nsSAFT:GLPostingDate>2026-01-15</nsSAFT:GLPostingDate>
                <nsSAFT:CustomerID>109876543210</nsSAFT:CustomerID>
                
                <nsSAFT:TransactionLine>
                    <nsSAFT:RecordID>1</nsSAFT:RecordID>
                    <nsSAFT:AccountID>411</nsSAFT:AccountID>
                    <nsSAFT:TaxpayerAccountID>411.01</nsSAFT:TaxpayerAccountID>
                    <nsSAFT:CustomerID>109876543210</nsSAFT:CustomerID>
                    <nsSAFT:Description>Вземане от клиент</nsSAFT:Description>
                    <nsSAFT:DebitAmount>
                        <nsSAFT:Amount>1200.00</nsSAFT:Amount>
                    </nsSAFT:DebitAmount>
                    <nsSAFT:TaxInformation>
                        <nsSAFT:TaxType>100010</nsSAFT:TaxType>
                        <nsSAFT:TaxCode>100211</nsSAFT:TaxCode>
                        <nsSAFT:TaxPercentage>20.00</nsSAFT:TaxPercentage>
                        <nsSAFT:TaxBase>1000.00</nsSAFT:TaxBase>
                        <nsSAFT:TaxAmount>
                            <nsSAFT:Amount>200.00</nsSAFT:Amount>
                        </nsSAFT:TaxAmount>
                    </nsSAFT:TaxInformation>
                </nsSAFT:TransactionLine>
                
                <nsSAFT:TransactionLine>
                    <nsSAFT:RecordID>2</nsSAFT:RecordID>
                    <nsSAFT:AccountID>702</nsSAFT:AccountID>
                    <nsSAFT:TaxpayerAccountID>702.01</nsSAFT:TaxpayerAccountID>
                    <nsSAFT:CustomerID>109876543210</nsSAFT:CustomerID>
                    <nsSAFT:Description>Приход от продажба</nsSAFT:Description>
                    <nsSAFT:CreditAmount>
                        <nsSAFT:Amount>1000.00</nsSAFT:Amount>
                    </nsSAFT:CreditAmount>
                    <nsSAFT:TaxInformation>
                        <nsSAFT:TaxType>100010</nsSAFT:TaxType>
                        <nsSAFT:TaxCode>100211</nsSAFT:TaxCode>
                        <nsSAFT:TaxPercentage>20.00</nsSAFT:TaxPercentage>
                        <nsSAFT:TaxBase>1000.00</nsSAFT:TaxBase>
                        <nsSAFT:TaxAmount>
                            <nsSAFT:Amount>200.00</nsSAFT:Amount>
                        </nsSAFT:TaxAmount>
                    </nsSAFT:TaxInformation>
                </nsSAFT:TransactionLine>
                
                <nsSAFT:TransactionLine>
                    <nsSAFT:RecordID>3</nsSAFT:RecordID>
                    <nsSAFT:AccountID>453</nsSAFT:AccountID>
                    <nsSAFT:TaxpayerAccountID>453.01</nsSAFT:TaxpayerAccountID>
                    <nsSAFT:CustomerID>109876543210</nsSAFT:CustomerID>
                    <nsSAFT:Description>ДДС от продажба</nsSAFT:Description>
                    <nsSAFT:CreditAmount>
                        <nsSAFT:Amount>200.00</nsSAFT:Amount>
                    </nsSAFT:CreditAmount>
                </nsSAFT:TransactionLine>
            </nsSAFT:Transaction>
        </nsSAFT:Journal>
    </nsSAFT:GeneralLedgerEntries>
    
    <nsSAFT:SourceDocumentsMonthly>
        <nsSAFT:SalesInvoices>
            <nsSAFT:NumberOfEntries>1</nsSAFT:NumberOfEntries>
            <nsSAFT:TotalDebit>1200.00</nsSAFT:TotalDebit>
            <nsSAFT:TotalCredit>1200.00</nsSAFT:TotalCredit>
            
            <nsSAFT:Invoice>
                <nsSAFT:InvoiceNo>INV-001</nsSAFT:InvoiceNo>
                <nsSAFT:InvoiceType>FT</nsSAFT:InvoiceType>
                <nsSAFT:TransactionID>JE-2026-001</nsSAFT:TransactionID>
                <nsSAFT:Period>1</nsSAFT:Period>
                <nsSAFT:PeriodYear>2026</nsSAFT:PeriodYear>
                <nsSAFT:TransactionDate>2026-01-15</nsSAFT:TransactionDate>
                <nsSAFT:CustomerID>109876543210</nsSAFT:CustomerID>
                <nsSAFT:Lines>
                    <nsSAFT:Line>
                        <nsSAFT:LineNumber>1</nsSAFT:LineNumber>
                        <nsSAFT:ProductCode>PROD001</nsSAFT:ProductCode>
                        <nsSAFT:ProductDescription>Стока А</nsSAFT:ProductDescription>
                        <nsSAFT:Quantity>10</nsSAFT:Quantity>
                        <nsSAFT:UnitPrice>100.00</nsSAFT:UnitPrice>
                        <nsSAFT:UnitOfMeasure>C62</nsSAFT:UnitOfMeasure>
                        <nsSAFT:CreditAmount>1000.00</nsSAFT:CreditAmount>
                        <nsSAFT:Tax>
                            <nsSAFT:TaxType>100010</nsSAFT:TaxType>
                            <nsSAFT:TaxCode>100211</nsSAFT:TaxCode>
                            <nsSAFT:TaxPercentage>20.00</nsSAFT:TaxPercentage>
                            <nsSAFT:TaxAmount>200.00</nsSAFT:TaxAmount>
                        </nsSAFT:Tax>
                    </nsSAFT:Line>
                </nsSAFT:Lines>
                <nsSAFT:DocumentTotals>
                    <nsSAFT:TaxExclusiveAmount>1000.00</nsSAFT:TaxExclusiveAmount>
                    <nsSAFT:TaxAmount>200.00</nsSAFT:TaxAmount>
                    <nsSAFT:GrossTotal>1200.00</nsSAFT:GrossTotal>
                </nsSAFT:DocumentTotals>
            </nsSAFT:Invoice>
        </nsSAFT:SalesInvoices>
        
        <nsSAFT:Payments>
            <nsSAFT:NumberOfEntries>0</nsSAFT:NumberOfEntries>
            <nsSAFT:TotalDebit>0.00</nsSAFT:TotalDebit>
            <nsSAFT:TotalCredit>0.00</nsSAFT:TotalCredit>
        </nsSAFT:Payments>
        
        <nsSAFT:PurchaseInvoices>
            <nsSAFT:NumberOfEntries>0</nsSAFT:NumberOfEntries>
            <nsSAFT:TotalDebit>0.00</nsSAFT:TotalDebit>
            <nsSAFT:TotalCredit>0.00</nsSAFT:TotalCredit>
        </nsSAFT:PurchaseInvoices>
    </nsSAFT:SourceDocumentsMonthly>
</nsSAFT:AuditFile>
```

## Приложение Ж: Rust пълен генератор ( boilerplate )

```rust
use quick_xml::events::{BytesDecl, BytesEnd, BytesStart, BytesText, Event};
use quick_xml::Writer;
use std::io::{Cursor, Write};
use rust_decimal::Decimal;
use chrono::NaiveDate;

pub struct SaftGenerator<W: Write> {
    writer: Writer<W>,
}

impl<W: Write> SaftGenerator<W> {
    pub fn new(writer: W) -> Self {
        Self {
            writer: Writer::new_with_indent(writer, b' ', 2),
        }
    }
    
    fn write_element(&mut self, name: &str, content: &str) -> Result<(), quick_xml::Error> {
        self.writer.write_event(Event::Start(BytesStart::new(name)))?;
        self.writer.write_event(Event::Text(BytesText::new(content)))?;
        self.writer.write_event(Event::End(BytesEnd::new(name)))?;
        Ok(())
    }
    
    fn start_element(&mut self, name: &str) -> Result<(), quick_xml::Error> {
        self.writer.write_event(Event::Start(BytesStart::new(name)))
    }
    
    fn end_element(&mut self, name: &str) -> Result<(), quick_xml::Error> {
        self.writer.write_event(Event::End(BytesEnd::new(name)))
    }
    
    pub fn generate_header(&mut self, company: &Company, period: (&str, &str)) -> Result<(), quick_xml::Error> {
        self.start_element("nsSAFT:Header")?;
        
        self.write_element("nsSAFT:TaxAccountingBasis", &company.tax_accounting_basis)?;
        self.write_element("nsSAFT:CompanyName", &company.name)?;
        self.write_element("nsSAFT:CompanyID", &format!("10{}", company.eik))?;
        
        if let Some(ref vat) = company.vat_number {
            self.write_element("nsSAFT:VATRegistrationNumber", &format!("BG{}", vat))?;
        }
        
        self.write_element("nsSAFT:DateCreated", &chrono::Utc::now().format("%Y-%m-%d").to_string())?;
        self.write_element("nsSAFT:CurrencyCode", &company.currency)?;
        self.write_element("nsSAFT:SelectionStartDate", period.0)?;
        self.write_element("nsSAFT:SelectionEndDate", period.1)?;
        self.write_element("nsSAFT:SoftwareID", &company.software_id)?;
        self.write_element("nsSAFT:SoftwareVersion", &company.software_version)?;
        
        self.end_element("nsSAFT:Header")?;
        Ok(())
    }
    
    pub fn generate_accounts(&mut self, accounts: &[Account]) -> Result<(), quick_xml::Error> {
        self.start_element("nsSAFT:GeneralLedgerAccounts")?;
        
        for acc in accounts {
            self.start_element("nsSAFT:Account")?;
            self.write_element("nsSAFT:AccountID", &acc.saft_account_id)?;
            self.write_element("nsSAFT:AccountDescription", &acc.name)?;
            self.write_element("nsSAFT:TaxpayerAccountID", &acc.code)?;
            self.write_element("nsSAFT:AccountType", &acc.account_type)?;
            
            if let Some(ref bal) = acc.opening_debit {
                self.write_element("nsSAFT:OpeningDebitBalance", &bal.to_string())?;
            }
            if let Some(ref bal) = acc.opening_credit {
                self.write_element("nsSAFT:OpeningCreditBalance", &bal.to_string())?;
            }
            
            self.end_element("nsSAFT:Account")?;
        }
        
        self.end_element("nsSAFT:GeneralLedgerAccounts")?;
        Ok(())
    }
    
    pub fn generate_journal_entry(&mut self, entry: &JournalEntry) -> Result<(), quick_xml::Error> {
        self.start_element("nsSAFT:Transaction")?;
        
        self.write_element("nsSAFT:TransactionID", &entry.id)?;
        self.write_element("nsSAFT:TransactionDate", &entry.date.to_string())?;
        self.write_element("nsSAFT:Description", &entry.description)?;
        self.write_element("nsSAFT:GLPostingDate", &entry.gl_posting_date.to_string())?;
        
        for (i, line) in entry.lines.iter().enumerate() {
            self.start_element("nsSAFT:TransactionLine")?;
            self.write_element("nsSAFT:RecordID", &(i + 1).to_string())?;
            self.write_element("nsSAFT:AccountID", &line.account_code)?;
            
            if let Some(ref cp_id) = line.counterpart_id {
                self.write_element("nsSAFT:CustomerID", cp_id)?;
            }
            
            if let Some(debit) = line.debit {
                self.start_element("nsSAFT:DebitAmount")?;
                self.start_element("nsSAFT:Amount")?;
                self.write_element("nsSAFT:Amount", &debit.to_string())?;
                self.end_element("nsSAFT:Amount")?;
                self.end_element("nsSAFT:DebitAmount")?;
            }
            
            if let Some(credit) = line.credit {
                self.start_element("nsSAFT:CreditAmount")?;
                self.write_element("nsSAFT:Amount", &credit.to_string())?;
                self.end_element("nsSAFT:CreditAmount")?;
            }
            
            self.end_element("nsSAFT:TransactionLine")?;
        }
        
        self.end_element("nsSAFT:Transaction")?;
        Ok(())
    }
}

pub fn generate_full_saft(data: &SaftExportData) -> Result<String, quick_xml::Error> {
    let buffer = Cursor::new(Vec::new());
    let mut gen = SaftGenerator::new(buffer);
    
    gen.writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), None)))?;
    
    let mut root = BytesStart::new("nsSAFT:AuditFile");
    root.push_attribute(("xmlns:nsSAFT", "mf:nra:dgti:dxxxx:declaration:v1"));
    gen.writer.write_event(Event::Start(root))?;
    
    gen.generate_header(
        &data.company,
        (&data.period_start.to_string(), &data.period_end.to_string())
    )?;
    
    gen.end_element("nsSAFT:AuditFile")?;
    
    let result = gen.writer.into_inner().into_inner();
    Ok(String::from_utf8_lossy(&result).to_string())
}
```

## Приложение З: Често задавани въпроси (FAQ)

### Q1: Трябва ли да променя целия си сметкоплан?
**A:** Не. SAF-T изисква **мапване** между вашите сметки и номенклатурата на НАП. Вашите сметки остават непроменени вътрешно.

### Q2: Какво става, ако контрагент няма ЕИК?
**A:** Използвайте префикс 15 и вътрешен идентификатор от вашата система. Но това ще генерира предупреждение.

### Q3: Мога ли да подавам SAF-T ръчно?
**A:** Технически да, но не е практично. Файлът за един месец може да има хиляди редове. Нужен е софтуер.

### Q4: Какви глоби има за грешки?
**A:** Глобите се определят от НАП. Основното е: неподаване = глоба, грешни данни = ревизия.

### Q5: Работи ли SAF-T за всички видове фирми?
**A:** Да, с различни настройки (TaxAccountingBasis): A = търговски, P = бюджетни, BANK, INSURANCE.

### Q6: Трябва ли да включвам всички фактури в SourceDocuments?
**A:** Да, всички фактури за периода трябва да са включени. Връзката с GeneralLedgerEntries е чрез TransactionID.

### Q7: Как се обработват сторнирани фактури?
**A:** Като нова транзакция с отрицателни суми или като CreditNote в SourceDocuments.

### Q8: Какво е PhysicalStock при OnDemand отчет?
**A:** Това е моментна снимка на наличностите към датата на заявката. Изисква се за търговци със склад.
