# Personal Finance Management System

**A production-grade data platform for real-time personal finance analytics, built on PostgreSQL, dbt, and Streamlit.**

This project demonstrates core data engineering patterns: ETL pipeline orchestration, unstructured data extraction, trigger-based workflows, and analytical data modeling—applied to a real domain with measurable complexity.

---

## The Problem

Personal finance tracking typically lives in spreadsheets or disconnected apps. This creates two problems:

1. **Data fragmentation**: Bank statements, manual expenses, and investment holdings are siloed across PDFs, credit card statements, and Google Sheets.
2. **Analysis debt**: Deriving insights (spending trends, savings rate, fund allocation) requires manual aggregation and recalculation.

**Why it matters for data engineering**: Building a unified system forces you to handle realistic challenges: parsing unstructured bank PDFs, maintaining data quality across multiple sources, modeling complex financial hierarchies, and keeping an analytical layer in sync with source data.

---

## What This System Does

### Core Features
- **Unified expense tracking**: Ingest bank statements (PDF) + manual entries → normalized expense table
- **Income & savings reconciliation**: Monthly income vs. spending calculations, fund-level allocation tracking
- **Time-series analysis**: Monthly/yearly trends, category breakdowns, fund performance
- **Multi-source data fusion**: Combine PDF statements, Google Sheets house data, and manual entries into a single source of truth

### Why It's Interesting

| Aspect | What Happens | Why It's Hard |
|--------|--------------|---------------|
| **PDF parsing** | Extract transaction lines from unstructured bank statements | OCR failures, statement format variations across banks |
| **Data quality** | De-duplicate transactions, handle partial refunds, track prepaid items | Business logic lives in forms; needs validation at multiple layers |
| **Fact tables** | Model expenses with fund categories, travelers, trip attribution | SCD Type 2 for holdings; star schema for drilling across accounts |
| **ETL scheduling** | Sync Google Sheets house data daily, validate freshness | Docker-based scheduler; handles failures & backfills |
| **Trigger logic** | Auto-link fund withdrawals to expenses | DB triggers + application-layer validation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit (Web UI)                          │
│  Income Input │ Expense Input │ Monthly Calcs │ Historical Stats│
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐  ┌───▼──────────┐  ┌─▼──────────────┐
│  PDF Statement │  │ Google Sheets│  │ Manual Input   │
│  Upload        │  │ (House Data) │  │ (Transactions) │
└───────┬────────┘  └───┬──────────┘  └─┬──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   ETL Pipeline (Python)         │
        │  • pdfplumber extraction        │
        │  • Text-to-table parsing        │
        │  • Category matching            │
        │  • Deduplication (UNIQUE const) │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   PostgreSQL (12 tables)        │
        │  ├─ expense (raw)               │
        │  ├─ income                      │
        │  ├─ transactions (fund mgmt)    │
        │  └─ [holdings, prices, signals] │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   dbt (SQL modeling layer)      │
        │  intermediate_expenses_with     │
        │  _summary (filters + calcs)     │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  Streamlit (Analytics Views)    │
        │  Charts │ Tables │ KPIs         │
        └─────────────────────────────────┘
```

### Key Design Decisions

**Why PostgreSQL + dbt + Streamlit?**
- **PostgreSQL**: Supports constraints (UNIQUE, CHECK, FK) for data quality enforcement. Triggers auto-sync fund transactions when expenses change.
- **dbt**: Single source of truth for transformations (e.g., summary categories, fund allocations). Version-controlled, testable SQL.
- **Streamlit**: Rapid iteration on dashboards. Session state handles complex multi-step forms (input → review → confirm).

**Why Docker Compose?**
- Dev/prod parity: `.env.dev` and `.env.prod` configs; `docker-compose.yml` + overlay files separate concerns.
- Services are isolated: app ↔ db ↔ dbt via Docker network. No "works on my machine."

---

## Data Engineering in Action

### 1. Unstructured PDF → Structured Data

**The Problem**: Bank PDFs have inconsistent layouts. RBC, PC, and Scotia Red each format statements differently.

**The Solution**: 
```python
# app/modules/upload_pdf/pipeline/rbc/rbc_extracted.py
with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        for line in text.splitlines():
            if '$' in line and any(month in line for month in months):
                # Extract transaction line with regex
```

**Why it matters**: 
- Regex patterns are specific per bank (RBC has different date formats than Scotia).
- Text extraction can fail on poor scans; fallback to manual entry.
- No magic — pattern matching + human review = reliable extraction.

**Trade-off**: Could use ML (paddleOCR, LayoutLM), but regex + regex is 95% accurate and maintainable. ML adds complexity without proportional gain here.

---

### 2. Data Quality: Constraints + Triggers

**The Problem**: Manual expense entry is error-prone. Users can:
- Enter the same transaction twice
- Create a fund withdrawal without selecting a fund category
- Update an expense, but the linked fund transaction becomes stale

**The Solution**:

```sql
-- Prevent duplicates at the DB level
ALTER TABLE expense ADD CONSTRAINT unique_expense_entry 
  UNIQUE (date, items, amount, source_notes);

-- Validate fund category + withdrawal requirement
ALTER TABLE expense ADD CONSTRAINT fund_required_when_excluded
  CHECK (
    (exclude_from_monthly = FALSE) OR 
    (exclude_from_monthly = TRUE AND target_fund_category IS NOT NULL)
  );

-- Auto-sync fund transactions when expense amount changes
CREATE TRIGGER expense_update_trigger AFTER UPDATE ON expense
  FOR EACH ROW EXECUTE FUNCTION sync_linked_transactions();
```

**Why it matters**:
- Constraints fail fast, catch bugs at insert time.
- Triggers keep fund ledger in sync without app-layer orchestration.
- Single source of truth: the DB enforces business rules.

**Trade-off**: Triggers are harder to debug than app-layer logic. But they guarantee consistency even if the app crashes mid-request.

---

### 3. dbt: The Analytical Layer

**The Problem**: Every dashboard query recalculates the same things (spending by category, summary categories, fund allocations). Duplication + inconsistency.

**The Solution**:
```sql
-- dbt/budget_project/models/intermediate/intermediate_expenses_with_summary.sql
SELECT
    *,
    COALESCE(
        (amount / NULLIF(amount_for_number_of_travelers, 0)) * paid_for_number_of_travlerers, 
        0
    ) AS amount_I_spend,
    {{ get_summary_category('category') }} AS summary_category
FROM {{ source('public', 'expense') }}
WHERE exclude_from_monthly = FALSE AND category != 'House'
```

This view:
- Filters out fund-withdrawal expenses (already tracked as transactions).
- Calculates per-person expense share (for group trip tracking).
- Applies business logic (summary category macro) in one place.
- Gets refreshed daily via `dbt run` in Docker.

**Why it matters**:
- Single source of truth for all dashboards.
- Testable: can write assertions (e.g., "summary_category is never NULL").
- Maintainable: change logic once, all dashboards update.

---

### 4. ETL Scheduling: House Data Sync

**The Problem**: House expenses live in a Google Sheet (maintained separately). Need daily sync to stay current.

**The Solution**:
```python
# etl/house_pipeline.py
def run_house_etl():
    raw_data = extract(CREDS_PATH)  # gspread → Pandas
    transformed_data = transformation(raw_data)  # Normalize schema
    new_rows_count = load_new_house_data(transformed_data)  # UPSERT via ON CONFLICT
```

Runs daily via Docker: `dbt run` container + APScheduler.

**Why it matters**:
- Separates concerns: house data is maintained separately (Google Sheets) but merged into analytics (Postgres).
- Idempotent: `ON CONFLICT DO NOTHING` means re-running is safe.
- Traceable: logs capture when/why sync failed.

---

### 5. Monthly Calculations: Business Logic at the Right Layer

**The Problem**: Users set financial goals (saving target, retirement %, travel fund limits). System must:
- Calculate actual savings
- Allocate across fund categories
- Create fund transaction records

**Why it's complex**:
- Formula depends on thresholds (if savings < half the goal, travel fund = 0).
- Results are deterministic: running calculation again should delete old records, not duplicate them.
- Links to two data layers: expenses (from dbt view) + fund categories (manual).

**The Solution**: 
```python
# app/pages/6_Monthly_Calculation.py
def rerun_monthly_saving(...):
    # 1. Delete old "saved from" deposits for this month
    cursor.execute("""
        DELETE FROM transactions
        WHERE EXTRACT(YEAR FROM date) = %s
          AND EXTRACT(MONTH FROM date) = %s
          AND source_notes LIKE 'saved from%%'
    """, (year, month))
    
    # 2. Recalculate and insert fresh
    for fund_category, amount in calculate_allocations(...):
        insert_transaction_data(...)
```

**Why it matters**:
- Business logic lives in the app, not the DB (easier to test, iterate).
- Explicit delete-then-insert ensures no duplicates.
- User-facing: "Rerun Calculation" button means corrections are self-service.

---

## Data Model Highlights

### Fact Tables

**`expense`** (raw transactional events)
- Captures every spending event, enriched with category, trip, and fund allocation info.
- Constraint: `UNIQUE (date, items, amount, source_notes)` prevents duplicates from re-uploads.
- Optional: `exclude_from_monthly` flag + `target_fund_category` for fund-linked expenses.

**`transactions`** (fund movement ledger)
- Records all fund movements: deposits (from income), withdrawals (to spending), transfers (between accounts).
- Fact: `source_notes LIKE 'saved from%'` = auto-calculated; otherwise manually entered.
- Key link: `expense_id` foreign key ties fund withdrawals back to originating expenses.

### Intermediate Tables (via dbt)

**`intermediate_expenses_with_summary`**
- Filters: excludes fund-withdrawal expenses and house (tracked separately).
- Enrichment: adds `summary_category` (e.g., "Grocery", "Donation and Gifts", "Daily Expenses").
- Calculation: `amount_I_spend` = per-person share for group expenses.

---

## Testing & Validation

### Data Quality Checks
- **DB constraints**: UNIQUE, CHECK, NOT NULL, FKs catch bad data at insert.
- **dbt assertions** (future): test summary_category is never NULL, expense amounts are positive.
- **Application validation**: Pydantic models validate form input before insert.

### Manual Tests
- Re-upload same statement twice: UNIQUE constraint prevents duplicates. ✅
- Update expense amount: trigger syncs linked fund transaction. ✅
- Delete expense with fund withdrawal: cascade delete cleans up transactions. ✅

---

## What You'd Learn from This Codebase

### For Data Engineers
1. **ETL pipeline design**: Extract (pdfplumber), transform (Pandas), load (PostgreSQL). Idempotent, traceable, testable.
2. **Data quality**: Constraints + triggers + application validation = defense in depth.
3. **Analytical modeling**: dbt view abstractions, macro reuse, single source of truth.
4. **Scheduling**: Docker-based ETL orchestration with error handling.

### For Full-Stack Data Roles
1. **End-to-end system**: From form input → DB constraints → dbt views → Streamlit dashboards.
2. **Business logic**: Allocation formulas, fund tracking, multi-source reconciliation.
3. **Real-world complexity**: PDFs, Google Sheets integration, user corrections, audit trails.

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 14+ (or use Docker)

### Quick Start
```bash
# Clone repo
git clone <repo-url>
cd personal_finance_management

# Create .env.dev (see .env.example)
cp .env.example .env.dev
# Fill in: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, etc.

# Start services
./dev.sh up

# Access app
# Streamlit: http://localhost:8502
# PostgreSQL: localhost:5433
```

For detailed setup, see [SETUP.md](./docs/SETUP.md).

---

## Project Structure

```
.
├── app/
│   ├── pages/           # Streamlit pages (income, expense, calculations, etc.)
│   ├── modules/         # Reusable components (forms, charts, ETL pipelines)
│   ├── models/          # Pydantic validation (Income, Expense, Transaction)
│   ├── backend/         # DB queries (expense_backend.py, income_backend.py, etc.)
│   └── utils/           # Helpers (validation, CSS, data constants)
├── dbt/
│   └── budget_project/
│       ├── models/      # SQL transformations (views & staging)
│       └── macros/      # Reusable SQL functions (get_summary_category)
├── etl/                 # Standalone ETL scripts (house_pipeline.py)
├── database/            # Schema & seed data
│   ├── 01_init_schema.sql
│   └── 02_seed_dev.sql
├── docker-compose.yml   # Base services (app, db, dbt)
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── Dockerfile
```

---

## Key Files to Review

**If you want to understand the data model:**
→ `database/01_init_schema.sql` (12 tables, constraints, triggers)

**If you want to see ETL in action:**
→ `app/modules/upload_pdf/pipeline/` (PDF parsing + transformation)

**If you want to see dbt modeling:**
→ `dbt/budget_project/models/intermediate/` (SQL views with macros)

**If you want to see constraint-driven design:**
→ `app/models/expense_models.py` + `app/models/transaction_models.py` (Pydantic validation)

**If you want to see trigger-based workflows:**
→ Search `CREATE TRIGGER` in `database/01_init_schema.sql`

---

## Trade-offs & Why

| Decision | Alternative | Why This Wins |
|----------|-------------|---------------|
| PostgreSQL over NoSQL | MongoDB, DynamoDB | Schema enforcement + constraints for financial data (accuracy > flexibility). |
| dbt over in-app logic | Calculate in Streamlit | Testable, version-controlled, reusable across all dashboards. |
| Pydantic validation + DB constraints | Just app validation | Defense in depth; catches bugs even if app logic changes. |
| Regex PDF parsing over ML | paddleOCR, LayoutLM | 95% accuracy with zero dependency overhead. ML adds complexity without gain. |
| Docker Compose over manual setup | Manual postgres + venv | Dev/prod parity, isolated services, reproducible environment. |

---

## Next Steps for This Project

- [ ] Add dbt tests (e.g., assert summary_category is never NULL)
- [ ] Implement CI/CD (GitHub Actions: lint, test, Docker push)
- [ ] Add data lineage tracking (dbt docs, OpenLineage)
- [ ] ETF price API integration + signal-based buy recommendations
- [ ] AI chatbot (RAG + PostgreSQL vector search) for natural-language queries

---

## Contact

This project was built as a portfolio demonstration. It shows:
- **How to build real data systems** with realistic constraints (unstructured inputs, quality concerns, multi-source reconciliation).
- **Why architecture matters**: constraints, dbt modeling, and trigger-based workflows prevent bugs and keep systems maintainable.

**Hire me if you need someone who:**
- Designs data pipelines that are production-ready, not just "working."
- Understands data quality as a first-class concern (constraints, validation, testing).
- Can bridge data engineering and analytics (SQL + Python + orchestration).
- Ships systems, not just code.

---

## License

MIT
