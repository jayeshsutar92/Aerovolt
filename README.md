# Aerovolt — UK Wind Generation Forecasting & Analytics

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.3.1-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8.3.5-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/pytest-61%20passed-success.svg?logo=pytest&logoColor=white)](https://pytest.org/)

> **Live Deployment URLs**
> - **Production Frontend:** [https://aerovolt-alpha.vercel.app/](https://aerovolt-alpha.vercel.app/)
> - **Production Backend API:** [https://aerovolt-27cs.onrender.com](https://aerovolt-27cs.onrender.com)
> - **Interactive Swagger Docs:** [https://aerovolt-27cs.onrender.com/docs](https://aerovolt-27cs.onrender.com/docs)
> - **Backend Health Status:** [https://aerovolt-27cs.onrender.com/api/health](https://aerovolt-27cs.onrender.com/api/health)

Aerovolt is a specialized wind generation forecasting and procurement analytics dashboard tailored for participants in the Great Britain (GB) electricity market. It ingests national wind generation forecasts (`WINDFOR`) and half-hourly actual outturns (`FUELHH`) from the **Elexon Insights Solution (BMRS)** API, reconstructs procurement positions without lookahead bias, and evaluates forecast accuracy using industry-standard quantitative metrics (MAE, RMSE, Bias, and WAPE).

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement & Market Relevance](#2-problem-statement--market-relevance)
3. [Features](#3-features)
4. [Screenshots](#4-screenshots)
5. [Technology Stack](#5-technology-stack)
6. [Architecture & Data Flow](#6-architecture--data-flow)
7. [Data Sources & Ingestion](#7-data-sources--ingestion)
8. [Forecast Selection & Temporal Semantics](#8-forecast-selection--temporal-semantics)
9. [Forecast Accuracy Evaluation](#9-forecast-accuracy-evaluation)
10. [Project Structure](#10-project-structure)
11. [Prerequisites](#11-prerequisites)
12. [Local Setup Guide](#12-local-setup-guide)
13. [Environment Configuration](#13-environment-configuration)
14. [API Reference & OpenAPI Docs](#14-api-reference--openapi-docs)
15. [Testing & Quality Verification](#15-testing--quality-verification)
16. [Docker & Containerization](#16-docker--containerization)
17. [Deployment Status](#17-deployment-status)
18. [Current Limitations & Roadmap](#18-current-limitations--roadmap)
19. [AI-Assisted Development Disclosure](#19-ai-assisted-development-disclosure)
20. [License](#20-license)

---

## 1. Project Overview

In the Great Britain electricity market, commercial offtakers and energy utilities contract electrical energy in day-ahead wholesale auctions (such as EPEX SPOT and Nord Pool) to balance anticipated consumer demand and generation assets. 

Because wind power is intermittent and weather-dependent, procurement teams rely heavily on short-term and day-ahead forecast models produced by the National Energy System Operator (NESO). Aerovolt delivers:
- **Decision-Time Replay:** The ability to inspect the exact forecast model published prior to procurement gate closures (e.g. Day-Ahead 17:00 UTC), strictly eliminating data leakage from subsequent intraday revisions.
- **Outturn Benchmarking:** Direct side-by-side comparison of forecasted generation against metered GB transmission outturn.
- **Financial Risk Mitigation:** Quantitative error tracking (MAE, RMSE, and Bias) to identify systematic over-forecasting or under-forecasting patterns that trigger cash-out imbalance penalties.

---

## 2. Problem Statement & Market Relevance

### The Commercial Impact of Forecast Errors
Under the GB Balancing and Settlement Code (BSC) administered by Elexon:
- **Settlement Periods:** Each 24-hour day is divided into 48 half-hour settlement periods (SP 1–48).
- **Gate Closure:** One hour before each settlement period delivery start time, trading ceases and market participants submit their Final Physical Notifications (FPNs).
- **Cash-Out Imbalances:** If a utility over-estimates wind generation and under-delivers, the shortfall is settled at the **System Buy Price (SBP)**, which spikes dramatically during high-demand or low-wind periods. If a utility under-estimates and generates surplus, the excess is cashed out at the **System Sell Price (SSP)**, frequently resulting in lost revenue.

### The Analytical Challenge
Upstream providers publish forecast revisions up to 8 times daily. Reconstructing historical procurement decisions requires isolating records where $\text{publishTime} \le \text{decisionTime}$. Traditional dashboards often fall victim to **lookahead bias** by visualizing post-closure revisions that were physically unavailable when purchasing decisions occurred. Aerovolt strictly enforces temporal boundaries across all services.

---

## 3. Features

- **Procurement Dashboard:**
  - Timeseries visualization (Recharts Area Profile) displaying projected generation across half-hourly settlement intervals.
  - KPI summary cards tracking **Peak Forecast (MW)**, **Average Forecast (MW)**, **Minimum Forecast (MW)**, and total interval counts.
  - Interactive settlement date and half-hour period (1–48) filters.
  - Delivery schedule table detailing `startTime`, `publishTime`, and forecasted MW output.
- **Accuracy & Performance Analytics:**
  - Statistical benchmark cards: **Mean Absolute Error (MAE)**, **Root Mean Squared Error (RMSE)**, **Mean Bias (ME)**, and **Weighted Absolute Percentage Error (WAPE)**.
  - Dual-line comparative timeseries chart overlaying selected forecasts against actual metered outturns.
  - Interval-by-interval settlement breakdown table highlighting signed error ($e_t$) and absolute error ($|e_t|$).
  - Clear visual indicators for missing actuals or missing forecast intervals.
- **Resilient UI Foundation:**
  - Accessible loading states (`LoadingState`) with ambient spinners and descriptive status messaging.
  - Structured error state panels (`ErrorState`) displaying diagnostic details and retry action callbacks.
  - Dark-mode optimized theme built with modern Tailwind CSS v4 and Lucide React icons.

---

## 4. Screenshots

> *Screenshots placeholder: Run the application locally via `npm run dev` to interact with the live UI.*

```text
+------------------------------------------------------------------------------------+
|  Aerovolt  [GB Grid]                                      [Dashboard] [Analytics]  |
|------------------------------------------------------------------------------------|
|  Settlement Date: [ 2026-01-01 ]   Period: [ All Periods (1-48) ]      [ Refresh ]  |
|                                                                                    |
|  [ Peak: 14,250 MW ]   [ Avg: 9,840 MW ]   [ Min: 4,120 MW ]   [ Points: 48 ]      |
|                                                                                    |
|  +------------------------------------------------------------------------------+  |
|  |  Recharts Generation Profile (MW over Settlement Periods 1 - 48)             |  |
|  +------------------------------------------------------------------------------+  |
+------------------------------------------------------------------------------------+
```

---

## 5. Technology Stack

### Frontend
| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | React | `^19.3.1` | Component lifecycle and reactive UI |
| **Language** | TypeScript | `~6.0.3` | Strict type safety across contracts |
| **Build Tool** | Vite | `^8.3.4` | High-speed local dev and production bundling |
| **Styling** | Tailwind CSS | `^4.3.3` | Utility-first styling with `@tailwindcss/vite` |
| **Charts** | Recharts | `^3.10.1` | Timeseries area and dual-line charts |
| **Icons** | Lucide React | `^1.61.0` | Accessible SVG iconography |
| **Linter** | ESLint | `^10.13.0` | Code quality and React Hooks rules |

### Backend
| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | `3.13.7` | High-performance asynchronous backend |
| **Framework** | FastAPI | `0.141.1` | OpenAPI documentation, ASGI routing, CORS |
| **Validation** | Pydantic v2 | `2.13.4` | Request/response parsing and schema validation |
| **Settings** | Pydantic Settings | `2.15.0` | Centralized environment variable loading |
| **Server** | Uvicorn | `0.52.1` | Production ASGI web server |
| **HTTP Client**| HTTPX | `0.28.1` | Asynchronous external Elexon BMRS integration |
| **Test Suite** | Pytest | `9.1.1` | Unit, integration, and mock transport testing |

---

## 6. Architecture & Data Flow

Aerovolt utilizes a decoupled client-server architecture:

```mermaid
graph TD
    subgraph Frontend ["Frontend (React 19 + TypeScript + Vite)"]
        Navbar["Navbar Component"]
        Dashboard["Dashboard Page"]
        Analytics["Analytics Page"]
        ApiClient["API Client (services/api.ts)"]
    end

    subgraph Backend ["FastAPI Backend (Python 3.13)"]
        Main["FastAPI Router (main.py)"]
        HealthRoute["Health Route (/api/health)"]
        Settings["Pydantic Settings (core/config.py)"]
        ForecastSvc["Forecast Service"]
        AnalyticsSvc["Analytics Service"]
        ElexonSvc["Elexon BMRS Service"]
        DateUtils["Datetime Utils (UTC Normalization)"]
    end

    subgraph External ["External Data Sources"]
        ElexonAPI["Elexon Insights API (data.elexon.co.uk)"]
        FUELHH["FUELHH Dataset (Actuals)"]
        WINDFOR["WINDFOR Dataset (Forecasts)"]
    end

    Dashboard --> ApiClient
    Analytics --> ApiClient
    ApiClient -- "HTTP /api/*" --> Main
    Main --> HealthRoute
    Main --> Settings

    ForecastSvc --> DateUtils
    AnalyticsSvc --> DateUtils
    ElexonSvc --> DateUtils

    ForecastSvc --> ElexonSvc
    AnalyticsSvc --> ForecastSvc
    AnalyticsSvc --> ElexonSvc

    ElexonSvc -- "HTTPS GET" --> ElexonAPI
    ElexonAPI --> FUELHH
    ElexonAPI --> WINDFOR
```

---

## 7. Data Sources & Ingestion

Aerovolt integrates directly with the **Elexon Insights Solution (BMRS)** v1 API (`https://data.elexon.co.uk/bmrs/api/v1`):

### 1. `FUELHH` (Half-Hourly Generation by Fuel Type)
- **Endpoint:** `GET /datasets/FUELHH`
- **Description:** Metered transmission outturn aggregated by fuel category.
- **Filter Applied:** `fuelType == "WIND"`.
- **Temporal Resolution:** Half-hourly (30-minute intervals: 00:00, 00:30, 01:00, ..., 23:30 UTC), yielding **48 settlement periods per day** (SP 1–48).
- **Key Fields Extracted:** `settlementDate`, `settlementPeriod`, `generation` (MW), `publishTime`.
- **Timestamp Logic:** When `startTime` is not explicitly provided in the payload, Aerovolt calculates the delivery start timestamp from `settlementDate` and `(settlementPeriod - 1) * 30 minutes` in UTC.

### 2. `WINDFOR` (Wind Generation Forecast)
- **Endpoint:** `GET /datasets/WINDFOR`
- **Description:** Aggregated national wind power generation forecasts published by NESO models up to 8 times daily.
- **Temporal Resolution:** Hourly (60-minute intervals: 00:00, 01:00, 02:00, ..., 23:00 UTC), yielding **24 forecast intervals per day**, mapping to odd settlement periods (SP 1, 3, 5, ..., 47).
- **Key Fields Extracted:** `startTime` (delivery start in UTC), `publishTime` (model publication in UTC), `settlementDate`, `settlementPeriod`, `generation` (projected MW).
- **Sanitization:** Records with upstream formatting errors or lookahead violations ($\text{publishTime} > \text{startTime}$) are automatically rejected during ingestion.

### 3. Data Completeness & Expected Settlement Period Coverage
An audit of upstream Elexon data reveals an important structural difference between actual outturns and forecasts:
- `FUELHH` actuals cover all **48 settlement periods** of the GB settlement day.
- `WINDFOR` forecasts published by NESO for day-ahead procurement operate on a **60-minute cadence**, providing 24 delivery points per day that correspond to the start of each clock hour (odd-numbered settlement periods: SP 1, 3, 5, ..., 47).
- **Absence of Even Periods:** Half-hourly intervals at `:30` past each hour (SP 2, 4, 6, ..., 48) are **genuinely not published** by the system operator in the WINDFOR feed.
- **Data Integrity Guarantee:** In strict adherence to the project specification ("Represent missing records explicitly. Never fabricate values or silently substitute data"), Aerovolt **never synthesizes, interpolates, or imputes** values for missing even periods.
- **UI & Pipeline Alignment:** The comparison pipeline aligns all 48 delivery periods of the settlement day. Periods lacking upstream forecast records are displayed with an explicit `Absent in WINDFOR` badge. Accuracy benchmarks (MAE, RMSE, Bias, and WAPE) are calculated strictly over the 24 paired hourly periods ($N = 24$).

---

## 8. Forecast Selection & Temporal Semantics

In electricity analytics, timestamps carry strict market semantics:
- **Delivery Start Time (`startTime`):** The half-hour window when electrical energy is generated and delivered onto the grid.
- **Publication Time (`publishTime`):** The exact moment the forecast model was generated and released by the system operator.
- **Decision Time ($T_{\text{decision}}$):** The cutoff timestamp representing when a market participant executed their procurement decision.

### Anti-Leakage Selection Algorithm
Implemented in [`backend/app/services/forecast_service.py`](file:///d:/Personal%20Project/Gridbricks/backend/app/services/forecast_service.py):
1. **Filter Candidates:** Exclude any forecast where $\text{publishTime} > T_{\text{decision}}$ or $\text{publishTime} > \text{startTime}$.
2. **Maximize Recency:** For each distinct `startTime`, select the record maximizing $\text{publishTime}$:
   $$\hat{y}(t) = \operatorname{argmax}_{\text{rec}} (\text{rec.publishTime}) \quad \text{s.t.} \quad \text{rec.publishTime} \le \min(T_{\text{decision}}, \text{rec.startTime})$$
3. **Day-Ahead View:** Automatically sets $T_{\text{decision}}$ to 17:00 UTC on $(D - 1)$ for settlement date $D$.
4. **Intraday Gate Closure:** Evaluates positions with an allowable lead time (e.g. 1 hour prior to `startTime`).

---

## 9. Forecast Accuracy Evaluation

Implemented in [`backend/app/services/analytics_service.py`](file:///d:/Personal%20Project/Gridbricks/backend/app/services/analytics_service.py):

Let $y_t$ represent metered actual generation (MW), $\hat{y}_t$ represent selected forecast generation (MW), and $N$ represent the count of complete evaluated intervals:

### 1. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{N} \sum_{t=1}^N |\hat{y}_t - y_t|$$
- **Interpretation:** The average absolute deviation in megawatts, representing expected volume exposure.

### 2. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N (\hat{y}_t - y_t)^2}$$
- **Interpretation:** Heavily penalizes large individual forecast misses, identifying periods of acute volatility.

### 3. Mean Bias / Mean Error (ME)
$$\text{Bias} = \frac{1}{N} \sum_{t=1}^N (\hat{y}_t - y_t)$$
- **Interpretation:** Identifies systematic over-forecasting ($\text{Bias} > 0$, causing utility shortfalls) or under-forecasting ($\text{Bias} < 0$, causing spillages).

### 4. Weighted Absolute Percentage Error (WAPE)
$$\text{WAPE} = \frac{\sum_{t=1}^N |\hat{y}_t - y_t|}{\sum_{t=1}^N y_t} \times 100\%$$
- **Zero-Generation Protection:** Percentage metrics become mathematically undefined or massively inflated when actual generation approaches zero. If total actual generation is below $1.0\text{ MW}$, Aerovolt suppresses WAPE and reports `null` to avoid misleading analytics.

### 5. Mathematical Validation: Why MAE Equals Mean Bias (4,233.125 MW) on 2026-01-01
On the baseline procurement date (`2026-01-01`), both MAE and Mean Bias evaluate to exactly **`4,233.125 MW`**. Investigation confirms that this is mathematically justified by the underlying data:
- For every single one of the $N = 24$ evaluated delivery periods on 2026-01-01, the day-ahead forecast strictly exceeded the metered actual generation ($\hat{y}_t > y_t$).
- The individual interval forecast errors $e_t = \hat{y}_t - y_t$ were all positive, ranging from $+3,212.0\text{ MW}$ (SP 47) to $+5,839.0\text{ MW}$ (SP 11).
- Because $e_t > 0$ for all $t \in \{1, \dots, 24\}$, the absolute value operation has no effect:
  $$|e_t| = e_t \quad \forall \, t \implies \sum_{t=1}^{24} |e_t| = \sum_{t=1}^{24} e_t = 101,595.0\text{ MW}$$
- Therefore, the sample averages are identical:
  $$\text{MAE} = \frac{101,595.0}{24} = 4,233.125\text{ MW} \quad \text{and} \quad \text{Bias} = \frac{101,595.0}{24} = 4,233.125\text{ MW}$$
- This confirms that the identical value is physically and mathematically justified: the day-ahead forecast exhibited uniform positive bias across every hour of January 1, 2026, resulting in zero under-forecasting periods.

---

## 10. Project Structure

```text
Aerovolt/
├── .agent/                      # Project-wide engineering rules & skills
│   ├── rules.md                 # Mandatory behavioral and coding rules
│   └── skills.md                # Energy domain guidelines & code patterns
├── .dockerignore                # Root Docker ignore rules
├── .gitignore                   # Root ignore rules (Python, Node, OS, Agent)
├── docker-compose.yml           # Unified multi-container orchestration
├── README.md                    # Project documentation
├── backend/                     # FastAPI backend application
│   ├── .dockerignore            # Backend container ignore rules
│   ├── .env.example             # Backend environment template
│   ├── .gitignore               # Python cache & env ignores
│   ├── Dockerfile               # Production Python 3.13-slim container
│   ├── myproject.toml           # Project metadata
│   ├── requirements.txt         # Containerized dependency specifications
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Application entry point, CORS, root route
│   │   ├── api/                 # API router organization
│   │   │   ├── __init__.py      # Centralized router aggregation
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py    # Health-check endpoint (/api/health)
│   │   │       ├── forecasts.py # Wind generation forecast endpoint (/api/forecasts)
│   │   │       └── analytics.py # Accuracy & outturn comparison (/api/analytics)
│   │   ├── core/                # Centralized settings & config
│   │   │   ├── __init__.py
│   │   │   └── config.py        # Pydantic Settings (env vars, CORS)
│   │   ├── schemas/             # Pydantic contracts & schemas
│   │   │   ├── __init__.py
│   │   │   ├── actual.py        # ActualGenerationRecord schemas
│   │   │   ├── analytics.py     # Comparison & AccuracyMetrics schemas
│   │   │   ├── common.py        # ErrorDetail, ErrorResponse schemas
│   │   │   └── forecast.py      # ForecastRecord schemas
│   │   ├── services/            # Business & integration services
│   │   │   ├── __init__.py
│   │   │   ├── analytics_service.py # Timeseries alignment & MAE/RMSE
│   │   │   ├── elexon_service.py    # FUELHH & WINDFOR API client
│   │   │   └── forecast_service.py  # Anti-leakage decision-time selection
│   │   └── utils/               # Datetime & UTC normalization helpers
│   │       ├── __init__.py
│   │       └── datetime_utils.py
│   └── tests/                   # Pytest test suite (59 automated tests)
│       ├── conftest.py
│       ├── test_analytics_service.py
│       ├── test_config.py
│       ├── test_datetime_utils.py
│       ├── test_elexon_service.py
│       ├── test_forecast_routes.py
│       ├── test_forecast_service.py
│       ├── test_health.py
│       └── test_schemas.py
└── frontend/                    # React 19 Vite application
    ├── .dockerignore            # Frontend container ignore rules
    ├── .gitignore               # Frontend ignores (node_modules, dist)
    ├── Dockerfile               # Multi-stage Node 22 + Nginx container
    ├── nginx.conf               # Nginx reverse proxy & SPA configuration
    ├── package.json             # NPM dependencies & scripts
    ├── package-lock.json
    ├── vite.config.ts           # Vite config with @tailwindcss/vite
    ├── tsconfig.json            # TypeScript configuration
    ├── tsconfig.app.json
    ├── tsconfig.node.json
    ├── eslint.config.js         # ESLint 10 configuration
    ├── index.html               # Web entry HTML
    ├── public/                  # Static SVG assets
    └── src/
        ├── main.tsx             # React entry point
        ├── index.css            # Tailwind CSS v4 @import
        ├── App.tsx              # Page orchestration & layout
        ├── components/          # Reusable component library
        │   ├── index.ts
        │   ├── layout/
        │   │   ├── Navbar.tsx
        │   │   └── DashboardLayout.tsx
        │   └── common/
        │       ├── LoadingState.tsx
        │       └── ErrorState.tsx
        ├── pages/               # Application view pages
        │   ├── index.ts
        │   ├── Dashboard.tsx    # Forecast overview & chart
        │   └── Analytics.tsx    # MAE/RMSE benchmarks & table
        ├── services/            # Frontend API client
        │   └── api.ts           # Typed fetch wrapper
        └── types/               # TypeScript domain contracts
            ├── index.ts
            ├── actual.ts
            ├── analytics.ts
            ├── common.ts
            └── forecast.ts
```

---

## 11. Prerequisites

Before running Aerovolt locally, ensure the following software is installed on your system:

| Prerequisite | Minimum Version | Recommended Version | Verification Command |
| :--- | :--- | :--- | :--- |
| **Python** | `3.11+` | `3.13.7` | `python --version` |
| **Node.js** | `18+` | `20+` or `22+` | `node --version` |
| **npm** | `9+` | `10+` | `npm --version` |
| **Shell** | Windows PowerShell 5.1+ / PS Core 7+ | PowerShell 7+ | `$PSVersionTable.PSVersion` |

---

## 12. Local Setup Guide

Follow these step-by-step instructions in Windows PowerShell to launch both the backend and frontend locally:

### Step 1: Clone Repository
```powershell
git clone https://github.com/jayeshsutar92/Aerovolt.git
cd Aerovolt
```

### Step 2: Configure & Start Backend
Open a PowerShell terminal:

```powershell
# Navigate into backend directory
cd backend

# Create your local environment file from template
Copy-Item .env.example .env

# (Optional) Create and activate a Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required Python dependencies
pip install fastapi uvicorn pydantic pydantic-settings httpx pytest python-dotenv

# Run the FastAPI development server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*The backend API will start at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

### Step 3: Configure & Start Frontend
Open a **second** PowerShell terminal:

```powershell
# Navigate into frontend directory
cd frontend

# Create your local environment file from template
Copy-Item .env.example .env

# Install npm dependencies
npm install

# Start the Vite development server
npm run dev
```
*The React application will launch at `http://localhost:5173` and will communicate with the local FastAPI backend at `http://127.0.0.1:8000` via `VITE_API_BASE_URL`.*

---

## 13. Environment Configuration

Aerovolt uses clean, environment-based configuration separation for local development, Docker, and cloud deployments (Vercel and Render).

### Backend Configuration (`backend/.env`)

Backend settings are loaded through [`backend/app/core/config.py`](file:///d:/Personal%20Project/Gridbricks/backend/app/core/config.py) from environment variables or a local `backend/.env` file. A reference template is provided in [`backend/.env.example`](file:///d:/Personal%20Project/Gridbricks/backend/.env.example).

| Variable | Type | Default | Description |
| :--- | :---: | :--- | :--- |
| `APP_NAME` | string | `Aerovolt` | Application display name |
| `ENVIRONMENT` | string | `development` | Runtime environment (`development`, `test`, `production`) |
| `VERSION` | string | `0.1.0` | API semver version |
| `DEBUG` | boolean | `false` | Enables verbose debug logs |
| `API_PREFIX` | string | `/api` | Base prefix for all registered API endpoints |
| `CORS_ORIGINS` | string / JSON list | `http://localhost:5173,http://127.0.0.1:5173,https://aerovolt-alpha.vercel.app` | Allowed browser origins (comma-separated or JSON list). Wildcard `*` is strictly rejected in production. Trailing slashes are automatically normalized. |
| `ELEXON_BASE_URL` | string | `https://data.elexon.co.uk/bmrs/api/v1` | Upstream Elexon Insights Solution REST base URL |
| `ELEXON_TIMEOUT_SECONDS` | float | `15.0` | Request timeout in seconds for Elexon BMRS network calls |

### Frontend Configuration (`frontend/.env`)

Frontend environment settings are read by Vite via `import.meta.env` in [`frontend/src/services/api.ts`](file:///d:/Personal%20Project/Gridbricks/frontend/src/services/api.ts). Templates are provided in [`frontend/.env.example`](file:///d:/Personal%20Project/Gridbricks/frontend/.env.example) and [`frontend/.env.production`](file:///d:/Personal%20Project/Gridbricks/frontend/.env.production).

| Variable | Default (Dev) | Default (Prod) | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | `https://aerovolt-27cs.onrender.com` | Base URL used by the frontend API client for all backend requests. |

### Production Deployment Configuration

#### 1. Vercel Project Settings (Frontend: `https://aerovolt-alpha.vercel.app/`)
Under **Project Settings > Environment Variables** on Vercel:
- **`VITE_API_BASE_URL`**: `https://aerovolt-27cs.onrender.com`
*(Note: Because Vite inlines `import.meta.env` at build time, [`frontend/.env.production`](file:///d:/Personal%20Project/Gridbricks/frontend/.env.production) already sets this production default automatically. Setting it in Vercel project settings ensures explicit override capability.)*

#### 2. Render Web Service Settings (Backend: `https://aerovolt-27cs.onrender.com`)
Under **Environment Variables** in the Render Dashboard:
- **`ENVIRONMENT`**: `production`
- **`CORS_ORIGINS`**: `https://aerovolt-alpha.vercel.app,http://localhost:5173,http://127.0.0.1:5173`
*(Allows requests from the production Vercel frontend as well as local development testing.)*
- **`ELEXON_BASE_URL`**: `https://data.elexon.co.uk/bmrs/api/v1`
- **`ELEXON_TIMEOUT_SECONDS`**: `15.0`

> [!IMPORTANT]
> Never commit active `.env` files or credentials to Git. Both `backend/.env` and `frontend/.env` are ignored by `.gitignore`. Use `.env.example` templates for configuration sharing.

---

## 14. API Reference & OpenAPI Docs

The backend automatically serves interactive API documentation:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`

### Registered Endpoints

#### 1. `GET /api/health`
Performs operational health check.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "app": "Aerovolt",
    "environment": "development",
    "version": "0.1.0"
  }
  ```

#### 2. `GET /api/forecasts`
Queries national wind generation forecasts from Elexon `WINDFOR`, applying anti-leakage selection.
- **Query Parameters:**
  - `settlement_date` (string, optional): Target delivery date in `YYYY-MM-DD` format (defaults to `2026-01-01`).
  - `settlement_period` (integer, optional): Specific settlement period (1–48).
  - `decision_time` (string, optional): ISO-8601 decision cutoff; only forecasts published on or before this timestamp are considered.
  - `lead_hours` (float, optional): Lead time prior to delivery window start.
- **Response `200 OK` (`ForecastListResponse`):**
  ```json
  {
    "settlement_date": "2026-01-01",
    "total_count": 24,
    "items": [
      {
        "start_time": "2026-01-01T00:00:00Z",
        "publish_time": "2025-12-31T16:45:00Z",
        "settlement_date": "2026-01-01",
        "settlement_period": 1,
        "generation_mw": 14250.0
      }
    ]
  }
  ```

#### 3. `GET /api/analytics`
Retrieves aligned forecast-versus-actual comparison points and summary error metrics.
- **Query Parameters:**
  - `settlement_date` (string, optional): Target delivery date in `YYYY-MM-DD` format (defaults to `2026-01-01`).
- **Response `200 OK` (`ComparisonResponse`):**
  ```json
  {
    "settlement_date": "2026-01-01",
    "sample_count": 48,
    "metrics": {
      "mae": 4233.125,
      "rmse": 4310.45,
      "bias": 4233.125,
      "wape_percent": 34.52,
      "sample_count": 24
    },
    "points": [
      {
        "start_time": "2026-01-01T00:00:00Z",
        "settlement_date": "2026-01-01",
        "settlement_period": 1,
        "actual_mw": 10016.875,
        "forecast_mw": 14250.0,
        "error_mw": 4233.125,
        "abs_error_mw": 4233.125
      }
    ]
  }
  ```

#### 4. `GET /`
Root index route providing service status and navigation links.
- **Response `200 OK`:**
  ```json
  {
    "message": "Aerovolt backend is running",
    "docs_url": "/docs",
    "health_check": "/api/health"
  }
  ```

---

## 15. Testing & Quality Verification

Aerovolt maintains rigorous automated testing and static analysis standards:

### 1. Backend Pytest Suite
Run the full test suite in `backend/`:
```powershell
cd backend
python -m pytest tests -v
```
**Verified Results:**
- `61 passed in 0.25s`
- Includes tests for:
  - `FUELHH` and `WINDFOR` Elexon parsing, filtering, and error handling with mock transport.
  - Decision-time forecast selection (strictly rejecting forecasts published after decision time).
  - Day-Ahead (D-1 17:00 UTC) and Gate Closure selection logic.
  - Timeseries alignment between 24 hourly WINDFOR forecasts and 48 half-hourly FUELHH actuals.
  - Verification that even periods absent from WINDFOR have `forecast_mw = None` without fabricating data.
  - Exact mathematical validation of `MAE == Mean Bias` under uniform positive over-forecasting.
  - Zero-generation WAPE suppression and empty-state handling.
  - FastAPI route registration and parameter validation (`/api/health`, `/api/forecasts`, `/api/analytics`).
  - Pydantic schema validation and UTC timestamp normalization.
  - CORS origin validation, trailing slash normalization, and production wildcard rejection.
  - Production Vercel origin (`https://aerovolt-alpha.vercel.app`) authorization.

### 2. Frontend ESLint Checks
Run linting in `frontend/`:
```powershell
cd frontend
npm run lint
```
**Verified Results:** `0 errors, 0 warnings`.

### 3. Frontend Production Build & Typecheck
Run type-checking and bundling in `frontend/`:
```powershell
cd frontend
npm run build
```
**Verified Results:** `tsc -b && vite build` compiled 2,517 modules cleanly with production bundle output in `dist/`.

---

## 16. Docker & Containerization

Aerovolt provides a complete, production-grade Docker containerization setup for running both the FastAPI backend and React 19 frontend seamlessly without requiring local Python or Node.js runtime environments.

### Container Architecture

```mermaid
graph LR
    subgraph Host ["Host Environment"]
        Browser["Web Browser (localhost:5173)"]
        ApiUser["API Client / Swagger (localhost:8000)"]
    end

    subgraph DockerNet ["Docker Bridge Network (aerovolt-network)"]
        subgraph FrontendCont ["aerovolt-frontend (nginx:alpine)"]
            Nginx["Nginx Reverse Proxy & Static Server (:80)"]
            StaticFiles["React 19 SPA Assets (dist/)"]
        end

        subgraph BackendCont ["aerovolt-backend (python:3.13-slim)"]
            Uvicorn["Uvicorn ASGI (:8000)"]
            FastApp["FastAPI Application (non-root appuser)"]
        end
    end

    Browser -- "HTTP :5173" --> Nginx
    ApiUser -- "HTTP :8000" --> Uvicorn
    Nginx -- "Proxy /api/ -> :8000/api/" --> Uvicorn
    Uvicorn --> FastApp
    Nginx --> StaticFiles
```

1. **Backend Service (`aerovolt-backend`):**
   - **Base Image:** `python:3.13-slim`.
   - **Isolation:** Dependencies are installed into a clean container environment from [`backend/requirements.txt`](file:///d:/Personal%20Project/Gridbricks/backend/requirements.txt) using `pip install --no-cache-dir`. Local Windows virtual environments (`backend/.venv`) are strictly excluded via [backend/.dockerignore](file:///d:/Personal%20Project/Gridbricks/backend/.dockerignore).
   - **Security:** Runs as a non-privileged `appuser` (UID 1000). Secrets remain outside images.
   - **Health Check:** Periodically probes `http://localhost:8000/api/health` via `curl`.
   - **Port:** Exposes `8000` to the host for direct API testing and Swagger UI.

2. **Frontend Service (`aerovolt-frontend`):**
   - **Multi-Stage Build:**
     - *Stage 1 (Builder):* `node:22-alpine` installs dependencies via `npm ci` and compiles the optimized production bundle (`tsc -b && vite build`).
     - *Stage 2 (Runner):* `nginx:alpine` serves static assets and reverse-proxies `/api/` traffic to `http://backend:8000/api/`.
   - **Routing:** Configured with SPA fallback (`try_files $uri $uri/ /index.html`) in [frontend/nginx.conf](file:///d:/Personal%20Project/Gridbricks/frontend/nginx.conf).
   - **Health Check:** Probes `http://localhost:80/` via `wget`.
   - **Port:** Maps port `80` in the container to port `5173` on the host, maintaining parity with local Vite development.

3. **Multi-Container Orchestration (`docker-compose.yml`):**
   - Coordinates service startup order with `depends_on: { backend: { condition: service_healthy } }`.
   - Connects both containers to an isolated bridge network (`aerovolt-network`).

---

### Docker Command Reference

All commands should be executed from the project root directory in PowerShell or a standard shell:

#### 1. Validate Compose Configuration
Verify syntax, environment variables, and network configurations:
```powershell
docker compose config
```
*Expected Result: Clean YAML dump of resolved services with exit code 0.*

#### 2. Build Container Images
Build both backend and frontend images from scratch:
```powershell
docker compose build --no-cache
```

#### 3. Start Containers in Detached Mode
Launch the complete Aerovolt application stack in the background:
```powershell
docker compose up -d
```
*The services will be accessible at:*
- **Frontend Dashboard:** `http://localhost:5173`
- **Backend API & Health:** `http://localhost:8000/api/health`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`

#### 4. Monitor Service Logs
Stream consolidated logs or logs for a specific service:
```powershell
# Stream all logs
docker compose logs -f

# Stream backend logs only
docker compose logs -f backend

# Stream frontend logs only
docker compose logs -f frontend
```

#### 5. Check Health & Container Status
Inspect operational status and healthcheck results:
```powershell
docker compose ps
```

#### 6. Stop & Remove Containers
Gracefully shut down containers and tear down the bridge network:
```powershell
# Stop and remove containers and networks
docker compose down

# Stop and remove containers, networks, and named volumes
docker compose down -v
```

---

### Containerization Verification Status

- **Configuration Validation:** Successfully verified with `docker compose config` (exit code `0`). Both services, health checks, ports (`8000:8000`, `5173:80`), and network topologies parse cleanly without warnings.
- **Local Daemon Environment:** Docker CLI `29.6.2` and Docker Compose `v5.3.1` are installed on the host. In local Windows development environments, launching container images requires running Docker Desktop with the `com.docker.service` Windows service active.

---

## 17. Deployment Status

- **Cloud Deployment:** Live & Operational
- **Production Frontend:** [https://aerovolt-alpha.vercel.app/](https://aerovolt-alpha.vercel.app/) (Hosted on **Vercel**)
- **Production Backend API:** [https://aerovolt-27cs.onrender.com](https://aerovolt-27cs.onrender.com) (Hosted on **Render**)
- **Live Swagger Documentation:** [https://aerovolt-27cs.onrender.com/docs](https://aerovolt-27cs.onrender.com/docs)
- **Live Health Status:** [https://aerovolt-27cs.onrender.com/api/health](https://aerovolt-27cs.onrender.com/api/health)

### Deployment Architecture & Settings

| Component | Platform | Live URL | Key Environment Variable |
| :--- | :--- | :--- | :--- |
| **Frontend** | Vercel | `https://aerovolt-alpha.vercel.app/` | `VITE_API_BASE_URL=https://aerovolt-27cs.onrender.com` |
| **Backend** | Render | `https://aerovolt-27cs.onrender.com` | `CORS_ORIGINS=https://aerovolt-alpha.vercel.app,http://localhost:5173,http://127.0.0.1:5173` |

#### Vercel Configuration Note
The frontend Vite configuration automatically bundles `VITE_API_BASE_URL` from [`frontend/.env.production`](file:///d:/Personal%20Project/Gridbricks/frontend/.env.production) during production builds, defaulting to `https://aerovolt-27cs.onrender.com`. In your Vercel Project Settings under **Environment Variables**, you can also explicitly set `VITE_API_BASE_URL` to override or redeploy anytime.

#### Render Configuration Note
The FastAPI backend allows `https://aerovolt-alpha.vercel.app` by default in its CORS origin list. If defining custom `CORS_ORIGINS` in the Render Dashboard, include `https://aerovolt-alpha.vercel.app` as a comma-separated origin (or JSON array). Trailing slashes are automatically stripped by the backend settings parser to ensure consistent CORS matching.

---

## 18. Current Limitations & Roadmap

1. **Upstream In-Memory Caching:** External Elexon BMRS API calls currently query the upstream API per request. Adding a caching layer (Redis or in-memory TTL cache) will significantly reduce latency for repeated historical queries.
2. **Database Persistence:** Persisting historical outturn and forecast snapshots to PostgreSQL or SQLite would enable multi-month trend analysis beyond January 2026.
3. **Solar & BESS Expansion:** Expand beyond wind power into solar PV generation outturns and Battery Energy Storage System (BESS) arbitrage analytics.
4. **Intraday Lead Time Sliders:** Add an interactive timeline slider to the UI to visualize how forecast accuracy evolves as the lead time shrinks from 24 hours to 1 hour ahead of gate closure.

---

## 19. AI-Assisted Development Disclosure

In accordance with transparent software development practices:
- This project was developed with assistance from **Antigravity**, an agentic AI coding assistant developed by the Google DeepMind team.
- **Gemini 3.8 Flash** was utilized as the underlying foundation model during the development workflow.
- **Scope of AI Assistance:** AI assistance was employed for architectural scaffolding, implementing FastAPI backend services and Pydantic schemas, authoring React 19 / TypeScript components and Recharts visualizations, creating automated pytest suites with mock transports, and performing repository hygiene.
- **Human Verification:** All generated code, linting suites, and test cases were verified and executed in the local terminal environment.

---

## 20. License

This repository does not currently include an open-source license. All rights are reserved by the project author. For inquiries regarding licensing or commercial evaluation, contact the repository maintainers.
