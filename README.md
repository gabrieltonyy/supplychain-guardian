# SupplyChain Guardian

AI-powered autonomous supply chain risk management platform built for the AMD AI Hackathon.

SupplyChain Guardian is a multi-agent system designed to help enterprises detect, analyze, and respond to supply chain disruptions in real time. The platform combines deterministic risk analytics, vector search, workflow automation, and AI-assisted reasoning to reduce operational disruption, procurement delays, and supplier risk exposure.

The system continuously monitors supplier ecosystems using external intelligence feeds such as weather, geopolitical activity, financial indicators, logistics disruptions, and tariff changes. When elevated risk is detected, the platform autonomously evaluates mitigation strategies, simulates supplier-switch scenarios, and initiates procurement workflows through RFQ generation and approval routing.

---

# Core AI Agents

## 1. Risk Analyst Agent

* Ingests real-time external risk signals
* Computes weighted supplier risk scores
* Detects anomalies using historical baselines
* Produces explainable risk summaries

## 2. Mitigation Strategist Agent

* Discovers alternative suppliers
* Uses vector similarity search for supplier matching
* Simulates switching scenarios
* Ranks mitigation strategies using TOPSIS multi-criteria analysis

## 3. Execution Agent

* Generates RFQs automatically
* Routes procurement approvals
* Dispatches supplier communications
* Tracks supplier responses and execution workflows

## 4. Compliance Agent *(in progress)*

* Regulatory validation
* Audit trail generation
* Trade restriction checks
* Governance and policy enforcement

---

# Key Features

* Real-time supplier risk scoring
* Multi-agent orchestration with LangGraph
* AI-assisted procurement workflows
* Deterministic scoring and simulation engines
* Explainable AI reasoning
* Vector-based supplier discovery using Qdrant
* PostgreSQL + Redis + Qdrant architecture
* FastAPI backend
* React/TypeScript frontend
* Async event-driven processing
* Human-in-the-loop approval workflows

---

# Technology Stack

## Backend

* FastAPI
* LangGraph
* SQLAlchemy
* PostgreSQL
* Redis
* Qdrant

## AI / ML

* Ollama + Mistral
* LangChain
* Vector embeddings
* Multi-agent orchestration

## Infrastructure

* Docker
* Kubernetes
* AsyncIO
* APScheduler

---

# AMD Hackathon Focus

This project explores how AI agents and accelerated AI infrastructure can improve operational resilience in global supply chains. The system is designed to demonstrate:

* autonomous enterprise workflows,
* real-time risk intelligence,
* AI-assisted decision support,
* and scalable multi-agent orchestration.

---

# Architecture Overview

```text
External Risk Feeds
    ↓
Risk Analyst Agent
    ↓
Mitigation Strategist Agent
    ↓
Execution Agent
    ↓
Compliance Agent
    ↓
Dashboard + Reports + Alerts
```

---

# Project Structure

```text
backend/     → FastAPI backend and AI agents
frontend/    → React frontend dashboard
infra/       → Docker, Kubernetes, Terraform
data/        → Mock feeds and seed data
docs/        → PRD, architecture, and system docs
```

---

# Current Status

Current MVP implementation includes:

* foundational backend architecture,
* risk analysis engine,
* mitigation planning workflows,
* execution automation framework,
* and agent orchestration pipeline.

Compliance automation and advanced analytics are currently under development.

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

API available at:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/api/v1/health
```

---

# Vision

SupplyChain Guardian aims to evolve into a fully autonomous enterprise resilience platform capable of proactively preventing supply chain failures before they impact operations.

The long-term goal is to combine AI agents, predictive analytics, and autonomous execution workflows into a unified operational intelligence platform for global supply chains.

---

# License

MIT License
