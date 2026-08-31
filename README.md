**ATRR — Agentic Transaction Recovery & Replanning**

ATRR (Agentic Transaction Recovery & Replanning) is a transaction recovery platform that helps recover failed transactions through constraint-aware recovery planning, policy verification, customer approval, execution, and adaptive replanning.

Instead of stopping at a failed recovery attempt, ATRR evaluates available recovery options, selects the best valid action, verifies merchant policy constraints, executes the action, records the outcome, and can select another available plan when an execution attempt fails.

Overview

Failed transactions can create customer dissatisfaction, merchant losses, and unnecessary manual intervention. ATRR provides a structured recovery workflow that evaluates available recovery actions against transaction requirements and merchant policies.

The core recovery flow is:

Failed Transaction
        |
        v
Transaction Intent
        |
        v
Candidate Discovery
        |
        v
Constraint Validation
        |
        v
Recovery Plan Generation
        |
        v
Recovery Plan Ranking
        |
        v
Decision Agent
        |
        v
Policy Verification
        |
        v
Customer Approval
        |
        v
Execution
      /     \
     /       \
 Success    Failure
    |          |
    v          v
Recovered   Replanning
               |
               v
         Decision Agent
               |
               v
        Next Safe Action

Key Features

Constraint-Aware Recovery

Recovery candidates are evaluated against transaction requirements such as:

Maximum customer budget

Minimum product rating

Delivery deadline

Failed product exclusion

Only valid candidates are converted into executable recovery plans.

Recovery Plan Generation

Valid candidates are transformed into structured recovery plans containing information such as:

Plan ID

Action type

Product ID

Customer cost

Expected revenue

Expected merchant value

Constraint status

Recovery explanation

Recovery Plan Ranking

Recovery plans are ranked using expected merchant value so that the system can prioritize the best available valid recovery option.

Decision Agent

The Decision Agent receives the current recovery context and selects the highest-ranked recovery plan that has not already been attempted.

Its context includes:

Transaction intent

Available recovery plans

Merchant policy

Previous recovery attempts

Merchant Policy Verification

Before execution, the selected recovery action is checked against the applicable merchant policy.

Customer Approval

Customer approval is treated as an explicit execution gate. If approval is not provided, the recovery process stops without executing another recovery action.

Automatic Replanning

When a recovery execution attempt fails, ATRR records the failed attempt and updates the recovery context. Previously attempted actions are excluded from subsequent decisions so another available recovery plan can be selected.

Recovery Plan 1
      |
      v
Execution
      |
      v
   FAILURE
      |
      v
Failed Attempt Recorded
      |
      v
Replanning Triggered
      |
      v
Decision Agent
      |
      v
Previously Attempted Plan Excluded
      |
      v
Next Available Recovery Plan
      |
      v
Execution
      |
      v
   SUCCESS
      |
      v
  RECOVERED

Audit Trail

ATRR records the recovery lifecycle using structured audit events such as:

RECOVERY_STARTED
PLANS_GENERATED
AGENT_DECISION
ACTION_PROPOSED
POLICY_CHECK
EXECUTION
REPLANNING_TRIGGERED
RECOVERY_COMPLETED
RECOVERY_FAILED

System Architecture

                         +----------------------+
                         |    React Frontend    |
                         |   Recovery Console   |
                         +----------+-----------+
                                    |
                                    | HTTP / JSON
                                    v
                         +----------------------+
                         |     FastAPI API      |
                         |   /api/v1/recover    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Recovery Orchestrator|
                         +----------+-----------+
                                    |
          +-------------------------+-------------------------+
          |             |             |            |          |
          v             v             v            v          v
     Candidate      Recovery      Decision      Policy    Execution
      Service       Service         Agent       Service    Service
                                    |
                                    v
                            Replanning Service
                                    |
                                    v
                              Audit Service

Technology Stack

Backend

Python 3.11

FastAPI

Pydantic

Uvicorn

Pytest

Frontend

React 19

Vite

Axios

Tailwind CSS

Lucide React

React Router

Recharts

Data

The current prototype uses CSV-based data for:

Products

Inventory

Merchants

Offers

Delivery options

Merchant policies

Development Tools

Git

GitHub

Visual Studio Code

PowerShell

npm

Project Structure

ATRR-Agentic-Transaction-Recovery/
│
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── agent_context.py
│       │   └── decision_agent.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   └── recovery.py
│       │
│       ├── core/
│       │   └── __init__.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── agent_decision.py
│       │   ├── audit_event.py
│       │   ├── candidate.py
│       │   ├── constraint_result.py
│       │   ├── execution_request.py
│       │   ├── execution_result.py
│       │   ├── merchant_policy.py
│       │   ├── policy_decision.py
│       │   ├── recovery_action.py
│       │   ├── recovery_attempt.py
│       │   ├── recovery_plan.py
│       │   ├── recovery_request.py
│       │   └── transaction_intent.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── audit_service.py
│       │   ├── candidate_service.py
│       │   ├── constraint_service.py
│       │   ├── execution_service.py
│       │   ├── merchant_data_service.py
│       │   ├── policy_service.py
│       │   ├── recovery_action_service.py
│       │   ├── recovery_orchestrator.py
│       │   ├── recovery_service.py
│       │   └── replanning_service.py
│       │
│       └── main.py
│
├── data/
│   ├── delivery_options.csv
│   ├── inventory.csv
│   ├── merchants.csv
│   ├── offers.csv
│   ├── policies.csv
│   └── products.csv
│
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   │
│   ├── src/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── test_audit_service.py
│   ├── test_candidate_service.py
│   ├── test_constraint_service.py
│   ├── test_decision_agent.py
│   ├── test_execution_service.py
│   ├── test_merchant_data_service.py
│   ├── test_policy_service.py
│   ├── test_recovery_action_service.py
│   ├── test_recovery_orchestrator.py
│   ├── test_recovery_service.py
│   ├── test_replanning_service.py
│   └── test_transaction_intent.py
│
├── .gitignore
├── README.md
└── requirements.txt

Installation

Prerequisites

Make sure you have:

Python 3.11+

Node.js and npm

Git

Clone the Repository

git clone https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery.git
cd ATRR-Agentic-Transaction-Recovery

Create and Activate the Python Environment

Windows PowerShell:

python -m venv venv
.\venv\Scripts\Activate.ps1

If the virtual environment already exists, activate it instead:

.\venv\Scripts\Activate.ps1

Install Backend Dependencies

pip install -r requirements.txt

Install Frontend Dependencies

cd frontend
npm install
cd ..

Running the Application

Start the Backend

From the project root:

python -m uvicorn backend.app.main:app --reload --port 8000

The backend runs at:

http://127.0.0.1:8000

Health Check

Open:

http://127.0.0.1:8000/health

Expected response:

{
  "status": "ok",
  "service": "ATRR",
  "message": "ATRR backend is running"
}

API Documentation

FastAPI interactive documentation is available at:

http://127.0.0.1:8000/docs

Start the Frontend

Open a second terminal:

cd frontend
npm run dev

Vite will provide a local URL such as:

http://localhost:5173

If the port is already in use, Vite will automatically select another available port.

Recovery API

Endpoint

POST /api/v1/recover

Example Request

{
  "transaction_id": "TXN-DEMO-001",
  "category": "headphones",
  "max_budget": 5000,
  "min_rating": 4.0,
  "delivery_deadline_days": 2,
  "failed_product_id": "P003",
  "customer_approved": true
}

Example Successful Response

{
  "transaction_id": "TXN-DEMO-001",
  "status": "RECOVERED",
  "selected_action": {
    "action_id": "SUB-P001",
    "action_type": "substitute_product",
    "product_id": "P001",
    "customer_cost": 4499.0,
    "merchant_value": 809.82,
    "constraint_safe": true
  }
}

The complete API response also includes recovery attempts and audit events.

Customer Approval Flow

Customer approval acts as an explicit execution safeguard.

Recovery Plan
      |
      v
Policy Check
      |
      v
Customer Approval?
     /       \
   YES        NO
    |          |
    v          v
 Execute     Blocked
    |          |
    v          v
Recovered   CUSTOMER_APPROVAL_REQUIRED

Replanning Flow

ATRR supports adaptive recovery when an execution attempt fails.

The Decision Agent receives the previous recovery attempts as part of the current recovery context. Previously attempted actions are excluded from further selection.

Attempt 1
   |
   v
Execution Failure
   |
   v
Recovery Attempt Recorded
   |
   v
REPLANNING_TRIGGERED
   |
   v
Decision Agent
   |
   v
Attempted Action Excluded
   |
   v
Attempt 2
   |
   v
Execution Success
   |
   v
RECOVERED

The replanning behavior is covered by:

tests/test_recovery_orchestrator.py

with the test:

test_agent_replans_after_execution_failure

Audit Trail

A typical successful recovery produces:

RECOVERY_STARTED
        ↓
PLANS_GENERATED
        ↓
AGENT_DECISION
        ↓
ACTION_PROPOSED
        ↓
POLICY_CHECK
        ↓
EXECUTION
        ↓
RECOVERY_COMPLETED

A recovery involving an execution failure can additionally include:

EXECUTION
    |
    v
REPLANNING_TRIGGERED
    |
    v
AGENT_DECISION
    |
    v
ACTION_PROPOSED
    |
    v
POLICY_CHECK
    |
    v
EXECUTION
    |
    v
RECOVERY_COMPLETED

Frontend

The React frontend provides a transaction recovery console where users can:

Enter transaction details

Set the maximum budget

Set the minimum rating

Set the delivery deadline

Specify the failed product

Provide customer approval

Start a recovery request

View recovery status

View the selected recovery action

View recovery activity and audit events

The frontend communicates with the FastAPI backend through the recovery API.

Example Recovery Scenario

A sample recovery request can use:

Transaction ID       : TXN-DEMO-001
Category             : headphones
Maximum budget       : ₹5,000
Minimum rating       : 4.0
Delivery deadline    : 2 days
Failed product       : P003
Customer approval    : Approved

A successful recovery can result in:

Failed Product
      |
      v
P003
      |
      v
Candidate Evaluation
      |
      v
P001 Selected
      |
      v
Policy Approved
      |
      v
Execution Successful
      |
      v
RECOVERED

Example selected recovery:

Product ID       : P001
Customer Cost    : ₹4,499
Merchant Value   : ₹809.82
Constraint Check : Passed
Status           : RECOVERED

UI Flow

Recovery Request
       |
       v
Process Status
       |
       v
Selected Recovery
       |
       v
Recovery Activity

The interface is designed as a transaction operations console focused on the recovery workflow, decisions, outcomes, and auditability.

Testing

Run the complete backend test suite from the project root:

python -m pytest

Current test result:

59 passed

The test suite covers:

Transaction intent

Candidate selection

Constraint validation

Decision Agent

Execution service

Merchant data service

Policy service

Recovery action service

Recovery service

Recovery orchestration

Replanning service

Audit service

Frontend Production Build

To verify the frontend production build:

cd frontend
npm run build

The current frontend production build has been successfully verified.

Design Principles

Safety

Recovery actions must satisfy customer and merchant constraints before execution.

Customer Control

Customer approval remains an explicit execution gate.

Adaptability

Failed recovery attempts can trigger another decision using the updated recovery context.

Traceability

Recovery decisions, policy checks, execution outcomes, and recovery results are recorded in the audit trail.

Current Implementation Status

The current prototype includes:

Constraint-aware candidate selection

Recovery plan generation

Recovery plan ranking

Decision Agent

Policy verification

Customer approval gate

Execution gate

Recovery attempt tracking

Replanning after execution failure

Audit trail

FastAPI recovery API

React frontend

Frontend-to-backend integration

Backend Tests

59 passed

Frontend Build

Production build successful

Future Improvements

Possible future enhancements include:

Persistent transaction storage

Production database integration

Real merchant API integration

Real payment gateway integration

Real-time transaction monitoring

Authentication and role-based access

Advanced recovery analytics

Notification services

Production-grade observability

Distributed execution workers

Additional recovery action types

Enhanced recovery simulation and failure scenarios

Screenshots

Suggested screenshots for the repository include:

screenshots/
├── dashboard.png
├── recovery-success.png
├── audit-trail.png
└── replanning.png

Recommended screenshots:

ATRR Transaction Recovery Dashboard

Successful Recovery Result

Recovery Status Pipeline

Recovery Audit Trail

Replanning Scenario

Demo Flow

A basic demonstration can follow this sequence:

1. Enter a failed transaction.
2. Define the customer's recovery constraints.
3. Provide customer approval.
4. Start the recovery process.
5. Review the selected recovery plan.
6. Verify policy status.
7. Execute the selected recovery action.
8. View the final recovery result.
9. Review the audit trail.

For an adaptive recovery scenario:

First Action
     |
     v
Execution Failure
     |
     v
Replanning
     |
     v
Next Safe Action
     |
     v
Successful Recovery

Repository

GitHub Repository:

https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery

Author

Anvi Pardhi

Information Technology Student

Interested in software engineering, full-stack development, AI systems, and building practical technology solutions.

License

This project was developed as a hackathon prototype for exploring safe, adaptive, and traceable transaction recovery workflows.