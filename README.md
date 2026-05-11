# SupplyChain Guardian

<div align="center">

# AI-Powered Autonomous Supply Chain Risk Intelligence Platform

### Built for the AMD AI Hackathon

Detect. Predict. Mitigate. Automate.

</div>

---

## Overview

SupplyChain Guardian is an AI-powered multi-agent platform designed to autonomously detect, analyze, and mitigate supply chain disruptions in real time.

Modern supply chains are increasingly vulnerable to:

- geopolitical instability,
- logistics bottlenecks,
- supplier insolvency,
- tariff fluctuations,
- climate disruptions,
- and operational delays.

Traditional ERP and procurement systems are reactive.

SupplyChain Guardian introduces a proactive AI-driven operational intelligence layer capable of:

- continuously monitoring supplier ecosystems,
- identifying emerging disruptions,
- simulating mitigation strategies,
- autonomously generating procurement workflows,
- and orchestrating enterprise decision support.

The platform combines:

- Multi-Agent AI orchestration
- Real-time external intelligence feeds
- Explainable risk scoring
- Autonomous RFQ workflows
- Supplier vector similarity search
- Human-in-the-loop approvals
- Deterministic simulation engines

---

# Why This Matters

Global supply chain disruptions cost enterprises **trillions annually** through:

- delayed shipments,
- production downtime,
- inventory shortages,
- supplier failures,
- and procurement inefficiencies.

Most organizations still rely on fragmented monitoring systems and manual response workflows.

SupplyChain Guardian transforms supply chain operations from:

Reactive → Predictive → Autonomous.

---

# Key Capabilities

## Real-Time Risk Intelligence

Continuously analyzes:

- supplier financial health,
- geopolitical developments,
- weather disruptions,
- shipping anomalies,
- tariff changes,
- logistics instability,
- and operational anomalies.

---

## Multi-Agent AI Orchestration

The platform uses collaborative AI agents powered by LangGraph workflows.

### Risk Analyst Agent

Responsible for:

- supplier risk scoring,
- anomaly detection,
- external intelligence analysis,
- and explainable risk reasoning.

### Mitigation Strategist Agent

Responsible for:

- discovering alternative suppliers,
- evaluating switching scenarios,
- cost/time tradeoff analysis,
- and mitigation planning.

### Execution Agent

Responsible for:

- autonomous RFQ generation,
- workflow routing,
- approval orchestration,
- and supplier execution coordination.

### Compliance Agent *(In Progress)*

Responsible for:

- regulatory validation,
- trade compliance,
- governance enforcement,
- and audit reporting.

---

# Core Features

- AI-powered autonomous procurement workflows
- Real-time supplier risk scoring
- Explainable AI decision reasoning
- LangGraph multi-agent orchestration
- Human-in-the-loop approvals
- Vector-based supplier discovery
- RFQ lifecycle automation
- Deterministic mitigation simulations
- Async event-driven processing
- Audit and workflow history tracking
- PostgreSQL + Redis + Qdrant architecture
- Scalable API-first backend

---

# Architecture

```text
                    ┌─────────────────────────┐
                    │ External Intelligence   │
                    │-------------------------│
                    │ Weather APIs            │
                    │ Financial APIs          │
                    │ Logistics Feeds         │
                    │ Tariff / Geo Events     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Risk Analyst Agent      │
                    │-------------------------│
                    │ Risk Scoring            │
                    │ Anomaly Detection       │
                    │ Signal Correlation      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Mitigation Strategist   │
                    │-------------------------│
                    │ Supplier Discovery      │
                    │ Scenario Simulation     │
                    │ TOPSIS Optimization     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Execution Agent         │
                    │-------------------------│
                    │ RFQ Automation          │
                    │ Approval Workflows      │
                    │ Supplier Coordination   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Compliance Agent        │
                    │-------------------------│
                    │ Governance Checks       │
                    │ Audit Trails            │
                    │ Trade Validation        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Dashboard & Analytics   │
                    └─────────────────────────┘
```

---

# Tech Stack

## Frontend

- Next.js
- TypeScript
- TailwindCSS
- React Query
- Modern Dashboard UI

## Backend

- FastAPI
- Python
- SQLAlchemy
- AsyncIO
- APScheduler

## AI & Intelligence Layer

- LangGraph
- LangChain
- Ollama
- Mistral
- Vector Embeddings
- Deterministic Risk Engines

## Data & Infrastructure

- PostgreSQL
- Redis
- Qdrant
- Docker
- Kubernetes

---

# AI Workflow Pipeline

```text
External Signals
      ↓
Risk Analysis
      ↓
Anomaly Detection
      ↓
Mitigation Planning
      ↓
Supplier Matching
      ↓
RFQ Generation
      ↓
Approval Workflow
      ↓
Execution & Monitoring
```

---

# Example Workflow

## Scenario

A supplier in Southeast Asia experiences:

- severe weather disruption,
- shipment delays,
- and deteriorating financial indicators.

## SupplyChain Guardian Response

1. Risk Analyst Agent detects abnormal supplier risk patterns
2. Mitigation Strategist identifies alternative suppliers
3. Cost/time simulations are executed
4. Execution Agent generates RFQs automatically
5. Procurement approval workflow is initiated
6. Compliance validation is performed
7. Decision audit trail is stored

All within minutes.

---

# Project Structure

```text
backend/
├── app/
├── agents/
├── workflows/
├── services/
├── models/
├── api/
└── tests/

frontend/
├── app/
├── components/
├── hooks/
├── services/
└── types/

infra/
├── docker/
├── kubernetes/
└── deployment/

docs/
├── architecture/
├── diagrams/
├── workflows/
└── prd/
```

---

# Local Development

## Backend Setup

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

Backend available at:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/api/v1/health
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend available at:

```text
http://localhost:3000
```

---

# Environment Variables

Example backend configuration:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
QDRANT_HOST=localhost
OLLAMA_BASE_URL=http://localhost:11434
```

---

# Demo Highlights

The MVP currently demonstrates:

- Autonomous risk detection
- Supplier anomaly analysis
- AI mitigation reasoning
- Supplier alternative discovery
- RFQ workflow automation
- Approval workflow orchestration
- Real-time operational dashboards

---

# Future Roadmap

- Full compliance automation
- SAP / ERP integrations
- Predictive disruption forecasting
- Autonomous supplier negotiations
- Multi-modal document intelligence
- AI contract analysis
- Real-time global trade monitoring
- Advanced simulation engines
- Enterprise-grade observability

---

# AMD AI Hackathon Focus

This project demonstrates how accelerated AI infrastructure and agentic workflows can transform enterprise supply chain operations through:

- autonomous decision systems,
- operational intelligence,
- scalable multi-agent orchestration,
- and real-time mitigation automation.

---

# Vision

SupplyChain Guardian aims to become the autonomous operating system for enterprise supply chain resilience.

A future where AI agents continuously protect global operations before disruptions become business crises.

---

# Contributors

Built with passion for the AMD AI Hackathon.

Contributions, ideas, and collaboration are welcome.

---

# License

MIT License