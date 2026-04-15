# MoneyMap – Personal Finance Management System

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Framework-Django-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_5-7952B3?logo=bootstrap&logoColor=white)
![ChartJS](https://img.shields.io/badge/Charts-Chart.js-FF6384?logo=chartdotjs&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> A full-stack personal finance web app — track income and expenses, plan budgets, monitor investments, and set savings goals, all in one place.

---

## Problem Statement

Most people lose track of their finances because their money data is scattered — bank apps, spreadsheets, mental notes. MoneyMap brings everything into one platform: transactions, budgets, investments, and goals, with visual insights that make financial patterns obvious at a glance.

---

## Screenshots

### Login Page
![Login](DjangoMoneyMap/DjangoMoneyMap/Output_Screenshots/Login.png)

### Dashboard
![Dashboard](DjangoMoneyMap/DjangoMoneyMap/Output_Screenshots/Dashboard.png)

### Transactions Page
![Transactions](DjangoMoneyMap/DjangoMoneyMap/Output_Screenshots/Transactions.png)

### Budget Page
![Budget](DjangoMoneyMap/DjangoMoneyMap/Output_Screenshots/Budget.png)

### Goals Page
![Goals](DjangoMoneyMap/DjangoMoneyMap/Output_Screenshots/Goals.png)

### Investments Page
![Investments](DjangoMoneyMap/DjangoMoneyMap/Output_Screenshots/Investments.png)

---

## Live Demo
https://money-map-kz82.onrender.com

## Features

| Feature | Description |
|---|---|
| Authentication | Secure register / login / forgot password with per-user private data |
| Transaction Tracking | Record income and expense transactions with categories and full history |
| Budget Planner | Set spending limits per category; visual progress bar with over-budget alerts |
| Investment Tracker | Log stocks, mutual funds, or crypto; auto-calculates gain/loss and profit % |
| Savings Goals | Set financial targets with deadlines and track progress |
| Dashboard | Total balance, income, expenses, recent transactions, and Chart.js visualisations |
| Interactive Charts | Spending patterns and investment distribution rendered client-side via Chart.js |
| Financial Blog | Built-in blog articles to improve financial literacy |
| Reports | Summarised financial reports by time period |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| Backend Framework | Django |
| Frontend | Bootstrap 5, JavaScript, HTML, CSS, Chart.js |
| Database | PostgreSQL |
| ORM | Django ORM |
| Authentication | `django.contrib.auth` |
| Charts | Chart.js (via CDN) |
| Templating | Django Templates |

---

## Project Structure

```
MONEYMAP/
│
├── DjangoMoneyMap/             # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── MoneyMapControl/            # Main application — all features in one app
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgot_password.html
│   │   ├── dashboard.html
│   │   ├── transactions.html
│   │   ├── budget.html
│   │   ├── investments.html
│   │   ├── goals.html
│   │   ├── reports.html
│   │   └── blog_detail.html
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                # All Django forms
│   ├── models.py               # All models — Transaction, Budget, Investment, Goal, Blog
│   ├── signals.py              # Django signals (e.g. auto-create profile on user creation)
│   ├── tests.py
│   ├── urls.py
│   └── views.py                # All view logic
│
├── static/
├── staticfiles/
├── Output_Screenshots/         # UI screenshots
│   ├── Dashboard.png
│   ├── Budget.png
│   ├── Goals.png
│   ├── Investments.png
│   ├── Login.png
│   └── Transactions.png
│
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## Database Schema

```
User (django.contrib.auth)
────────────────────────────
id (PK)
username
password (hashed)
email


Transaction                         Category
────────────────────────            ──────────────────
id (PK)                             id (PK)
user_id (FK → User)                 name
type → income | expense             user_id (FK → User)
amount
category_id (FK → Category)
date
note


Budget                              Investment
────────────────────────            ─────────────────────────
id (PK)                             id (PK)
user_id (FK → User)                 user_id (FK → User)
category_id (FK → Category)         name
limit_amount                        type → stock | mutual fund | crypto
period → monthly | weekly           invested_amount
                                    current_value
                                    date

Goal
────────────────────────
id (PK)
user_id (FK → User)
name
target_amount
saved_amount
deadline
```

---

## Key Calculations

```python
# Budget — remaining and over-budget check
remaining = budget.limit_amount - total_spent_in_category
over_budget = total_spent_in_category > budget.limit_amount

# Investment — gain/loss and profit %
gain_loss = current_value - invested_amount
profit_pct = (gain_loss / invested_amount) * 100

# Dashboard — net balance
balance = total_income - total_expenses
```

---

## Getting Started

## Environment Variables
Create a `.env` file in the root:
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

### Prerequisites

```bash
Python 3.8+
pip
```

### Installation

```bash
# Clone the repo
git clone https://github.com/PriyankaRS17/Money_Map.git
cd DjangoMoneyMap

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000**

---

## Usage

**Register / Login** — Create an account. All data is private and isolated per user.

**Transactions** — Add income or expense entries with category, amount, date, and note. View full history with filters.

**Budget** — Set a spending limit per category. The system tracks actual spend against the limit and alerts you when exceeded.

**Investments** — Log an investment with amount invested and current value. MoneyMap auto-calculates gain/loss and profit %.

**Goals** — Set a savings target with a deadline. Update your saved amount as you progress.

**Dashboard** — See your net balance, recent transactions, spending breakdown, and investment distribution in interactive Chart.js charts.

---

## Key Engineering Decisions

- **Single-app architecture (`MoneyMapControl`)** — all models, views, and forms in one app keeps the codebase simple and navigable for a solo project; no unnecessary abstraction overhead
- **Per-user data isolation** — every model has a `user_id` FK; all querysets filtered by `request.user`, preventing any cross-user data leakage
- **Django signals (`signals.py`)** — used for auto-triggered actions on model events (e.g. creating related records automatically on user registration) without cluttering views
- **Budget alerts at view layer** — over-budget check runs against live transaction aggregates on each page load; no separate alert model or scheduled job needed
- **Investment profit % computed dynamically** — calculated from stored `invested_amount` and user-updated `current_value`; keeping the model lean and values always current
- **Chart.js over server-side charts** — dashboard passes aggregated JSON to Chart.js for client-side rendering; reduces server load and enables smooth interactivity

---

## What I'd Improve Next

- [x] Deployed to Render
- [x] Migrated SQLite to PostgreSQL for production
- [ ] Add recurring transactions (auto-log monthly salary, rent)
- [ ] Connect real-time stock/crypto price API (Alpha Vantage / CoinGecko) for live investment values
- [ ] Export transactions as CSV or PDF
- [ ] Email alerts when budget limit is exceeded
- [ ] Write Django `TestCase` unit tests for budget and investment calculation logic
- [ ] Dockerize and deploy to Render / AWS

---

## Author

**Priyanka R P**
priyankapremnath17@gmail.com
[LinkedIn](https://www.linkedin.com/in/priyanka-rp) · [GitHub](https://github.com/PriyankaRS17) · 
