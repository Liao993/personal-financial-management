# Personal Finance Management App

A production-minded finance data app I built to solve my own fund allocation problem: different savings goals live in different bank accounts, while spending data arrives from bank statement PDFs, manual entries, and a separate house-expense source. The app turns those scattered inputs into a PostgreSQL-backed finance system with PDF ingestion, ETL, dbt models, fund transaction logic, and Streamlit analytics dashboards.

This project is written as both a working personal tool and a portfolio case study for data analytics, data engineering, and full-stack data app development.

## Portfolio Snapshot

**Problem solved:** Track income, expenses, savings funds, travel spending, house expenses, TFSA/RRSP contribution room, and portfolio holdings without manually reconciling everything in spreadsheets.

**Core highlight:** Upload bank statement PDFs, extract transactions, review/edit the parsed rows, validate the data, and load clean expense records into PostgreSQL.

**Secondary ETL highlight:** Pull house-expense data from an external source, normalize it, stage it, and load only new records into the analytics database.

**Analytics highlight:** Use historical dashboards to monitor savings rate, spending mix, travel savings, house costs, current fund balances, and long-term financial trends.

## What The App Does

- Ingests bank statement PDFs from multiple banks including RBC, PC, and Scotia Red.
- Converts semi-structured PDF text into expense rows through bank-specific extraction and transformation modules.
- Provides a Streamlit review step before loading statement data into the database.
- Supports manual income, manual expense, fund transaction, and portfolio holding entry.
- Tracks fund categories separately from physical bank accounts, so savings goals can be managed even when money moves between accounts.
- Automatically creates linked fund-withdrawal transactions for expenses that should be paid from savings instead of monthly cash flow.
- Updates linked withdrawal records when the original expense amount or notes change.
- Syncs house-expense data through a separate Python ETL pipeline.
- Uses dbt to create an analytical view for historical spending, summary categories, travel shares, and house summaries.
- Provides dashboards for monthly calculations, current savings status, historical statistics, travel spending, house expenses, TFSA/RRSP tracking, statement viewing, and portfolio holdings.

## Skills Demonstrated

| Area | Evidence in this project |
| --- | --- |
| Data engineering | PDF extraction pipelines, Google Sheets-style external ETL, staging tables, idempotent inserts, Dockerized services |
| Analytics engineering | dbt project, SQL transformation layer, reusable macro for summary categories, curated analytical view |
| Database design | PostgreSQL schema, primary keys, uniqueness constraints, foreign keys, trigger-based synchronization |
| Data quality | Validation before insert, duplicate prevention, human-in-the-loop review for parsed statements |
| Product thinking | Workflow-specific pages for upload, review, correction, monthly recalculation, and historical analysis |
| Backend engineering | Modular Python backend functions for expenses, income, transactions, statements, portfolio, and live prices |
| Visualization | Streamlit dashboards with KPIs, tables, bar charts, line charts, pie charts, and category drilldowns |
| DevOps | Docker Compose dev/prod environments, service health checks, persistent volumes, environment-based configuration |

## Architecture

```text
Bank PDFs          Manual Input          External House Data
   |                    |                       |
   v                    v                       v
PDF extraction      Streamlit forms        Python ETL
bank-specific       validation             extract/transform/load
pipelines                |                       |
   |                    v                       v
   +-------------> PostgreSQL <------------------+
                    |
                    v
                  dbt
        curated analytical models
                    |
                    v
             Streamlit dashboards
      monthly, historical, travel, house,
      savings, statement viewer, portfolio
```

### Main Components

- `app/Home.py` - Streamlit entry point and navigation guidance.
- `app/pages/` - User-facing workflows and analytics pages.
- `app/modules/upload_pdf/pipeline/` - Bank statement extraction, transformation, review, and load flow.
- `etl/` - External house-expense ETL pipeline.
- `database/` - PostgreSQL schema, seed data, trigger logic, and portfolio schema.
- `dbt/budget_project/` - Analytics engineering layer.
- `docker-compose*.yml` - Local development and production service definitions.

## Data Pipeline Highlights

### 1. Bank Statement PDF ETL

The statement upload flow is designed around reliability rather than blind automation:

1. The user selects a bank and uploads a statement PDF.
2. A bank-specific extractor reads statement text with `pdfplumber`.
3. A transformation module converts raw text into structured transaction rows.
4. Streamlit displays an editable review table.
5. Validated rows are inserted into PostgreSQL with the selected bank saved as the payment method.

Relevant files:

- `app/modules/upload_pdf/pipeline/pipeline.py`
- `app/modules/upload_pdf/pipeline/rbc/`
- `app/modules/upload_pdf/pipeline/pc/`
- `app/modules/upload_pdf/pipeline/scotia_red/`
- `app/modules/upload_pdf/pipeline/load.py`

Why this matters: bank statements are semi-structured data. The project shows practical extraction engineering, source-specific parsing, validation, and a review workflow that protects the database from bad ingestion.

### 2. External House Expense ETL

House expenses are maintained outside the app and synced through a separate ETL pipeline:

1. Extract raw data using service credentials.
2. Transform the data into the app's expense schema.
3. Load records into a staging table with explicit column types.
4. Insert only new rows into the main `expense` table using `ON CONFLICT DO NOTHING`.
5. Drop the staging table after a successful load.

Relevant files:

- `etl/house_pipeline.py`
- `etl/extract.py`
- `etl/transformed.py`
- `etl/load.py`

This demonstrates a common data engineering pattern: external source ingestion, schema normalization, staging, idempotent load, and database-safe typing.

### 3. dbt Analytics Layer

The dbt model `intermediate_expenses_with_summary` centralizes analytical business logic:

- Calculates the user's share of group expenses.
- Maps granular categories into summary categories through a dbt macro.
- Builds house summary categories.
- Excludes fund withdrawals and house records where including them would double-count monthly spending.

Relevant files:

- `dbt/budget_project/models/intermediate/intermediate_expenses_with_summary.sql`
- `dbt/budget_project/macros/get_summary_category.sql`
- `dbt/budget_project/models/sources.yml`

For a data analyst or analytics engineer, this is the layer that makes dashboard definitions consistent and maintainable.

## Database And Business Logic

The PostgreSQL layer protects financial consistency:

- `expense` stores normalized spending records.
- `income` stores earning records.
- `transactions` stores fund deposits, withdrawals, and transfers.
- `unique_expense_entry` prevents duplicate expense loads by date, item, amount, and source note.
- `transactions.expense_id` links auto-created withdrawals back to the original expense.
- `ON DELETE CASCADE` removes linked fund transactions when an expense is deleted.
- Insert and update triggers create and synchronize fund-withdrawal transactions.

The trigger flow is especially important for the app's real use case. When an expense is marked as excluded from monthly spending because it should be paid from a savings fund, PostgreSQL automatically creates the matching withdrawal. If the expense later changes because of a refund or correction, the linked withdrawal is updated too.

Relevant files:

- `database/01_init_schema.sql`
- `database/03_expense_transaction_sync.sql`
- `app/pages/16_Expense_Editor.py`
- `app/modules/transaction/`

## Analytics Features

The app is built to answer practical finance questions:

- How much did I save this month after expenses?
- Which fund categories need deposits or withdrawals?
- How are current savings distributed across accounts and goals?
- How has my savings rate changed historically?
- Which categories drive spending changes year over year?
- How much have I spent on travel, and which trips/categories explain it?
- How much are house costs contributing to my overall financial picture?
- How are TFSA/RRSP and portfolio holdings tracking?

Important dashboard areas:

- `app/pages/6_Monthly_Calculation.py`
- `app/pages/8_Historical_Stats.py`
- `app/pages/9_Traveling_Spending_Stats.py`
- `app/pages/10_Current_Saving_Status.py`
- `app/pages/11_House_Expenses.py`
- `app/pages/12_TFSA_RRSP.py`
- `app/pages/13_Statement_Viewer.py`
- `app/pages/14_Portfolio_Holdings.py`

## Tech Stack

- **Python** for application logic and ETL.
- **Streamlit** for the app UI and analytics dashboards.
- **PostgreSQL** for durable storage and database-enforced consistency.
- **dbt-postgres** for analytics modeling.
- **pdfplumber** for statement text extraction.
- **Pandas** and **SQLAlchemy** for data transformation and loading.
- **Plotly**, **Matplotlib**, and **Seaborn** for visual analytics.
- **Docker Compose** for reproducible dev/prod environments.
- **gspread** and **google-auth** for external spreadsheet-style source integration.
- **yfinance** for portfolio price support.

## Local Development

Create a local environment file named `.env.dev`. The compose files expect database settings, account/fund settings, optional mortgage settings, and any external-source credentials needed for the house ETL.

After `.env.dev` is populated, start the development stack:

```bash
./dev.sh up
```

The development app runs at:

```text
http://localhost:8502
```

Useful development commands:

```bash
./dev.sh restart
./dev.sh reload-sample
./dev.sh dbt
./dev.sh logs
./dev.sh psql
```

Production uses the production compose overlay:

```bash
./prod.sh up
```

## Suggested Portfolio Screenshots

Add screenshots under a folder like `docs/images/` and reference them from this README. To protect private data, use sample data, blurred merchant names, or cropped views.

Recommended screenshots:

1. **Statement upload and review** - Show the PDF upload workflow after extraction, with the editable transaction table visible. This proves the PDF-to-database pipeline.
2. **Historical stats dashboard** - Show yearly or monthly spending and savings trends. This is the best screenshot for data analyst storytelling.
3. **Current saving status** - Show fund balances across categories/accounts. This communicates the original business problem: savings goals split across bank accounts.
4. **Travel spending analytics** - Show trip/category breakdowns to demonstrate custom analytical dimensions beyond simple expense tracking.
5. **House expenses dashboard** - Show the external ETL source integrated into the same analytics system.
6. **Statement viewer** - Show a filtered query/result page to demonstrate operational data access and auditability.
7. **Database/dbt proof screenshot** - Optional but strong for engineering recruiters: a screenshot of dbt output or the Postgres schema/trigger file beside a dashboard.

Suggested README image layout:

```md
## Screenshots

### PDF Statement Ingestion
![PDF statement ingestion review](docs/images/pdf-statement-review.png)

### Historical Savings And Spending
![Historical finance dashboard](docs/images/historical-stats.png)

### Fund Balances
![Current saving status dashboard](docs/images/current-saving-status.png)

### Travel Analytics
![Travel spending dashboard](docs/images/travel-stats.png)
```

## Why This Project Matters

This is not only a dashboard. It is a small production data system with ingestion, validation, storage, transformation, analytics, and operational workflows. The project demonstrates that I can take an ambiguous personal finance problem, design a data model, automate messy source ingestion, enforce data quality, and build a working application around the analysis.

For data analyst roles, it shows dashboarding, metrics design, category modeling, trend analysis, and financial storytelling.

For data engineer or software engineer roles, it shows ETL design, PostgreSQL modeling, dbt transformations, Dockerized deployment, modular Python architecture, and database-backed workflow automation.
