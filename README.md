# 💸 Personal Finance Management Platform

![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B.svg?style=for-the-badge&logo=dbt&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama%20LLM-000000.svg?style=for-the-badge&logo=ollama&logoColor=white)

## 📌 Project Overview
A **production application** (not a notebook demo) that runs my own household finances: multi-bank PDF statement ingestion, fund-based savings tracking across accounts, portfolio holdings, and a dbt analytics layer — all containerized with separate dev/prod environments and a live production deployment.

**Business problem solved:** Savings goals (retirement, house, travel, emergency) live across multiple physical bank accounts, while spending data arrives from PDFs, manual entry, and an external sheet. This app unifies all of it into one PostgreSQL-backed system with automated reconciliation, so "how much can I actually spend" and "am I on track" are always a query away instead of a spreadsheet reconciliation project.

---

## 🏗️ Architecture

```text
Bank PDFs        Manual Input       External Sheet        Live Market Prices
   │                  │                    │                      │
   ▼                  ▼                    ▼                      ▼
Bank-specific    Streamlit forms      Python ETL          yfinance fetch
PDF extractors   + validation         extract/transform/          │
   │                  │               load (staged,               │
   ▼                  ▼               idempotent)                 │
   └──────────────────┴──────────────────┴──────────────┬─────────┘
                                                          ▼
                                                    PostgreSQL
                                          (triggers auto-sync fund
                                           withdrawals on expense
                                           insert/update/delete)
                                                          │
                                                          ▼
                                                        dbt
                                          (summary categories, house
                                           reporting logic, curated view)
                                                          │
                                                          ▼
                                              Streamlit Dashboards
                                    monthly calc · historical stats · travel ·
                                    house · TFSA/RRSP · portfolio · statement viewer
                                                          │
                                                          ▼
                                          AI Semantic Chat (local LLM router)
                                     natural language → metric catalog → SQL
                                        (Ollama picks a metric, never writes SQL)
```

---

## 📊 Data Model

| Table | Grain | Purpose |
|---|---|---|
| `income` | Transaction | Earning records (regular + irregular) |
| `expense` | Transaction | Spending, with fund-withdrawal flags and split allocation |
| `transactions` | Transaction | Deposits, withdrawals, transfers — by **fund category**, decoupled from physical account |
| `portfolio_holdings` | Lot | ETF/stock units by account, category, and purpose |
| `etf_prices` | Daily | Latest price per ticker + live USD→CAD FX rate |
| `dbt_budget.intermediate_expenses_with_summary` | View | Curated analytics layer — summary categories, house rollups, per-traveler cost splits |

---

## ⚙️ Key Engineering Decisions

- **Fund-based accounting, not account-based.** Money is tracked by *savings goal* (fund category), independent of which bank account physically holds it — the schema and every dashboard is built around this abstraction.
- **Database-enforced consistency via triggers**, not application logic. When an expense is marked as fund-withdrawal-required, a Postgres `AFTER INSERT` trigger auto-creates the linked withdrawal transaction; an `AFTER UPDATE` trigger re-syncs it if the amount changes (secondary-fund-first absorption logic for partial refunds). `ON DELETE CASCADE` removes linked transactions automatically. This means correctness doesn't depend on every code path remembering to update two tables.
- **Separate dev/prod Docker Compose stacks** (`docker-compose.yml` + `.dev.yml`/`.prod.yml` overlays, driven by `dev.sh`/`prod.sh`), with isolated Postgres volumes, ports, and seeded sample data for dev so the pipeline is fully testable without touching real financial data.
- **dbt as the single source of analytical truth** — a macro-driven summary-category model that every dashboard queries, so category logic isn't duplicated across chart code.
- **Idempotent, staged ETL** for the external house-expense source: extract → stage → `INSERT ... ON CONFLICT DO NOTHING` → drop staging table, safe to rerun on any schedule.
- **Multi-bank PDF ingestion** — bank-specific regex extractors (RBC, PC, Scotia) normalize semi-structured statement text into a common schema, with a human-in-the-loop Streamlit review/edit step before anything is validated (Pydantic) and loaded.
- **AI Semantic Layer (in progress)** — a local, self-hosted LLM (Ollama, Llama 3.1) acts strictly as a **router**, not a SQL generator: it selects one metric from a governed `semantic_layer.yml` catalog (including derived/formula metrics like savings rate) and a date range; the actual SQL is templated by a `query_builder`, never written by the model. This keeps natural-language Q&A auditable and prevents LLM-generated SQL from touching a financial database directly — a governance pattern, not just a chatbot demo.
- **Mobile-first quick-entry surface** — a separate lightweight page for logging income/expenses/transactions from a phone, reusing the same validation and backend layer as the desktop forms.

---

## 🖥️ Feature Surface

| Page | What it does |
|---|---|
| Monthly Calculation | Applies a configurable savings formula to allocate income across funds; supports rerun/recalculation when past expenses change |
| Current Saving Status | Live pivot of fund balance × account, combining manual transactions and auto-generated withdrawals |
| Historical Stats | Multi-year trend charts: spending mix, savings rate, category drift |
| Portfolio Holdings | ETF/stock tracking with live price fetch, CAD-normalized valuation, allocation-by-category charts |
| Expense Editor | Correct/refund/delete past expenses; linked fund transactions resync automatically |
| Statement Viewer | Ad-hoc SQL query tool with guardrails (DML/DDL confirmation step, schema hints) |
| AI Semantic Chat | Natural-language Q&A over governed metrics, answered by a local LLM |

---

## 🚀 How to Run

```bash
./dev.sh up          # start dev stack (Postgres :5433, app :8502) with seeded sample data
./dev.sh dbt          # run dbt models
./dev.sh restart      # rebuild + reseed sample data deterministically

./prod.sh up          # start production stack (app :8501)
```

Requires Docker, a `.env.dev` / `.env.prod` file with DB and account/fund config, and (for AI Semantic Chat) a local Ollama instance running `llama3.1:8b`.

---

## 💡 What This Demonstrates

This is a live, self-hosted production system, schema design with trigger-enforced integrity, containerized dev/prod parity, idempotent ETL, a governed dbt analytics layer, and — as the newest addition — a **safety-conscious approach to LLM-assisted analytics** where the model routes intent instead of generating unvetted SQL. It reflects how I actually think about data engineering: correctness at the database layer first, dashboards second, AI as a constrained interface on top rather than a shortcut around governance.
