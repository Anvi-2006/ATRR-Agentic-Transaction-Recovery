# ATRR — Agentic Transaction Recovery & Replanning

**ATRR (Agentic Transaction Recovery & Replanning)** is an agentic transaction recovery platform designed to recover failed transactions through constraint-aware recovery planning, merchant policy verification, customer approval, execution control, and adaptive replanning.

Instead of stopping at a failed recovery attempt, ATRR evaluates available recovery options, selects the best valid action, verifies policy constraints, executes the action, records the outcome, and can select another available plan when an execution attempt fails.

---

## Overview

Failed transactions can create customer dissatisfaction, merchant losses, and unnecessary manual intervention.

ATRR provides a structured recovery workflow that evaluates available recovery actions against transaction requirements and merchant policies.

### Core Recovery Flow

```text
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
```

---

## Features

### Constraint-Aware Recovery

ATRR evaluates recovery candidates against transaction requirements such as:

* Maximum customer budget
* Minimum product rating
* Delivery deadline
* Failed product exclusion

Only candidates that satisfy the current constraints are converted into executable recovery plans.

### Recovery Plan Generation

Valid candidates are transformed into structured recovery plans containing:

* Plan ID
* Action type
* Product ID
* Customer cost
* Expected revenue
* Expected merchant value
* Constraint status
* Recovery explanation

### Recovery Plan Ranking

Recovery plans are ranked using expected merchant value so that ATRR can prioritize the best available valid recovery option.

### Decision Agent

The Decision Agent receives the current recovery context and selects the highest-ranked recovery plan that has not already been attempted.

The decision context includes:

* Transaction intent
* Available recovery plans
* Merchant policy
* Previous recovery attempts

### Merchant Policy Verification

Before execution, the selected recovery action is checked against the applicable merchant policy.

### Customer Approval

Customer approval is treated as an explicit execution gate.

If approval is not provided, the recovery process stops without executing another recovery action.

### Automatic Replanning

When a recovery execution attempt fails, ATRR records the failed attempt and updates the recovery context.

Previously attempted actions are excluded from subsequent decisions so another available recovery plan can be selected.

### Audit Trail

ATRR records important recovery events throughout the recovery lifecycle, including:

```text
RECOVERY_STARTED
PLANS_GENERATED
AGENT_DECISION
ACTION_PROPOSED
POLICY_CHECK
EXECUTION
REPLANNING_TRIGGERED
RECOVERY_COMPLETED
RECOVERY_FAILED
```

---

## System Architecture

```text
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
```

---

## Recovery Decision Flow

```text
Failed Transaction
        |
        v
Create Transaction Intent
        |
        v
Find Recovery Candidates
        |
        v
Validate Constraints
        |
        v
Generate Recovery Plans
        |
        v
Rank Recovery Plans
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
Execute Selected Action
        |
        +-------------------+
        |                   |
        v                   v
     SUCCESS             FAILURE
        |                   |
        v                   v
   RECOVERED         Record Attempt
                            |
                            v
                     Replanning
                            |
                            v
                     Decision Agent
                            |
                            v
                    Next Safe Action
```

---

## Technology Stack

### Backend

* Python 3.11
* FastAPI
* Pydantic
* Uvicorn
* Pytest

### Frontend

* React 19
* Vite
* Axios
* Tailwind CSS
* Lucide React
* React Router
* Recharts

### Data Layer

The current prototype uses CSV-based data for:

* Products
* Inventory
* Merchants
* Offers
* Delivery options
* Merchant policies

### Development Tools

* Git
* GitHub
* Visual Studio Code
* PowerShell
* npm
* Pytest

---

## Project Structure

```text
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
```

---

## Installation

### Prerequisites

Make sure you have the following installed:

* Python 3.11+
* Node.js
* npm
* Git

### Clone the Repository

```bash
git clone https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery.git
cd ATRR-Agentic-Transaction-Recovery
```

### Create the Python Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If the virtual environment already exists:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install Backend Dependencies

```powershell
pip install -r requirements.txt
```

### Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

---

## Running the Application

### Start the Backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### Health Check

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "ATRR",
  "message": "ATRR backend is running"
}
```

### API Documentation

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Start the Frontend

Open a second terminal:

```powershell
cd frontend
npm run dev
```

Vite will provide a local URL, typically:

```text
http://localhost:5173
```

If the port is already in use, Vite will automatically select another available port.

---

## API

### Recovery Endpoint

```text
POST /api/v1/recover
```

### Request Body

```json
{
  "transaction_id": "TXN-DEMO-001",
  "category": "headphones",
  "max_budget": 5000,
  "min_rating": 4.0,
  "delivery_deadline_days": 2,
  "failed_product_id": "P003",
  "customer_approved": true
}
```

### Successful Response

```json
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
```

The complete response also contains recovery attempts and audit events.

---

## Customer Approval Flow

Customer approval acts as an explicit execution safeguard.

```text
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
```

This ensures the platform does not continue recovery execution without customer authorization.

---

## Replanning

ATRR supports adaptive recovery when an execution attempt fails.

The Decision Agent receives previous recovery attempts as part of the current recovery context.

Previously attempted actions are excluded from subsequent decisions.

```text
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
```

The replanning behavior is covered by:

```text
tests/test_recovery_orchestrator.py
```

Specifically:

```text
test_agent_replans_after_execution_failure
```

---

## Audit Trail

ATRR provides a structured audit trail for recovery decisions and actions.

### Typical Successful Recovery

```text
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
```

### Recovery with Replanning

```text
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
```

---

## Example Recovery Scenario

A sample recovery request can use:

| Field             | Value          |
| ----------------- | -------------- |
| Transaction ID    | `TXN-DEMO-001` |
| Category          | `headphones`   |
| Maximum budget    | ₹5,000         |
| Minimum rating    | 4.0            |
| Delivery deadline | 2 days         |
| Failed product    | `P003`         |
| Customer approval | Approved       |

Example recovery outcome:

| Result           | Value              |
| ---------------- | ------------------ |
| Selected product | `P001`             |
| Action           | Substitute product |
| Customer cost    | ₹4,499             |
| Merchant value   | ₹809.82            |
| Constraint check | Passed             |
| Final status     | `RECOVERED`        |

---

## Frontend

The React frontend provides a transaction recovery console where users can:

* Enter transaction details
* Set the maximum budget
* Set the minimum rating
* Set the delivery deadline
* Specify the failed product
* Provide customer approval
* Start a recovery request
* View recovery status
* View the selected recovery action
* View recovery activity
* View the audit trail

### UI Flow

```text
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
```

The interface is designed as a transaction operations console focused on recovery decisions, outcomes, and auditability.

---

## Testing

Run the complete backend test suite:

```powershell
python -m pytest
```

### Current Test Result

```text
59 passed
```

The test suite covers:

* Transaction intent
* Candidate selection
* Constraint validation
* Decision Agent
* Execution service
* Merchant data service
* Policy service
* Recovery action service
* Recovery service
* Recovery orchestration
* Replanning service
* Audit service

---

## Frontend Production Build

To verify the frontend production build:

```powershell
cd frontend
npm run build
```

The production frontend build has been successfully verified.

---

## Design Principles

### Safety

Recovery actions must satisfy customer and merchant constraints before execution.

### Customer Control

Customer approval remains an explicit execution gate.

### Adaptability

Failed recovery attempts can trigger another decision using the updated recovery context.

### Traceability

Recovery decisions, policy checks, execution outcomes, and recovery results are recorded in the audit trail.

---

## Current Implementation Status

| Component                            | Status      |
| ------------------------------------ | ----------- |
| Constraint-aware candidate selection | ✅           |
| Recovery plan generation             | ✅           |
| Recovery plan ranking                | ✅           |
| Decision Agent                       | ✅           |
| Policy verification                  | ✅           |
| Customer approval gate               | ✅           |
| Execution gate                       | ✅           |
| Recovery attempt tracking            | ✅           |
| Replanning after execution failure   | ✅           |
| Audit trail                          | ✅           |
| FastAPI recovery API                 | ✅           |
| React frontend                       | ✅           |
| Frontend-to-backend integration      | ✅           |
| Backend test suite                   | ✅ 59 passed |
| Frontend production build            | ✅           |

---

## Future Improvements

Possible future enhancements include:

* Persistent transaction storage
* Production database integration
* Real merchant API integration
* Real payment gateway integration
* Real-time transaction monitoring
* Authentication and role-based access
* Advanced recovery analytics
* Notification services
* Production-grade observability
* Distributed execution workers
* Additional recovery action types
* Enhanced recovery simulation and failure scenarios

---

## Screenshots

Add screenshots of the application here when preparing the final repository presentation.

Recommended screenshots:

1. **ATRR Transaction Recovery Dashboard**
2. **Successful Recovery Result**
3. **Recovery Status Pipeline**
4. **Recovery Audit Trail**
5. **Replanning Scenario**

Suggested directory:

```text
screenshots/
├── dashboard.png
├── recovery-success.png
├── audit-trail.png
└── replanning.png
```

Once screenshots are added, they can be embedded using standard Markdown image syntax:

```markdown
![ATRR Dashboard](screenshots/dashboard.png)
```

---

## Demo Flow

A basic demonstration can follow this sequence:

```text
1. Enter a failed transaction.
2. Define the customer's recovery constraints.
3. Provide customer approval.
4. Start the recovery process.
5. Review the selected recovery plan.
6. Verify the policy status.
7. Execute the selected recovery action.
8. View the final recovery result.
9. Review the audit trail.
```

For an adaptive recovery scenario:

```text
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
```

---

## Repository

**GitHub Repository:**

https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery

---

## Author

**Anvi Pardhi**

Information Technology Student

Interested in software engineering, full-stack development, AI systems, and building practical technology solutions.

---

## License

This project was developed as a hackathon prototype for exploring safe, adaptive, and traceable transaction recovery workflows.
