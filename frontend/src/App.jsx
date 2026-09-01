import { useMemo, useState } from "react";
import axios from "axios";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleStop,
  Clock3,
  FileCheck2,
  Gauge,
  Layers3,
  LockKeyhole,
  PackageCheck,
  Play,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  StopCircle,
  TrendingUp,
  TriangleAlert,
  Users,
  Zap,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const DEFAULT_FORM = {
  transaction_id: "TXN-DEMO-001",
  category: "headphones",
  max_budget: 5000,
  min_rating: 4.0,
  delivery_deadline_days: 2,
  failed_product_id: "P003",
  customer_approved: true,
};

const DEMO_BATCH = [
  {
    transaction_id: "FINAL-NORMAL-001",
    failed_product_id: "P003",
    category: "headphones",
    max_budget: 5000,
    min_rating: 4.0,
    delivery_deadline_days: 2,
    customer_approved: true,
    simulation_scenario: "NORMAL",
  },
  {
    transaction_id: "FINAL-REPLAN-001",
    failed_product_id: "P001",
    category: "headphones",
    max_budget: 5000,
    min_rating: 4.0,
    delivery_deadline_days: 2,
    customer_approved: true,
    simulation_scenario: "REPLAN",
  },
  {
    transaction_id: "FINAL-REPLAN-002",
    failed_product_id: "P006",
    category: "chargers",
    max_budget: 2000,
    min_rating: 4.0,
    delivery_deadline_days: 2,
    customer_approved: true,
    simulation_scenario: "REPLAN",
  },
  {
    transaction_id: "FINAL-ESCALATE-001",
    failed_product_id: "P003",
    category: "headphones",
    max_budget: 5000,
    min_rating: 4.0,
    delivery_deadline_days: 2,
    customer_approved: true,
    simulation_scenario: "ESCALATE",
  },
  {
    transaction_id: "FINAL-STOP-001",
    failed_product_id: "P003",
    category: "headphones",
    max_budget: 5000,
    min_rating: 4.0,
    delivery_deadline_days: 2,
    customer_approved: true,
    simulation_scenario: "STOP",
  },
];

function App() {
  const [mode, setMode] = useState("single");

  return (
    <div className="app-shell">
      <Header mode={mode} setMode={setMode} />

      <main className="main-content">
        {mode === "single" ? <SingleRecovery /> : <BatchDashboard />}
      </main>

      <footer className="footer">
        <span>ATRR / Agentic Transaction Recovery</span>
        <span>Bounded autonomous recovery pipeline</span>
      </footer>
    </div>
  );
}

function Header({ mode, setMode }) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">
          <ShieldCheck size={19} strokeWidth={2.2} />
        </div>

        <div>
          <div className="brand-name">ATRR</div>
          <div className="brand-subtitle">
            Agentic Transaction Recovery
          </div>
        </div>
      </div>

      <div className="header-center">
        <div className="system-state">
          <span className="online-dot" />
          Operational
        </div>
      </div>

      <div className="mode-switcher">
        <button
          type="button"
          className={mode === "single" ? "active" : ""}
          onClick={() => setMode("single")}
        >
          <Zap size={14} />
          Single Recovery
        </button>

        <button
          type="button"
          className={mode === "batch" ? "active" : ""}
          onClick={() => setMode("batch")}
        >
          <Layers3 size={14} />
          Batch Intelligence
        </button>
      </div>
    </header>
  );
}

function SingleRecovery() {
  const [form, setForm] = useState(DEFAULT_FORM);
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
          delivery_deadline_days: Number(
            form.delivery_deadline_days
          ),
        }
      );

      setResult(response.data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to connect to the recovery service."
      );
    } finally {
      setLoading(false);
    }
  };

  const resetRecovery = () => {
    setResult(null);
    setError("");
  };

  const selectedAction = result?.selected_action;

  const auditEvents = Array.from(
    new Map(
      (result?.audit_events || []).map((event) => [
        event.event_id,
        event,
      ])
    ).values()
  );

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">SINGLE TRANSACTION</div>

          <h1>
            Recover failed transactions.
            <br />
            <span>Safely and intelligently.</span>
          </h1>

          <p>
            ATRR evaluates multiple recovery interventions,
            scores expected recovery value, validates policy,
            and adapts when an action fails.
          </p>
        </div>

        <div className="hero-status-card">
          <div className="hero-status-icon">
            <Sparkles size={17} />
          </div>

          <div>
            <span>Decision engine</span>
            <strong>Ready</strong>
          </div>
        </div>
      </section>

      <section className="single-grid">
        <div className="card request-card">
          <CardHeader
            label="01 / RECOVERY REQUEST"
            title="Transaction details"
            badge="LIVE"
          />

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
                  form.customer_approved
                    ? "approved"
                    : ""
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
                  Processing...
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
                <TriangleAlert size={16} />
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>

        <SingleStatus
          result={result}
          customerApproved={form.customer_approved}
        />
      </section>

      {result && (
        <>
          <SingleDecision result={result} />

          <section className="card audit-card">
            <CardHeader
              label="04 / AUDIT TRAIL"
              title="Recovery activity"
              action={
                <button
                  type="button"
                  className="text-button"
                  onClick={resetRecovery}
                >
                  <RefreshCw size={12} />
                  New recovery
                </button>
              }
            />

            <div className="audit-list">
              {auditEvents.map((event) => (
                <AuditRow
                  event={event}
                  key={event.event_id}
                />
              ))}
            </div>
          </section>
        </>
      )}

      {!result && (
        <section className="card empty-card">
          <div className="empty-icon">
            <Activity size={20} />
          </div>

          <div>
            <h3>Recovery engine ready</h3>
            <p>
              Submit a failed transaction to see risk,
              intervention ranking, policy validation,
              execution, and the final recovery trail.
            </p>
          </div>
        </section>
      )}
    </>
  );
}

function SingleStatus({ result, customerApproved }) {
  const isRecovered =
    result?.status === "RECOVERED";

  const isEscalated =
    result?.status === "ESCALATED";

  const isStopped =
    result?.status === "RECOVERY_STOPPED";

  const isBlocked =
    result?.status === "CUSTOMER_APPROVAL_REQUIRED";

  const attempts = result?.attempts || [];

  const steps = [
    "Request received",
    "Revenue risk detected",
    "Recovery options evaluated",
    "Policy verified",
    "Execution",
  ];

  return (
    <div className="card status-card">
      <CardHeader
        label="02 / RECOVERY STATUS"
        title="Process status"
        badge={result?.status || "READY"}
      />

      <div className="status-body">
        {steps.map((title, index) => {
          const number = index + 1;

          let state = result
            ? "completed"
            : "waiting";

          if (
            number === 5 &&
            result &&
            !isRecovered
          ) {
            state = "blocked";
          }

          return (
            <StatusStep
              key={title}
              number={String(number).padStart(2, "0")}
              title={title}
              state={state}
              last={number === steps.length}
            />
          );
        })}

        {result && (
          <div
            className={`result-mini ${
              isRecovered
                ? "success"
                : isEscalated
                ? "escalated"
                : isStopped
                ? "stopped"
                : isBlocked
                ? "blocked"
                : "warning"
            }`}
          >
            {isRecovered ? (
              <CheckCircle2 size={18} />
            ) : isEscalated ? (
              <AlertTriangle size={18} />
            ) : isStopped ? (
              <CircleStop size={18} />
            ) : (
              <TriangleAlert size={18} />
            )}

            <div>
              <span>
                {attempts.length > 1
                  ? `${attempts.length} recovery attempts`
                  : customerApproved
                  ? "Recovery result"
                  : "Approval required"}
              </span>

              <strong>{result.status}</strong>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SingleDecision({ result }) {
  const action = result.selected_action;
  const risk = result.revenue_risk;

  const attempts = result.attempts || [];

  return (
    <section className="card decision-card">
      <CardHeader
        label="03 / AGENT DECISION"
        title="Recovery intelligence"
        badge={
          result.status === "RECOVERED"
            ? "RECOVERED"
            : result.status
        }
      />

      <div className="decision-summary">
        <div className="decision-risk">
          <div className="risk-label">
            Revenue at risk
          </div>

          <strong>
            INR{" "}
            {Number(
              risk?.revenue_at_risk || 0
            ).toLocaleString("en-IN")}
          </strong>

          <span>
            {risk?.risk_level || "UNKNOWN"} risk · score{" "}
            {risk?.risk_score ?? "-"}
          </span>
        </div>

        {action ? (
          <div className="selected-panel">
            <div className="selected-icon">
              <PackageCheck size={21} />
            </div>

            <div className="selected-main">
              <span>Selected intervention</span>

              <h3>
                {action.action_type.replaceAll(
                  "_",
                  " "
                )}
              </h3>

              <p>
                {action.reason}
              </p>
            </div>

            <div className="selected-metrics">
              <Metric
                label="Expected recovery"
                value={`INR ${Number(
                  action.expected_recovery_value || 0
                ).toLocaleString("en-IN", {
                  maximumFractionDigits: 2,
                })}`}
              />

              <Metric
                label="Success probability"
                value={`${Math.round(
                  (action.success_probability || 0) *
                    100
                )}%`}
              />

              <Metric
                label="Attempts"
                value={attempts.length}
              />
            </div>
          </div>
        ) : (
          <div className="no-action-panel">
            <div className="no-action-icon">
              {result.status === "ESCALATED" ? (
                <AlertTriangle size={20} />
              ) : (
                <StopCircle size={20} />
              )}
            </div>

            <div>
              <span>Automated recovery outcome</span>
              <h3>{result.status}</h3>
              <p>
                No automated action was completed for
                this transaction.
              </p>
            </div>
          </div>
        )}
      </div>

      {attempts.length > 0 && (
        <div className="journey">
          <div className="journey-title">
            <span>Recovery journey</span>
            {attempts.length > 1 && (
              <span className="replan-pill">
                Adaptive replanning
              </span>
            )}
          </div>

          <div className="journey-track">
            {attempts.map((attempt, index) => (
              <div
                className="journey-node"
                key={attempt.attempt_id}
              >
                <div
                  className={`journey-dot ${
                    attempt.status === "SUCCESS"
                      ? "success"
                      : attempt.status ===
                        "BLOCKED"
                      ? "blocked"
                      : "failed"
                  }`}
                >
                  {attempt.status ===
                  "SUCCESS" ? (
                    <CheckCircle2 size={13} />
                  ) : (
                    <AlertTriangle size={13} />
                  )}
                </div>

                <div className="journey-copy">
                  <strong>
                    {attempt.action_id}
                  </strong>
                  <span>
                    Attempt {attempt.attempt_number} ·{" "}
                    {attempt.status}
                  </span>
                </div>

                {index <
                  attempts.length - 1 && (
                  <ArrowRight
                    size={15}
                    className="journey-arrow"
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function BatchDashboard() {
  const [loading, setLoading] = useState(false);
  const [batchResult, setBatchResult] =
    useState(null);
  const [error, setError] = useState("");

  const runDemoBatch = async () => {
    setLoading(true);
    setError("");
    setBatchResult(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/recover/batch`,
        {
          simulation_mode: true,
          transactions: DEMO_BATCH,
        }
      );

      setBatchResult(response.data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to connect to the batch recovery service."
      );
    } finally {
      setLoading(false);
    }
  };

  const metrics = batchResult?.metrics;

  const chartData = useMemo(() => {
  if (!metrics) return [];

  const total = Number(
    metrics.revenue_at_risk || 0
  );

  const recovered = Number(
    metrics.revenue_recovered || 0
  );

  const unrecovered = Math.max(
    total - recovered,
    0
  );

  return [
    {
      name: "At Risk",
      amount: total,
    },
    {
      name: "Recovered",
      amount: recovered,
    },
    {
      name: "Remaining Risk",
      amount: unrecovered,
    },
  ];
}, [metrics]);

  return (
    <>
      <section className="hero batch-hero">
        <div className="hero-copy">
          <div className="eyebrow">
            BATCH INTELLIGENCE
          </div>

          <h1>
            Measure recovered revenue.
            <br />
            <span>See how ATRR adapts.</span>
          </h1>

          <p>
            Run a deterministic recovery batch that
            demonstrates normal recovery, adaptive
            replanning, escalation, and bounded stopping.
          </p>
        </div>

        <button
          type="button"
          className="batch-run-button"
          onClick={runDemoBatch}
          disabled={loading}
        >
          {loading ? (
            <>
              <RotateCcw
                className="spin"
                size={16}
              />
              Running batch...
            </>
          ) : (
            <>
              <Play size={16} />
              Run demo batch
            </>
          )}
        </button>
      </section>

      {error && (
        <div className="error-box global-error">
          <TriangleAlert size={16} />
          <span>{error}</span>
        </div>
      )}

      {!batchResult ? (
        <section className="batch-empty">
          <div className="batch-empty-icon">
            {loading ? (
              <RotateCcw className="spin" size={26} />
            ) : (
              <Gauge size={26} />
            )}
          </div>

          <h2>
            {loading
              ? "Running recovery batch..."
              : "Batch dashboard ready"}
          </h2>

          <p>
            {loading
              ? "ATRR is evaluating transactions and running recovery scenarios."
              : "Run the demo batch to populate revenue risk, recovery outcomes, and the intervention journey."}
          </p>

          {!loading && (
            <div className="scenario-row">
              <ScenarioChip
                label="NORMAL"
                icon={<CheckCircle2 size={13} />}
              />

              <ScenarioChip
                label="REPLAN"
                icon={<RefreshCw size={13} />}
              />

              <ScenarioChip
                label="ESCALATE"
                icon={<AlertTriangle size={13} />}
              />

              <ScenarioChip
                label="STOP"
                icon={<StopCircle size={13} />}
              />
            </div>
          )}
        </section>
      ) : (
        <>
          <BatchKpis metrics={metrics} />

          <section className="batch-main-grid">
            <div className="card chart-card">
              <CardHeader
                label="RECOVERY ECONOMICS"
                title="Revenue recovery"
              />

              <div className="revenue-bars">
                <RevenueBar
                  label="Revenue at risk"
                  value={metrics.revenue_at_risk}
                  total={metrics.revenue_at_risk}
                />

                <RevenueBar
                  label="Revenue recovered"
                  value={metrics.revenue_recovered}
                  total={metrics.revenue_at_risk}
                />

                <RevenueBar
                  label="Remaining risk"
                  value={Math.max(
                    metrics.revenue_at_risk -
                      metrics.revenue_recovered,
                    0
                  )}
                  total={metrics.revenue_at_risk}
                />
              </div>
            </div>

            <div className="card outcome-card">
              <CardHeader
                label="OUTCOME DISTRIBUTION"
                title="Agent outcomes"
              />

              <div className="outcome-list">
                <OutcomeRow
                  label="Recovered"
                  value={metrics.transactions_recovered}
                  icon={<CheckCircle2 size={16} />}
                  tone="success"
                />

                <OutcomeRow
                  label="Multi-attempt"
                  value={metrics.transactions_replanned}
                  icon={<RefreshCw size={16} />}
                  tone="replan"
                />

                <OutcomeRow
                  label="Escalated"
                  value={metrics.transactions_escalated}
                  icon={<AlertTriangle size={16} />}
                  tone="escalated"
                />

                <OutcomeRow
                  label="Stopped"
                  value={metrics.transactions_stopped}
                  icon={<StopCircle size={16} />}
                  tone="stopped"
                />
              </div>
            </div>
          </section>

          <section className="card batch-table-card">
            <CardHeader
              label="TRANSACTION QUEUE"
              title="Recovery decisions"
              action={
                <span className="table-count">
                  {metrics.transactions_evaluated} transactions
                </span>
              }
            />

            <div className="batch-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Transaction</th>
                    <th>Risk</th>
                    <th>Revenue at risk</th>
                    <th>Decision</th>
                    <th>Attempts</th>
                    <th>Outcome</th>
                  </tr>
                </thead>

                <tbody>
                  {batchResult.results.map((item) => (
                    <tr key={item.transaction_id}>
                      <td>
                        <strong>{item.transaction_id}</strong>
                      </td>

                      <td>
                        <span
                          className={`risk-tag ${String(
                            item.revenue_risk?.risk_level || ""
                          ).toLowerCase()}`}
                        >
                          {item.revenue_risk?.risk_level}
                        </span>
                      </td>

                      <td>
                        INR{" "}
                        {Number(
                          item.revenue_risk?.revenue_at_risk || 0
                        ).toLocaleString("en-IN")}
                      </td>

                      <td>
                        {item.selected_action
                          ? item.selected_action.action_type.replaceAll(
                              "_",
                              " "
                            )
                          : "No automated action"}
                      </td>

                      <td>{item.attempts?.length || 0}</td>

                      <td>
                        <OutcomeBadge status={item.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}

function BatchKpis({ metrics }) {
  const cards = [
    {
      label: "Revenue at risk",
      value: `INR ${Number(
        metrics.revenue_at_risk || 0
      ).toLocaleString("en-IN")}`,
      icon: <TrendingUp size={17} />,
      className: "kpi-risk",
    },
    {
      label: "Revenue recovered",
      value: `INR ${Number(
        metrics.revenue_recovered || 0
      ).toLocaleString("en-IN")}`,
      icon: <CheckCircle2 size={17} />,
      className: "kpi-recovered",
    },
    {
      label: "Recovery rate",
      value: `${Number(
        metrics.recovery_rate * 100
      ).toFixed(1)}%`,
      icon: <Gauge size={17} />,
      className: "kpi-rate",
    },
    {
      label: "Revenue recovery",
      value: `${Number(
        metrics.revenue_recovery_rate * 100
      ).toFixed(1)}%`,
      icon: <Activity size={17} />,
      className: "kpi-revenue",
    },
    {
      label: "Multi-attempt",
      value: metrics.transactions_replanned,
      icon: <RefreshCw size={17} />,
      className: "kpi-replan",
    },
    {
      label: "Escalated / stopped",
      value: `${
        metrics.transactions_escalated +
        metrics.transactions_stopped
      }`,
      icon: <Users size={17} />,
      className: "kpi-guardrail",
    },
  ];

  return (
    <section className="kpi-grid">
      {cards.map((card) => (
        <div
          className={`kpi-card ${card.className}`}
          key={card.label}
        >
          <div className="kpi-icon">
            {card.icon}
          </div>

          <div className="kpi-label">
            {card.label}
          </div>

          <strong>{card.value}</strong>
        </div>
      ))}
    </section>
  );
}

function OutcomeRow({
  label,
  value,
  icon,
  tone,
}) {
  return (
    <div className="outcome-row">
      <div className={`outcome-icon ${tone}`}>
        {icon}
      </div>

      <span>{label}</span>

      <strong>{value}</strong>
    </div>
  );
}

function ScenarioChip({ label, icon }) {
  return (
    <div className="scenario-chip">
      {icon}
      {label}
    </div>
  );
}

function RevenueBar({ label, value, total }) {
  const percentage =
    total > 0
      ? Math.min((value / total) * 100, 100)
      : 0;

  return (
    <div className="revenue-bar-row">
      <div className="revenue-bar-header">
        <span>{label}</span>

        <strong>
          INR{" "}
          {Number(value).toLocaleString("en-IN")}
        </strong>
      </div>

      <div className="revenue-bar-track">
        <div
          className="revenue-bar-fill"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>

      <span className="revenue-bar-percent">
        {percentage.toFixed(1)}%
      </span>
    </div>
  );
}

function OutcomeBadge({ status }) {
  let icon = <AlertTriangle size={12} />;
  let className = "failed";

  if (status === "RECOVERED") {
    icon = <CheckCircle2 size={12} />;
    className = "success";
  } else if (status === "ESCALATED") {
    className = "escalated";
  } else if (status === "RECOVERY_STOPPED") {
    icon = <StopCircle size={12} />;
    className = "stopped";
  }

  return (
    <span className={`outcome-badge ${className}`}>
      {icon}
      {status.replaceAll("_", " ")}
    </span>
  );
}

function AuditRow({ event }) {
  return (
    <div className="audit-row">
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
  );
}

function CardHeader({
  label,
  title,
  badge,
  action,
}) {
  return (
    <div className="card-header">
      <div>
        <div className="section-label">{label}</div>
        <h2>{title}</h2>
      </div>

      {badge && (
        <span className="status-badge">
          {badge}
        </span>
      )}

      {action}
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

function StatusStep({
  number,
  title,
  state,
  last,
}) {
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
          <CircleStop size={13} />
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
            ? "Stopped / not completed"
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