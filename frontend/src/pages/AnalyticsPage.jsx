import { useEffect, useState } from "react";
import { getDashboardAnalytics, getJobsAnalytics, getCandidatesAnalytics } from "../api";
import toast from "react-hot-toast";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";

const CHART_COLORS = ["#8b5cf6", "#14b8a6", "#f59e0b", "#10b981", "#ec4899", "#0ea5e9"];

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState(null);
  const [jobsData, setJobsData] = useState([]);
  const [candidatesData, setCandidatesData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboardAnalytics(),
      getJobsAnalytics(),
      getCandidatesAnalytics(),
    ])
      .then(([d, j, c]) => {
        setDashboard(d.data.payload);
        setJobsData(j.data.payload.jobList || []);
        setCandidatesData(c.data.payload.candidateList || []);
      })
      .catch(() => toast.error("Failed to load analytics"))
      .finally(() => setLoading(false));
  }, []);

  const pieData = jobsData.map((j, i) => ({
    name: j.job_title,
    value: j.candidate_count,
  })).filter((j) => j.value > 0);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">Platform-wide performance and usage metrics</p>
      </div>

      <div className="page-body">
        {loading ? (
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div className="spinner" /><span style={{ color: "var(--text-secondary)" }}>Loading...</span>
          </div>
        ) : (
          <>
            {/* Summary */}
            <div className="stat-cards mb-6">
              {[
                { label: "Total Resumes", value: dashboard?.total_resumes, icon: "📄", color: "#8b5cf6" },
                { label: "Active Jobs", value: dashboard?.active_jobs, icon: "💼", color: "#14b8a6" },
                { label: "Total Rankings", value: dashboard?.total_rankings, icon: "🏆", color: "#f59e0b" },
                { label: "Avg Match", value: `${dashboard?.average_match_score}%`, icon: "📊", color: "#10b981" },
              ].map((s) => (
                <div key={s.label} className="stat-card">
                  <div className="stat-card-icon">{s.icon}</div>
                  <div className="stat-card-value" style={{ color: s.color }}>{s.value}</div>
                  <div className="stat-card-label">{s.label}</div>
                </div>
              ))}
            </div>

            {/* Charts */}
            <div className="grid-2 mb-6">
              {/* Bar: Job Rankings */}
              <div className="card">
                <div style={{ fontWeight: 600, marginBottom: "20px" }}>Candidates per Job</div>
                {jobsData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={jobsData}>
                      <XAxis dataKey="job_title" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} />
                      <Tooltip
                        contentStyle={{ background: "#16161f", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px", color: "#f1f5f9" }}
                      />
                      <Bar dataKey="candidate_count" fill="url(#grad1)" radius={[4, 4, 0, 0]} />
                      <defs>
                        <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#8b5cf6" />
                          <stop offset="100%" stopColor="#14b8a6" />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-state" style={{ padding: "40px" }}>
                    <div style={{ fontSize: "32px" }}>📊</div>
                    <p>Run analyses to see data</p>
                  </div>
                )}
              </div>

              {/* Pie: Top Scores */}
              <div className="card">
                <div style={{ fontWeight: 600, marginBottom: "20px" }}>Top Scores by Job</div>
                {jobsData.filter(j => j.top_score > 0).length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={jobsData.filter(j => j.top_score > 0)}
                        dataKey="top_score"
                        nameKey="job_title"
                        cx="50%" cy="50%"
                        outerRadius={70}
                        label={({ name, value }) => `${value}%`}
                      >
                        {jobsData.map((_, i) => (
                          <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Legend wrapperStyle={{ fontSize: "12px", color: "#94a3b8" }} />
                      <Tooltip
                        contentStyle={{ background: "#16161f", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px", color: "#f1f5f9" }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-state" style={{ padding: "40px" }}>
                    <div style={{ fontSize: "32px" }}>🥧</div>
                    <p>No scores yet</p>
                  </div>
                )}
              </div>
            </div>

            {/* Candidates Table */}
            {candidatesData.length > 0 && (
              <>
                <div style={{ fontWeight: 600, marginBottom: "12px", color: "var(--text-secondary)", fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  Candidate Breakdown
                </div>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Candidate</th>
                        <th>Skills</th>
                        <th>Exp.</th>
                        <th>Best Match</th>
                        <th>Jobs Applied</th>
                      </tr>
                    </thead>
                    <tbody>
                      {candidatesData.map((c) => (
                        <tr key={c.resume_id}>
                          <td style={{ fontWeight: 500 }}>{c.candidate_name || "—"}</td>
                          <td>{c.skills_count}</td>
                          <td>{c.experience_years > 0 ? `${c.experience_years} yr` : "—"}</td>
                          <td>
                            <span className={`badge ${c.best_match_score >= 75 ? "badge-green" : c.best_match_score >= 50 ? "badge-amber" : "badge-gray"}`}>
                              {c.best_match_score}%
                            </span>
                          </td>
                          <td>{c.jobs_applied}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </>
  );
}
