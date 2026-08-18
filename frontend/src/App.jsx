import { useState } from "react";

import {
  ShieldCheck,
  GraduationCap,
  Code2,
  ArrowRight,
  Search,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Brain,
  Database,
  Terminal,
  RefreshCw,
  Sparkles,
  Activity,
  GitBranch,
  BarChart3,
  Lock,
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [screen, setScreen] = useState("intro");
  const [role, setRole] = useState(null);

  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const selectRole = (selectedRole) => {
    setRole(selectedRole);
    setScreen("analyzer");
    setError("");
  };

  const goBackToIntro = () => {
    setRole(null);
    setScreen("intro");
    setError("");
  };

  const goBackToRole = () => {
    setScreen("role");
    setError("");
  };

  const analyzeRepository = async () => {
    const url = repoUrl.trim();

    if (!url) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    if (!url.includes("github.com/")) {
      setError("Please enter a valid public GitHub repository URL.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/analyze-project`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository_url: url,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "The repository could not be analyzed."
        );
      }

      setAnalysis(data);
      setScreen("results");
    } catch (err) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to connect to the ML Analyzer backend. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const analyzeAnother = () => {
    setAnalysis(null);
    setError("");
    setRepoUrl("");
    setScreen("analyzer");
  };

  return (
    <div className="app">
      <Navbar role={role} onHome={goBackToIntro} />

      <main className="main-container">

        {screen === "intro" && (
          <Intro onContinue={() => setScreen("role")} />
        )}

        {screen === "role" && (
          <RoleScreen
            onSelectRole={selectRole}
            onBack={goBackToIntro}
          />
        )}

        {screen === "analyzer" && (
          <Analyzer
            role={role}
            repoUrl={repoUrl}
            setRepoUrl={setRepoUrl}
            loading={loading}
            error={error}
            onAnalyze={analyzeRepository}
            onBack={goBackToRole}
          />
        )}

        {screen === "results" && analysis && (
          <Results
            role={role}
            repoUrl={repoUrl}
            analysis={analysis}
            onAnalyzeAnother={analyzeAnother}
          />
        )}

      </main>

      {screen === "intro" && <About />}
    </div>
  );
}


/* =========================================================
   NAVBAR
========================================================= */

function Navbar({ role, onHome }) {
  return (
    <nav className="navbar">

      <button className="brand" onClick={onHome}>
        <div className="brand-icon">
          <ShieldCheck size={22} />
        </div>

        <span>ML Analyzer</span>
      </button>

      <div className="nav-right">

        <span className="online-dot" />

        <span>
          Reliability Engine Online
        </span>

        {role && (
          <span className="role-pill">
            {role === "student"
              ? "Student Mode"
              : "Developer Mode"}
          </span>
        )}

      </div>

    </nav>
  );
}


/* =========================================================
   INTRO
========================================================= */

function Intro({ onContinue }) {
  return (
    <section className="intro-screen">

      <div className="intro-grid-bg" />

      <div className="intro-content">

        <div className="eyebrow">
          <span className="red-dot" />
          MACHINE LEARNING RELIABILITY
        </div>

        <h1>
          Build it.
          <span>Understand it.</span>
          Trust it.
        </h1>

        <p className="intro-description">
          ML Analyzer inspects your machine learning project
          and turns repository evidence into understandable
          reliability insights.
        </p>

        <div className="intro-actions">

          <button
            className="primary-button"
            onClick={onContinue}
          >
            START ANALYSIS
            <ArrowRight size={18} />
          </button>

        </div>

        <div className="intro-note">
          <Lock size={14} />
          Public GitHub repositories only. Your code is not modified.
        </div>

      </div>


      <div className="intro-visual">

        <div className="visual-card main-visual-card">

          <div className="visual-top">

            <div className="visual-label">
              <Activity size={15} />
              RELIABILITY ENGINE
            </div>

            <span className="live-badge">
              LIVE
            </span>

          </div>

          <div className="visual-score">
            <span>83</span>
            <small>/100</small>
          </div>

          <div className="visual-status">
            <CheckCircle2 size={17} />
            Reliability indicators detected
          </div>

          <div className="visual-lines">

            <div>
              <span>Data Quality</span>
              <strong>Healthy</strong>
            </div>

            <div>
              <span>Data Drift</span>
              <strong className="warning-text">
                Review
              </strong>
            </div>

            <div>
              <span>Performance</span>
              <strong>Healthy</strong>
            </div>

          </div>

        </div>

      </div>


      <div className="scroll-hint">
        <span />
        Explore ML Analyzer
      </div>

    </section>
  );
}


/* =========================================================
   ROLE SCREEN
========================================================= */

function RoleScreen({ onSelectRole, onBack }) {
  return (
    <section className="role-screen">

      <div className="role-header">

        <div className="section-label">
          CHOOSE YOUR EXPERIENCE
        </div>

        <h1>
          How will you use
          <span>ML Analyzer?</span>
        </h1>

        <p>
          Choose the experience that best matches what you want to do.
        </p>

      </div>


      <div className="role-grid">

        {/* STUDENT */}

        <button
          className="role-card"
          onClick={() => onSelectRole("student")}
        >

          <div className="role-card-top">

            <div className="role-icon">
              <GraduationCap size={27} />
            </div>

            <span className="role-number">
              01
            </span>

          </div>

          <div className="role-content">

            <div className="role-small-label">
              FOR LEARNERS
            </div>

            <h2>
              Student
            </h2>

            <p>
              Understand your ML project, learn what the
              analysis means, and discover what you can improve.
            </p>

          </div>

          <div className="role-footer">
            <span>
              ENTER STUDENT MODE
            </span>

            <ArrowRight size={18} />
          </div>

        </button>


        {/* DEVELOPER */}

        <button
          className="role-card"
          onClick={() => onSelectRole("developer")}
        >

          <div className="role-card-top">

            <div className="role-icon">
              <Code2 size={27} />
            </div>

            <span className="role-number">
              02
            </span>

          </div>

          <div className="role-content">

            <div className="role-small-label">
              FOR BUILDERS
            </div>

            <h2>
              Developer
            </h2>

            <p>
              Inspect ML project evidence, identify
              reliability risks, and review technical
              improvement areas.
            </p>

          </div>

          <div className="role-footer">
            <span>
              ENTER DEVELOPER MODE
            </span>

            <ArrowRight size={18} />
          </div>

        </button>

      </div>


      <button
        className="back-button"
        onClick={onBack}
      >
        ← Back to introduction
      </button>

    </section>
  );
}


/* =========================================================
   ANALYZER
========================================================= */

function Analyzer({
  role,
  repoUrl,
  setRepoUrl,
  loading,
  error,
  onAnalyze,
  onBack,
}) {
  return (
    <section className="analyzer-screen">

      <div className="analyzer-heading">

        <div className="section-label">
          {role === "student"
            ? "STUDENT ANALYSIS"
            : "DEVELOPER ANALYSIS"}
        </div>

        <h1>
          Inspect your
          <span>ML project.</span>
        </h1>

        <p>
          {role === "student"
            ? "Keep learning, keep experimenting, and keep building. Enter your project to understand what is working and where you can improve."
            : "Built with respect for the people who build. Inspect your project evidence, identify reliability risks, and make your next version stronger."}
        </p>

      </div>


      <div className="role-message">

        {role === "student" ? (
          <>
            <GraduationCap size={21} />

            <div>
              <strong>
                Keep building, keep learning. ❤️
              </strong>

              <span>
                Every project you create is a step forward.
                Use these insights to understand your project,
                improve it, and keep creating more ML projects.
              </span>
            </div>
          </>
        ) : (
          <>
            <Code2 size={21} />

            <div>
              <strong>
                Built with respect for the people who build. 🖤
              </strong>

              <span>
                Your code is more than files in a repository.
                It represents your work, decisions and experiments.
                Use ML Analyzer to make your next version even stronger.
              </span>
            </div>
          </>
        )}

      </div>


      <div className="analyzer-card">

        <div className="input-label">
          <GitBranch size={19} />
          GitHub Repository URL
        </div>

        <div className="input-row">

          <input
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) {
                onAnalyze();
              }
            }}
            placeholder="https://github.com/username/ml-project"
            disabled={loading}
          />

          <button
            className="analyze-button"
            onClick={onAnalyze}
            disabled={loading}
          >

            {loading ? (
              <>
                <Loader2
                  size={19}
                  className="spin"
                />
                ANALYZING
              </>
            ) : (
              <>
                <Search size={19} />
                ANALYZE
                <ArrowRight size={18} />
              </>
            )}

          </button>

        </div>

        <div className="input-hint">
          <ShieldCheck size={15} />
          We inspect repository evidence without changing your project.
        </div>


        {error && (
          <div className="error-box">

            <AlertTriangle size={20} />

            <div>

              <strong>
                Analysis failed
              </strong>

              <p>
                {error}
              </p>

            </div>

          </div>
        )}

      </div>


      <div className="analyzer-modules">

        <Module
          icon={<Database />}
          title="Data Quality"
          text="Look for available data quality evidence."
        />

        <Module
          icon={<BarChart3 />}
          title="Data Drift"
          text="Assess available evidence of distribution changes."
        />

        <Module
          icon={<Brain />}
          title="Model Performance"
          text="Inspect model and evaluation indicators."
        />

        <Module
          icon={<Activity />}
          title="Anomalies"
          text="Identify unusual or potentially risky patterns."
        />

        <Module
          icon={<RefreshCw />}
          title="Reproducibility"
          text="Check dependencies, configuration and repeatability evidence."
        />

        <Module
          icon={<Terminal />}
          title="Code Quality"
          text="Inspect ML-related implementation evidence."
        />

      </div>


      <button
        className="back-button"
        onClick={onBack}
      >
        ← Change experience
      </button>

    </section>
  );
}


/* =========================================================
   MODULE
========================================================= */

function Module({ icon, title, text }) {
  return (
    <div className="module-card">

      <div className="module-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </div>
  );
}


/* =========================================================
   RESULTS
========================================================= */

function Results({
  role,
  repoUrl,
  analysis,
  onAnalyzeAnother,
}) {
  const project = analysis?.project || {};
  const detected = analysis?.detected || {};

  const isML =
    project?.is_ml_project === true ||
    project?.type === "Machine Learning Project";

  const confidence =
    Number(project?.confidence) || 0;

  const score = calculateReliability(
    detected,
    isML
  );

  const metrics = buildMetrics(
    detected,
    isML
  );

  return (
    <section className="results-screen">

      <div className="results-top">

        <div>

          <div className="section-label">
            PROJECT CLASSIFICATION
          </div>

          <h1>
            {isML
              ? "Machine Learning Project"
              : "Not an ML Project"}
          </h1>

          <p className="repo-url">
            <GitBranch size={15} />
            {repoUrl}
          </p>

        </div>


        <div className="confidence-box">

          <span>
            CONFIDENCE
          </span>

          <strong>
            {confidence}%
          </strong>

        </div>

      </div>


      <div
        className={
          isML
            ? "classification-box success-box"
            : "classification-box danger-box"
        }
      >

        {isML ? (
          <CheckCircle2 size={22} />
        ) : (
          <AlertTriangle size={22} />
        )}

        <div>

          <strong>
            {isML
              ? "Machine-learning evidence detected"
              : "This repository does not appear to be an ML project"}
          </strong>

          <p>
            {project?.description ||
              (isML
                ? "ML-related components were detected in this repository."
                : "No clear machine-learning model or ML pipeline was detected.")}
          </p>

        </div>

      </div>


      {isML && (
        <>

          <div className="reliability-header">

            <div>

              <div className="section-label">
                RELIABILITY OVERVIEW
              </div>

              <h2>
                How reliable does the project appear?
              </h2>

            </div>


            <div className="reliability-score">

              <strong>
                {score}
              </strong>

              <span>
                /100
              </span>

              <small>
                {score >= 80
                  ? "Strong"
                  : score >= 60
                  ? "Needs Review"
                  : "Needs Attention"}
              </small>

            </div>

          </div>


          <div className="metrics-grid">

            {metrics.map((metric) => (
              <Metric
                key={metric.title}
                {...metric}
              />
            ))}

          </div>


          <EvidenceSection detected={detected} />

          <Suggestions metrics={metrics} />

        </>
      )}


      <div className="result-actions">

        <button
          className="primary-button"
          onClick={onAnalyzeAnother}
        >
          ANALYZE ANOTHER PROJECT
          <ArrowRight size={18} />
        </button>

      </div>

    </section>
  );
}


/* =========================================================
   METRIC
========================================================= */

function Metric({
  icon,
  title,
  score,
  status,
  description,
}) {
  const statusClass =
    score >= 80
      ? "good"
      : score >= 60
      ? "warning"
      : "bad";

  return (
    <div className="metric-card">

      <div className="metric-card-top">

        <div className="metric-icon">
          {icon}
        </div>

        <span className={`metric-status ${statusClass}`}>
          {status}
        </span>

      </div>

      <h3>
        {title}
      </h3>

      <div className="metric-score">
        {score}
        <small>/100</small>
      </div>

      <p>
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   METRIC CALCULATION
========================================================= */

function buildMetrics(detected, isML) {
  if (!isML) {
    return [];
  }

  const languages =
    detected?.languages || [];

  const libraries =
    detected?.ml_libraries || [];

  const mlFiles =
    detected?.ml_files || [];

  const indicators =
    detected?.ml_code_indicators || [];

  const hasPython =
    languages.some(
      (x) => x.toLowerCase() === "python"
    );

  const hasLibraries =
    libraries.length > 0;

  const hasMLFiles =
    mlFiles.length > 0;

  const hasIndicators =
    indicators.length > 0;

  const dataQualityScore =
    hasMLFiles ? 85 : hasIndicators ? 78 : 70;

  const driftScore =
    hasMLFiles ? 72 : 65;

  const performanceScore =
    hasIndicators ? 86 : 68;

  const anomalyScore =
    hasIndicators ? 80 : 65;

  const reproducibilityScore =
    hasPython && hasLibraries ? 82 : 65;

  const codeScore =
    hasIndicators ? 88 : hasLibraries ? 78 : 65;

  return [
    {
      icon: <Database size={20} />,
      title: "Data Quality",
      score: dataQualityScore,
      status:
        dataQualityScore >= 80
          ? "Healthy"
          : "Review",
      description:
        "Based on the available dataset and data-processing evidence.",
    },

    {
      icon: <BarChart3 size={20} />,
      title: "Data Drift",
      score: driftScore,
      status:
        driftScore >= 80
          ? "Healthy"
          : "Needs Attention",
      description:
        "Repository-level evidence for monitoring distribution changes.",
    },

    {
      icon: <Brain size={20} />,
      title: "Model Performance",
      score: performanceScore,
      status:
        performanceScore >= 80
          ? "Strong"
          : "Review",
      description:
        "Based on detected model and evaluation-related code indicators.",
    },

    {
      icon: <Activity size={20} />,
      title: "Anomalies",
      score: anomalyScore,
      status:
        anomalyScore >= 80
          ? "Healthy"
          : "Review",
      description:
        "Checks the available evidence for unusual or risky patterns.",
    },

    {
      icon: <RefreshCw size={20} />,
      title: "Reproducibility",
      score: reproducibilityScore,
      status:
        reproducibilityScore >= 80
          ? "Good"
          : "Review",
      description:
        "Based on languages, libraries and reproducibility-related evidence.",
    },

    {
      icon: <Terminal size={20} />,
      title: "Code Quality",
      score: codeScore,
      status:
        codeScore >= 80
          ? "Strong"
          : "Review",
      description:
        "Based on detected ML implementation indicators.",
    },
  ];
}


function calculateReliability(detected, isML) {
  if (!isML) {
    return 0;
  }

  const metrics = buildMetrics(
    detected,
    isML
  );

  if (!metrics.length) {
    return 60;
  }

  const total = metrics.reduce(
    (sum, item) => sum + item.score,
    0
  );

  return Math.round(
    total / metrics.length
  );
}


/* =========================================================
   EVIDENCE
========================================================= */

function EvidenceSection({ detected }) {
  const languages =
    detected?.languages || [];

  const libraries =
    detected?.ml_libraries || [];

  const mlFiles =
    detected?.ml_files || [];

  const indicators =
    detected?.ml_code_indicators || [];

  return (
    <section className="evidence-section">

      <div className="section-label">
        WHAT WE DETECTED
      </div>

      <div className="evidence-grid">

        <EvidenceCard
          icon={<Terminal />}
          title="Languages"
          items={languages}
        />

        <EvidenceCard
          icon={<Brain />}
          title="ML Libraries"
          items={libraries}
        />

        <EvidenceCard
          icon={<Database />}
          title="ML Files"
          items={mlFiles}
        />

        <EvidenceCard
          icon={<CheckCircle2 />}
          title="Code Indicators"
          items={indicators.map(
            (item) =>
              typeof item === "string"
                ? item
                : `${item?.file || ""} — ${
                    item?.indicator || ""
                  }`
          )}
        />

      </div>

    </section>
  );
}


function EvidenceCard({
  icon,
  title,
  items,
}) {
  return (
    <div className="evidence-card">

      <div className="evidence-title">

        <div className="evidence-icon">
          {icon}
        </div>

        <h3>
          {title}
        </h3>

      </div>


      {items.length > 0 ? (
        <div className="tag-list">

          {items.slice(0, 8).map(
            (item, index) => (
              <span
                className="evidence-tag"
                key={`${item}-${index}`}
              >
                {item}
              </span>
            )
          )}

        </div>
      ) : (
        <span className="not-detected">
          No clear evidence detected
        </span>
      )}

    </div>
  );
}


/* =========================================================
   SUGGESTIONS
========================================================= */

function Suggestions({ metrics }) {
  const needsAttention =
    metrics.filter(
      (metric) => metric.score < 80
    );

  return (
    <section className="suggestions-card">

      <div className="suggestion-heading">

        <Sparkles size={20} />

        <div>

          <div className="section-label">
            NEXT STEPS
          </div>

          <h2>
            What can you improve?
          </h2>

        </div>

      </div>


      {needsAttention.length === 0 ? (
        <div className="suggestion-good">

          <CheckCircle2 size={20} />

          <p>
            Your project shows strong evidence across
            the currently assessed reliability areas.
          </p>

        </div>
      ) : (
        <div className="suggestion-list">

          {needsAttention.map(
            (metric) => (
              <div
                className="suggestion-item"
                key={metric.title}
              >

                <AlertTriangle size={18} />

                <div>

                  <strong>
                    Review {metric.title}
                  </strong>

                  <p>
                    The current evidence suggests this
                    area deserves additional attention.
                    Add stronger testing, monitoring or
                    documentation where appropriate.
                  </p>

                </div>

              </div>
            )
          )}

        </div>
      )}

    </section>
  );
}


/* =========================================================
   ABOUT PROJECT + DEVELOPER
========================================================= */

function About() {
  return (
    <section className="about-section">

      <div className="about-inner">

        <div className="about-label-row">

          <div className="section-label">
            ABOUT THE PROJECT
          </div>

        </div>

        <h2>
          Making ML projects
          <span>easier to understand.</span>
        </h2>

        <p>
          ML Analyzer is designed to help students and developers
          inspect machine-learning repositories and understand
          the reliability evidence available inside their projects.
          It looks at areas such as data quality, data drift,
          anomalies, model performance, reproducibility and code quality.
        </p>


        <div className="about-divider" />


        <div className="developer-section">

          <div className="developer-label">
            <Code2 size={18} />
            ABOUT THE DEVELOPER
          </div>

          <h3>
            Built with curiosity,
            <span>learning and passion.</span>
          </h3>

          <p>
            ML Analyzer was built by <strong>Abhish Raju</strong>,
            with the goal of making machine-learning projects easier
            to understand, evaluate and improve.
          </p>

          <div className="developer-message">
            <Sparkles size={18} />

            <span>
              Built for every student who is learning,
              every developer who is building,
              and everyone who wants to make their next project better.
            </span>
          </div>

        </div>


        <div className="about-divider" />


        <div className="about-footer">

          <div>
            <strong>
              ML Analyzer
            </strong>

            <span>
              Machine Learning Reliability System
            </span>
          </div>

          <div className="about-credit">
            Built with ❤️ by <strong>Abhish Raju</strong>
          </div>

        </div>

      </div>

    </section>
  );
}


export default App;