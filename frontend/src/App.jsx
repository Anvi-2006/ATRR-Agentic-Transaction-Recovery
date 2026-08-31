import { useState } from "react";
import axios from "axios";
import {
  ShieldCheck,
  CheckCircle2,
  Clock3,
  CircleAlert,
  ArrowRight,
  RotateCcw,
  Zap,
  LockKeyhole,
  PackageCheck,
  FileCheck2,
  RefreshCw,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [form, setForm] = useState({
    transaction_id: "TXN-DEMO-001",
    category: "headphones",
    max_budget: 5000,
    min_rating: 4.0,
    delivery_deadline_days: 2,
    failed_product_id: "P003",
    customer_approved: true,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateField = (field, value) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const recoverTransaction = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/recover`,
        {
          ...form,
          max_budget: Number(form.max_budget),
          min_rating: Number(form.min_rating),
          delivery_deadline_days: Number(form.delivery_deadline_days),
        }
      );

      setResult(response.data);
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(JSON.stringify(err.response.data.detail));
      } else {
        setError(
          "Unable to connect to the recovery service. Make sure the FastAPI backend is running."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const resetRecovery = () => {
    setResult(null);
    setError("");
  };

  const isRecovered = result?.status === "RECOVERED";
  const selectedAction = result?.selected_action;
  const auditEvents = Array.from(new Map((result?.audit_events || []).map((event) => [event.event_id, event])).values());

  const getStepState = (step) => {
    if (!result) return "waiting";

    if (step <= 3) return "completed";

    if (step === 4) {
      return form.customer_approved ? "completed" : "blocked";
    }

    if (step === 5) {
      return isRecovered ? "completed" : "blocked";
    }

    return "waiting";
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={18} strokeWidth={2.2} />
          </div>

          <div>
            <div className="brand-name">ATRR</div>
            <div className="brand-subtitle">
              Transaction Recovery Platform
            </div>
          </div>
        </div>

        <div className="system-state">
          <span className="online-dot" />
          Operational
        </div>
      </header>

      <main className="main-content">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">TRANSACTION RECOVERY</div>

            <h1>
              Recover failed transactions.
              <br />
              <span>Safely and automatically.</span>
            </h1>

            <p>
              Evaluate available recovery options, verify merchant
              constraints, obtain customer approval, and execute the
              selected recovery action.
            </p>
          </div>

          <div className="hero-status">
            <div className="hero-status-icon">
              <Zap size={16} />
            </div>

            <div>
              <strong>Recovery engine</strong>
              <span>Ready to process</span>
            </div>
          </div>
        </section>

        <section className="workspace">
          <div className="card request-card">
            <div className="card-header">
              <div>
                <div className="section-label">01 / RECOVERY REQUEST</div>
                <h2>Transaction details</h2>
              </div>

              <span className="live-badge">LIVE</span>
            </div>

            <div className="card-body">
              <div className="form-grid">
                <Field
                  label="Transaction ID"
                  value={form.transaction_id}
                  onChange={(value) =>
                    updateField("transaction_id", value)
                  }
                />

                <Field
                  label="Category"
                  value={form.category}
                  onChange={(value) =>
                    updateField("category", value)
                  }
                />

                <Field
                  label="Maximum budget"
                  value={form.max_budget}
                  type="number"
                  prefix="₹"
                  onChange={(value) =>
                    updateField("max_budget", value)
                  }
                />

                <Field
                  label="Minimum rating"
                  value={form.min_rating}
                  type="number"
                  step="0.1"
                  onChange={(value) =>
                    updateField("min_rating", value)
                  }
                />

                <Field
                  label="Delivery deadline"
                  value={form.delivery_deadline_days}
                  type="number"
                  suffix="days"
                  onChange={(value) =>
                    updateField(
                      "delivery_deadline_days",
                      value
                    )
                  }
                />

                <Field
                  label="Failed product"
                  value={form.failed_product_id}
                  onChange={(value) =>
                    updateField(
                      "failed_product_id",
                      value
                    )
                  }
                />
              </div>

              <div className="approval-row">
                <div className="approval-info">
                  <div className="approval-icon">
                    <LockKeyhole size={15} />
                  </div>

                  <div>
                    <strong>Customer approval</strong>
                    <span>
                      Required before recovery execution
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  className={`approval-toggle ${
                    form.customer_approved ? "approved" : ""
                  }`}
                  onClick={() =>
                    updateField(
                      "customer_approved",
                      !form.customer_approved
                    )
                  }
                >
                  <CheckCircle2 size={14} />

                  {form.customer_approved
                    ? "Approved"
                    : "Required"}
                </button>
              </div>

              <button
                type="button"
                className="primary-button"
                onClick={recoverTransaction}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <RotateCcw
                      className="spin"
                      size={16}
                    />
                    Processing recovery...
                  </>
                ) : (
                  <>
                    <Zap size={16} />
                    Recover transaction
                    <ArrowRight size={16} />
                  </>
                )}
              </button>

              {error && (
                <div className="error-box">
                  <CircleAlert size={16} />
                  <span>{error}</span>
                </div>
              )}
            </div>
          </div>

          <div className="card status-card">
            <div className="card-header">
              <div>
                <div className="section-label">
                  02 / RECOVERY STATUS
                </div>
                <h2>Process status</h2>
              </div>

              <span className="status-badge">
                {result ? result.status : "READY"}
              </span>
            </div>

            <div className="status-body">
              <StatusStep
                number="01"
                title="Request received"
                state={getStepState(1)}
              />

              <StatusStep
                number="02"
                title="Recovery options evaluated"
                state={getStepState(2)}
              />

              <StatusStep
                number="03"
                title="Policy verified"
                state={getStepState(3)}
              />

              <StatusStep
                number="04"
                title="Customer approval"
                state={getStepState(4)}
              />

              <StatusStep
                number="05"
                title="Execution"
                state={getStepState(5)}
                last
              />

              {result && (
                <div
                  className={`result-mini ${
                    isRecovered ? "success" : "warning"
                  }`}
                >
                  {isRecovered ? (
                    <CheckCircle2 size={19} />
                  ) : (
                    <CircleAlert size={19} />
                  )}

                  <div>
                    <span>Recovery result</span>
                    <strong>{result.status}</strong>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {result && selectedAction && (
          <section className="card recommendation-card">
            <div className="card-header">
              <div>
                <div className="section-label">
                  03 / RECOVERY RESULT
                </div>
                <h2>Selected recovery</h2>
              </div>

              <span className="recommended-badge">
                <CheckCircle2 size={13} />
                Selected
              </span>
            </div>

            <div className="recommendation-content">
              <div className="product-icon">
                <PackageCheck size={24} />
              </div>

              <div className="product-main">
                <span className="product-action">
                  {selectedAction.action_type.replaceAll(
                    "_",
                    " "
                  )}
                </span>

                <h3>{selectedAction.product_id}</h3>

                <p>{selectedAction.reason}</p>
              </div>

              <div className="product-metrics">
                <Metric
                  label="Customer cost"
                  value={`₹${Number(
                    selectedAction.customer_cost
                  ).toLocaleString("en-IN")}`}
                />

                <Metric
                  label="Merchant value"
                  value={`₹${Number(
                    selectedAction.merchant_value
                  ).toFixed(2)}`}
                />

                <Metric
                  label="Constraint check"
                  value={
                    selectedAction.constraint_safe
                      ? "Passed"
                      : "Failed"
                  }
                />
              </div>
            </div>
          </section>
        )}

        {result && (
          <section className="card audit-card">
            <div className="card-header">
              <div>
                <div className="section-label">
                  04 / AUDIT TRAIL
                </div>
                <h2>Recovery activity</h2>
              </div>

              <button
                type="button"
                className="text-button"
                onClick={resetRecovery}
              >
                <RefreshCw size={12} />
                New recovery
              </button>
            </div>

            <div className="audit-list">
              {auditEvents.map((event) => (
                <div
                  className="audit-row"
                  key={event.event_id}
                >
                  <div className="audit-icon">
                    <FileCheck2 size={14} />
                  </div>

                  <div className="audit-event">
                    <strong>
                      {event.event_type.replaceAll(
                        "_",
                        " "
                      )}
                    </strong>

                    <span>{event.reason}</span>
                  </div>

                  <div className="audit-status">
                    {event.status}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {!result && (
          <section className="card empty-card">
            <Clock3 size={21} />

            <div>
              <h3>Ready for recovery</h3>

              <p>
                Submit a transaction to evaluate recovery
                options, verify constraints, and create a
                complete recovery record.
              </p>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>ATRR / Transaction Recovery</span>
        <span>Secure recovery pipeline</span>
      </footer>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  prefix,
  suffix,
  step,
}) {
  return (
    <label className="field">
      <span>{label}</span>

      <div className="input-wrap">
        {prefix && <small>{prefix}</small>}

        <input
          type={type}
          value={value}
          step={step}
          onChange={(event) =>
            onChange(event.target.value)
          }
        />

        {suffix && <small>{suffix}</small>}
      </div>
    </label>
  );
}

function StatusStep({ number, title, state, last }) {
  const completed = state === "completed";
  const blocked = state === "blocked";

  return (
    <div className="status-step">
      <div
        className={`step-number ${
          completed ? "completed" : ""
        } ${blocked ? "blocked" : ""}`}
      >
        {completed ? (
          <CheckCircle2 size={13} />
        ) : blocked ? (
          <CircleAlert size={13} />
        ) : (
          number
        )}
      </div>

      <div className="step-content">
        <strong>{title}</strong>

        <span>
          {completed
            ? "Completed"
            : blocked
            ? "Blocked"
            : "Waiting"}
        </span>
      </div>

      {!last && <div className="step-line" />}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default App;


