# ATRR — Agentic Transaction Recovery & Replanning

> **Track 03 — AI Revenue Recovery**

### A bounded agentic recovery system that detects revenue at risk, selects the highest-value recovery intervention, executes it safely, replans after failure, and escalates or stops when recovery boundaries are reached.

ATRR (**Agentic Transaction Recovery & Replanning**) is a transaction recovery platform designed to recover revenue from failed transactions through constraint-aware decisioning, merchant policy verification, customer approval, controlled execution, adaptive replanning, and measurable batch-level recovery.

Rather than relying on a fixed retry mechanism, ATRR treats recovery as a closed-loop process:

```text
Failed Transaction
        |
        v
Revenue Risk Detection
        |
        v
Transaction Intent
        |
        v
Candidate & Intervention Generation
        |
        v
Constraint Validation
        |
        v
Recovery Outcome Estimation
        |
        v
Recovery Value Scoring
        |
        v
Decision Agent
        |
        v
Merchant Policy Check
        |
        v
Customer Approval
        |
        v
Execution
      /   \
     /     \
 Success   Failure
   |          |
   v          v
Recover    Replanning
              |
              v
       New Recovery Decision
          /      |      \
         /       |       \
     Recover  Escalate   Stop
````

The system is designed around four core principles:

**Bounded Autonomy · Economic Decisioning · Adaptive Replanning · Traceability**

---

## 1. Problem

A failed transaction does not always mean lost revenue.

Depending on the situation, a transaction may still be recoverable through a different intervention such as:

* retrying a payment,
* substituting a product,
* changing delivery,
* applying an eligible incentive.

The challenge is deciding **which action should be attempted next**, while respecting customer requirements, merchant policies, economic constraints, and previous execution outcomes.

A simple retry mechanism cannot answer:

> **What is the safest and highest-value recovery action available right now?**

ATRR addresses this problem by continuously evaluating the current recovery state and selecting the best valid intervention.

---

## 2. Solution

ATRR converts failed-transaction recovery into an adaptive decision-and-execution workflow.

The platform:

1. Detects revenue at risk
2. Builds transaction intent
3. Discovers recovery candidates
4. Validates customer constraints
5. Generates recovery interventions
6. Estimates recovery outcomes
7. Calculates expected recovery value
8. Selects the best available recovery action
9. Verifies merchant policy
10. Enforces customer approval
11. Executes the selected action
12. Records the execution result
13. Replans when an execution attempt fails
14. Escalates after repeated failures
15. Stops when recovery should no longer continue
16. Measures recovery performance across a batch
17. Maintains a structured audit trail

---

## 3. Key Capabilities

### Revenue Risk Detection

ATRR explicitly quantifies the financial exposure associated with a failed transaction.

The Revenue Risk Service provides:

* Risk level
* Risk score
* Revenue at risk
* Recoverable revenue
* Recovery eligibility
* Risk explanation

Example:

```text
Risk Level:           MEDIUM
Risk Score:           0.60
Revenue at Risk:      ₹3,299
Recoverable Revenue:  ₹3,299
Recovery Eligible:    TRUE
```

This gives every recovery decision a measurable financial context.

---

### Constraint-Aware Recovery

Recovery decisions are based on the original transaction intent.

Current constraints include:

* Maximum customer budget
* Minimum product rating
* Delivery deadline
* Inventory availability
* Failed-product exclusion

Only constraint-safe options are eligible for recovery planning.

---

### Multi-Intervention Recovery

ATRR supports multiple recovery strategies rather than relying on a single retry path.

#### Product Substitution

Select an available alternative product that satisfies the customer's requirements.

#### Payment Retry

Retry a failed payment when merchant policy permits it and the configured retry limit has not been reached.

#### Delivery Change

Select an alternative delivery option when it satisfies the transaction's delivery requirement.

#### Offer / Incentive

Apply an eligible merchant incentive while respecting configured merchant limits.

---

## 4. Recovery Value Decisioning

Each candidate intervention is represented as a structured recovery plan.

Plans contain information such as:

* Action type
* Product or offer
* Customer cost
* Expected revenue
* Merchant value
* Success probability
* Constraint safety
* Expected recovery value

ATRR prioritizes interventions using **expected recovery value**.

Conceptually:

```text
Expected Recovery Outcome
            ×
     Success Probability
            -
      Recovery Cost
            =
   Expected Recovery Value
```

Example recovery options:

```text
Recovery Options

SUB-P001             ₹2,639.20
DELIVERY-EXPRESS     ₹2,309.30
RETRY-P003-1         ₹2,144.35
OFFER-OFF002         ₹2,124.25

          ↓

    Decision Agent

          ↓

       SUB-P001
```

This allows recovery decisions to consider both feasibility and economic impact.

---

## 5. Decision Agent

The Decision Agent evaluates the current recovery state and selects the highest-value available recovery plan that has not already been attempted.

The decision context includes:

* Transaction intent
* Available recovery plans
* Merchant policy
* Previous recovery attempts
* Current recovery state
* Simulation scenario

Previously attempted actions are excluded from subsequent decisions, allowing the system to choose a different recovery path after failure.

The decision loop is:

```text
Observe
   ↓
Evaluate
   ↓
Decide
   ↓
Act
   ↓
Observe Outcome
   ↓
Replan when necessary
```

The current Decision Agent is implemented as deterministic application logic rather than an LLM-based decision system.

---

## 6. Policy and Customer Safety Gates

ATRR separates recovery decisioning from execution.

A selected recovery action must pass the required safeguards before execution:

```text
Decision Agent
      |
      v
Selected Recovery Action
      |
      v
Merchant Policy Check
      |
      v
Customer Approval
      |
      v
Execution
```

### Merchant Policy Verification

The policy engine evaluates whether the selected action is permitted under the merchant's configured rules.

Typical checks include:

* Whether the action is allowed
* Payment retry limits
* Incentive limits
* Product substitution rules
* Delivery-change permissions
* Action-specific constraints

### Customer Approval

Customer authorization is an explicit execution gate.

Without approval, automated recovery execution does not continue.

This ensures the system does not silently perform customer-impacting recovery actions without authorization.

---

## 7. Adaptive Replanning

ATRR does not blindly repeat a failed recovery action.

When execution fails, the system records the attempt, updates the recovery context, excludes the failed action, generates remaining options, and asks the Decision Agent to select the next available action.

```text
Attempt 1
    |
    v
Execution Failure
    |
    v
Record Attempt
    |
    v
Update Recovery Context
    |
    v
Exclude Attempted Action
    |
    v
Generate Remaining Options
    |
    v
Re-score Recovery Plans
    |
    v
Decision Agent
    |
    v
Attempt 2
```

Example:

```text
Delivery Change
      |
      v
    FAILED
      |
      v
  REPLANNING
      |
      v
Payment Retry
      |
      v
   SUCCESS
      |
      v
  RECOVERED
```

This adaptive behavior is the core agentic capability of ATRR.

---

## 8. Bounded Autonomy

An automated recovery system should not continue indefinitely.

ATRR implements explicit boundaries for repeated failure and recovery termination.

### Escalation

When automated recovery reaches the configured failure boundary:

```text
Repeated Recovery Failure
        |
        v
     Guardrail
        |
        v
    ESCALATED
```

### Stop

When the recovery process should not proceed:

```text
Recovery Decision
       |
       v
      STOP
       |
       v
No Execution
       |
       v
RECOVERY_STOPPED
```

These controls create a bounded recovery workflow rather than an uncontrolled autonomous loop.

---

## 9. Batch Recovery

ATRR supports recovery across multiple transactions and measures the resulting financial impact.

The batch engine calculates:

* Transactions evaluated
* Recovery eligible
* Transactions recovered
* Transactions failed
* Transactions blocked
* Multi-attempt transactions
* Transactions escalated
* Transactions stopped
* Revenue at risk
* Revenue recovered
* Transaction recovery rate
* Revenue recovery rate

This directly supports the Track 03 requirement to demonstrate **measured money recovered across a batch**.

---

## 10. Verified Batch Demonstration

ATRR includes deterministic simulation scenarios so that recovery behavior can be reproduced consistently during demonstrations.

The verified demonstration batch contained:

```text
FINAL-NORMAL-001
FINAL-REPLAN-001
FINAL-REPLAN-002
FINAL-ESCALATE-001
FINAL-STOP-001
```

### Batch Results

| Metric                     |  Result |
| -------------------------- | ------: |
| Transactions evaluated     |       5 |
| Recovery eligible          |       5 |
| Transactions recovered     |       3 |
| Transactions failed        |       0 |
| Transactions blocked       |       0 |
| Multi-attempt transactions |       3 |
| Transactions escalated     |       1 |
| Transactions stopped       |       1 |
| Revenue at risk            | ₹15,295 |
| Revenue recovered          |  ₹8,697 |
| Transaction recovery rate  |   60.0% |
| Revenue recovery rate      |  56.86% |

### Scenario Behavior

#### NORMAL

```text
NORMAL
   |
   v
RECOVERED
```

#### REPLAN

```text
REPLAN
   |
   v
First Action Fails
   |
   v
Replanning
   |
   v
New Action Selected
   |
   v
RECOVERED
```

#### ESCALATE

```text
ESCALATE
   |
   v
Repeated Failures
   |
   v
Guardrail
   |
   v
ESCALATED
```

#### STOP

```text
STOP
   |
   v
Execution Prevented
   |
   v
RECOVERY_STOPPED
```

> **Metric note:** the backend metric `transactions_replanned` is displayed as **Multi-attempt** in the frontend because it counts transactions that required more than one automated attempt.

---

## 11. Auditability

ATRR records the major events produced throughout the recovery lifecycle.

A typical successful recovery produces:

```text
REVENUE_RISK_DETECTED
        ↓
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

A transaction involving replanning produces:

```text
EXECUTION
    ↓
REPLANNING_TRIGGERED
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

Audit information includes:

* Revenue risk detection
* Recovery plans
* Agent decisions
* Proposed actions
* Policy decisions
* Execution outcomes
* Failed attempts
* Replanning events
* Recovery completion
* Escalation events
* Stop events

This provides traceability across the recovery lifecycle.

---

# 12. System Architecture

```text
                           +----------------------------+
                           |       React Frontend       |
                           |                            |
                           |   Single Recovery          |
                           |   Batch Intelligence       |
                           +-------------+--------------+
                                         |
                                         | HTTP / JSON
                                         v
                           +----------------------------+
                           |         FastAPI API        |
                           |                            |
                           |  /api/v1/recover           |
                           |  /api/v1/recover/batch     |
                           +-------------+--------------+
                                         |
                                         v
                           +----------------------------+
                           |    Recovery Orchestrator    |
                           +-------------+--------------+
                                         |
          +------------------------------+------------------------------+
          |                |             |             |                |
          v                v             v             v                v
   Revenue Risk       Candidate      Decision       Policy          Execution
     Service         Services        Agent          Service          Service
                           |
                           v
                    Replanning Service
                           |
                           v
                      Audit Service
```

---

# 13. Recovery Pipeline

```text
Failed Transaction
        |
        v
Revenue Risk Detection
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
Recovery Intervention Generation
        |
        v
Outcome Estimation
        |
        v
Recovery Value Scoring
        |
        v
Decision Agent
        |
        v
Merchant Policy Verification
        |
        v
Customer Approval
        |
        v
Execution
        |
        +----------------------+
        |                      |
        v                      v
     SUCCESS                FAILURE
        |                      |
        v                      v
   RECOVERED               REPLANNING
                               |
                               v
                        New Decision
                               |
                    +----------+----------+
                    |          |          |
                    v          v          v
                 Recover   Escalate     Stop
```

---

# 14. Frontend

ATRR provides a React-based transaction operations dashboard.

## Single Recovery

The Single Recovery interface provides:

* Transaction details
* Customer constraints
* Customer approval
* Recovery execution
* Revenue risk
* Selected intervention
* Expected recovery value
* Success probability
* Recovery attempts
* Recovery journey
* Audit trail

### UI Flow

```text
Recovery Request
       |
       v
Process Status
       |
       v
Agent Decision
       |
       v
Recovery Journey
       |
       v
Audit Trail
```

---

## Batch Intelligence

The Batch Intelligence dashboard provides a financial and operational view of multiple recovery cases.

### Recovery KPIs

```text
Revenue at Risk
Revenue Recovered
Recovery Rate
Revenue Recovery
Multi-attempt
Escalated
Stopped
```

### Revenue Recovery

```text
Revenue at Risk
        ↓
Revenue Recovered
        ↓
Remaining Risk
```

### Transaction Queue

Each transaction displays:

```text
Transaction ID
Risk Level
Revenue at Risk
Recovery Decision
Attempt Count
Final Outcome
```

---

# 15. Technology Stack

## Backend

* Python 3.11
* FastAPI
* Pydantic
* Uvicorn
* Pandas
* NumPy
* Pytest

## Frontend

* React 19
* Vite
* Axios
* Lucide React
* Recharts

## Data Layer

The current prototype uses CSV-based data for:

* Products
* Merchants
* Inventory
* Offers
* Policies
* Delivery options

## Development

* Git
* GitHub
* Visual Studio Code
* PowerShell
* npm

---

# 16. Project Structure

```text
ATRR-Agentic-Transaction-Recovery/
│
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── agent_context.py
│       │   └── decision_agent.py
│       │
│       ├── api/
│       │   └── recovery.py
│       │
│       ├── models/
│       │   ├── agent_decision.py
│       │   ├── audit_event.py
│       │   ├── batch_recovery.py
│       │   ├── candidate.py
│       │   ├── constraint_result.py
│       │   ├── execution_request.py
│       │   ├── execution_result.py
│       │   ├── merchant_policy.py
│       │   ├── policy_decision.py
│       │   ├── recovery_action.py
│       │   ├── recovery_attempt.py
│       │   ├── recovery_intervention.py
│       │   ├── recovery_outcome.py
│       │   ├── recovery_plan.py
│       │   ├── recovery_request.py
│       │   ├── revenue_risk.py
│       │   └── transaction_intent.py
│       │
│       ├── services/
│       │   ├── audit_service.py
│       │   ├── batch_recovery_service.py
│       │   ├── candidate_service.py
│       │   ├── constraint_service.py
│       │   ├── execution_service.py
│       │   ├── merchant_data_service.py
│       │   ├── policy_service.py
│       │   ├── recovery_action_service.py
│       │   ├── recovery_orchestrator.py
│       │   ├── recovery_outcome_service.py
│       │   ├── recovery_service.py
│       │   ├── recovery_value_service.py
│       │   ├── replanning_service.py
│       │   └── revenue_risk_service.py
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
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── test_audit_service.py
│   ├── test_batch_recovery_service.py
│   ├── test_candidate_service.py
│   ├── test_constraint_service.py
│   ├── test_decision_agent.py
│   ├── test_execution_service.py
│   ├── test_merchant_data_service.py
│   ├── test_policy_service.py
│   ├── test_recovery_action_service.py
│   ├── test_recovery_orchestrator.py
│   ├── test_recovery_outcome_service.py
│   ├── test_recovery_service.py
│   ├── test_replanning_service.py
│   ├── test_revenue_risk_service.py
│   └── test_transaction_intent.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 17. Installation

## Prerequisites

* Python 3.11+
* Node.js
* npm
* Git

## Clone Repository

```bash
git clone https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery.git
cd ATRR-Agentic-Transaction-Recovery
```

## Backend Setup

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

## Frontend Setup

```powershell
cd frontend
npm install
cd ..
```

---

# 18. Running ATRR

## Start Backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

## Health Check

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

## API Documentation

FastAPI Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Start Frontend

Open a second terminal:

```powershell
cd frontend
npm run dev
```

Vite will provide a local frontend URL, for example:

```text
http://localhost:5173
```

If the port is occupied, Vite automatically selects another available port.

---

# 19. API

## Single Transaction Recovery

```text
POST /api/v1/recover
```

Example request:

```json
{
  "transaction_id": "TXN-DEMO-001",
  "failed_product_id": "P003",
  "category": "headphones",
  "max_budget": 5000,
  "min_rating": 4.0,
  "delivery_deadline_days": 2,
  "customer_approved": true,
  "simulation_scenario": "NORMAL"
}
```

The response contains:

* Transaction status
* Revenue risk
* Selected recovery action
* Recovery attempts
* Audit events
* Recovery outcome

---

## Batch Recovery

```text
POST /api/v1/recover/batch
```

Example request:

```json
{
  "simulation_mode": true,
  "transactions": [
    {
      "transaction_id": "FINAL-NORMAL-001",
      "failed_product_id": "P003",
      "category": "headphones",
      "max_budget": 5000,
      "min_rating": 4.0,
      "delivery_deadline_days": 2,
      "customer_approved": true,
      "simulation_scenario": "NORMAL"
    }
  ]
}
```

Supported deterministic simulation scenarios:

```text
NORMAL
REPLAN
ESCALATE
STOP
```

---

# 20. Testing

Run the complete backend test suite:

```powershell
python -m pytest -q
```

Verified result:

```text
83 passed
```

The automated tests cover:

* Transaction intent validation
* Candidate discovery
* Constraint validation
* Decision Agent behavior
* Merchant data services
* Merchant policy verification
* Recovery actions
* Recovery service
* Recovery orchestration
* Replanning
* Execution
* Recovery outcome estimation
* Recovery value scoring
* Revenue risk detection
* Batch recovery
* Audit behavior

---

# 21. Frontend Build Verification

From the frontend directory:

```powershell
cd frontend
npm run build
```

The production frontend build has been successfully verified.

---

# 22. Design Principles

### Safety

Recovery actions must satisfy applicable customer and merchant constraints before execution.

### Customer Control

Customer approval remains an explicit execution gate.

### Adaptability

Failed recovery attempts can trigger a new decision using the updated recovery context.

### Bounded Autonomy

ATRR can escalate or stop rather than continuing recovery indefinitely.

### Economic Decisioning

Recovery interventions are prioritized using expected recovery value.

### Traceability

Recovery decisions, policy checks, execution outcomes, and recovery results are recorded through the audit trail.

---

# 23. Current Implementation Status

| Component                            |    Status   |
| ------------------------------------ | :---------: |
| Revenue risk detection               |      ✅      |
| Constraint-aware candidate selection |      ✅      |
| Recovery intervention generation     |      ✅      |
| Recovery outcome estimation          |      ✅      |
| Recovery value scoring               |      ✅      |
| Decision Agent                       |      ✅      |
| Merchant policy verification         |      ✅      |
| Customer approval gate               |      ✅      |
| Execution gate                       |      ✅      |
| Recovery attempt tracking            |      ✅      |
| Adaptive replanning                  |      ✅      |
| Escalation guardrail                 |      ✅      |
| Stop behavior                        |      ✅      |
| Batch recovery                       |      ✅      |
| Revenue recovery metrics             |      ✅      |
| Audit trail                          |      ✅      |
| FastAPI recovery API                 |      ✅      |
| React frontend                       |      ✅      |
| Single Recovery dashboard            |      ✅      |
| Batch Intelligence dashboard         |      ✅      |
| Frontend-backend integration         |      ✅      |
| Backend test suite                   | ✅ 83 passed |
| Frontend production build            |      ✅      |

---

# 24. Demo Scenarios

## Normal Recovery

```text
Failed Transaction
      |
      v
Revenue Risk
      |
      v
Recovery Plans
      |
      v
Decision Agent
      |
      v
Policy + Approval
      |
      v
Execution
      |
      v
RECOVERED
```

## Replanning

```text
Recovery Action
      |
      v
Execution Failure
      |
      v
Record Attempt
      |
      v
Replanning
      |
      v
New Decision
      |
      v
Next Safe Action
      |
      v
RECOVERED
```

## Escalation

```text
Recovery Attempt
      |
      v
FAILURE
      |
      v
Replanning
      |
      v
FAILURE
      |
      v
Guardrail
      |
      v
ESCALATED
```

## Stop

```text
Recovery Decision
      |
      v
STOP
      |
      v
Execution Prevented
      |
      v
RECOVERY_STOPPED
```

---

# 25. Project Outcomes

ATRR demonstrates the transition from simple transaction retries to adaptive, measurable revenue recovery.

The overall operating model is:

```text
Detect
  ↓
Decide
  ↓
Execute
  ↓
Observe
  ↓
Replan
  ↓
Recover / Escalate / Stop
  ↓
Measure
  ↓
Audit
```

The verified demonstration batch produced:

```text
₹15,295
Revenue at Risk

₹8,697
Revenue Recovered

60.0%
Transaction Recovery Rate

56.86%
Revenue Recovery Rate
```

These results demonstrate that ATRR measures recovery at both the **transaction level** and the **financial level**.

---

# 26. Limitations

The current implementation is a hackathon prototype.

It currently uses:

* CSV-based data
* Deterministic simulation scenarios
* Local FastAPI execution
* Local React frontend
* In-memory recovery execution state

It does not currently integrate with live payment gateways or production merchant systems.

The Decision Agent is implemented using deterministic application logic rather than a production LLM-based agent.

---

# 27. Future Improvements

Potential extensions include:

* Persistent transaction storage
* Production database integration
* Real payment gateway integration
* Real merchant API integration
* Real-time transaction monitoring
* Authentication and role-based access control
* Notification services
* Production observability
* Distributed execution workers
* Additional recovery interventions
* Advanced recovery analytics
* LLM-assisted decision explanations
* Production-grade simulation environments

---

# 28. Repository

**GitHub Repository**

[https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery](https://github.com/Anvi-2006/ATRR-Agentic-Transaction-Recovery)

---

# 29. Author

**Anvi Pardhi**

Information Technology Student

Focused on software engineering, AI systems, full-stack development, and practical technology solutions.

---

# License

This project was developed as a hackathon prototype for exploring safe, adaptive, measurable, and traceable transaction recovery workflows.


