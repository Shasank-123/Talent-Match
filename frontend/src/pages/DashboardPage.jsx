import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboardAnalytics } from "../api";
import { FileText, Briefcase, TrendingUp, Star, ChevronRight, Zap } from "lucide-react";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getDashboardAnalytics()
      .then((res) => setStats(res.data.payload))
      .catch(() => toast.error("Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  const statItems = [
    { icon: "📄", label: "Total Resumes", value: stats?.total_resumes ?? 0, color: "#8b5cf6", sub: "Uploaded" },
    { icon: "💼", label: "Jobs Posted", value: stats?.total_jobs ?? 0, color: "#14b8a6", sub: `${stats?.active_jobs ?? 0} active` },
    { icon: "🏆", label: "Rankings Run", value: stats?.total_rankings ?? 0, color: "#f59e0b", sub: "Analyses" },
    { icon: "📊", label: "Avg Match Score", value: `${stats?.average_match_score ?? 0}%`, color: "#10b981", sub: "Overall" },
  ];

  const quickActions = [
    { icon: "📤", label: "Upload Resume", desc: "Add candidate resumes", to: "/resumes", color: "var(--accent-purple)" },
    { icon: "📝", label: "Post a Job", desc: "Create job description", to: "/jobs", color: "var(--accent-teal)" },
    { icon: "🚀", label: "Run Analysis", desc: "Rank candidates vs job", to: "/rankings", color: "var(--accent-amber)" },
    { icon: "📋", label: "Generate Report", desc: "Export ranking report", to: "/reports", color: "var(--accent-green)" },
  ];

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Welcome back — here's your TalentMatch overview</p>
      </div>
      <div className="page-body">
        {/* Stats */}
        <div className="stat-cards">
          {statItems.map((s) => (
            <div className="stat-card animate-fade" key={s.label}>
              <div className="stat-card-icon">{s.icon}</div>
              <div className="stat-card-value" style={{ color: s.color }}>{loading ? "—" : s.value}</div>
              <div className="stat-card-label">{s.label}</div>
              <div className="stat-card-sub">{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Status banner */}
        {!loading && !stats?.isAnalysisReady && (
          <div style={{
            background: "rgba(139,92,246,0.08)",
            border: "1px solid rgba(139,92,246,0.2)",
            borderRadius: "var(--radius-lg)",
            padding: "20px 24px",
            marginBottom: "28px",
            display: "flex", alignItems: "center", gap: "12px",
          }}>
            <Zap size={20} color="var(--accent-purple-light)" />
            <div>
              <div style={{ fontWeight: 600, marginBottom: "2px" }}>Get started</div>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                Upload resumes, create a job, then run your first analysis to see rankings.
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div style={{ marginBottom: "8px", fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Quick Actions
        </div>
        <div className="grid-2" style={{ marginBottom: "28px" }}>
          {quickActions.map((a) => (
            <div
              key={a.to}
              className="card"
              style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: "16px" }}
              onClick={() => navigate(a.to)}
            >
              <div style={{
                width: 44, height: 44, borderRadius: "var(--radius-md)",
                background: `${a.color}1a`, display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: "22px", flexShrink: 0
              }}>
                {a.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, marginBottom: "2px" }}>{a.label}</div>
                <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{a.desc}</div>
              </div>
              <ChevronRight size={16} color="var(--text-muted)" />
            </div>
          ))}
        </div>

        {/* How it works */}
        <div style={{ marginBottom: "8px", fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          How TalentMatch Works
        </div>
        <div className="card">
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {[
              { step: "1", title: "Upload Resumes", desc: "Upload PDF or DOCX resumes. AI parses and extracts skills automatically." },
              { step: "2", title: "Create Job Description", desc: "Define the role with required skills, experience level, and job context." },
              { step: "3", title: "Run Analysis", desc: "ML engine computes semantic similarity and skill match scores." },
              { step: "4", title: "Review Rankings", desc: "View ranked candidates with AI-generated explanations and skill gaps." },
              { step: "5", title: "Interview & Report", desc: "Generate targeted interview questions and downloadable PDF reports." },
            ].map((s) => (
              <div key={s.step} style={{ display: "flex", gap: "16px", alignItems: "flex-start" }}>
                <div style={{
                  width: 28, height: 28, borderRadius: "50%",
                  background: "var(--gradient-1)", color: "white",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "12px", fontWeight: 700, flexShrink: 0
                }}>
                  {s.step}
                </div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: "2px" }}>{s.title}</div>
                  <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
