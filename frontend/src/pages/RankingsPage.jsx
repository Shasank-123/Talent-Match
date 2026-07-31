import { useEffect, useState } from "react";
import { getJobs, getResumes, analyzeRankings, getRankings } from "../api";
import toast from "react-hot-toast";
import { Play, ChevronDown, ChevronUp } from "lucide-react";

function ScoreBar({ value }) {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? "#10b981" : pct >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <div className="score-bar" style={{ flex: 1 }}>
        <div className="score-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span style={{ fontSize: "13px", fontWeight: 600, color, minWidth: "36px" }}>{pct}%</span>
    </div>
  );
}

export default function RankingsPage() {
  const [jobList, setJobList] = useState([]);
  const [resumeList, setResumeList] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [rankingList, setRankingList] = useState([]);
  const [isRankingCompleted, setIsRankingCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [expanding, setExpanding] = useState(null);

  useEffect(() => {
    getJobs().then((r) => setJobList(r.data.payload.jobList));
    getResumes().then((r) => setResumeList(r.data.payload.resumeList));
  }, []);

  const loadRankings = (jobId) => {
    if (!jobId) return;
    getRankings(jobId)
      .then((res) => {
        setRankingList(res.data.payload.rankingList || []);
        setIsRankingCompleted(res.data.payload.rankingList?.length > 0);
      })
      .catch(() => {});
  };

  const handleJobChange = (e) => {
    setSelectedJob(e.target.value);
    setRankingList([]);
    setIsRankingCompleted(false);
    if (e.target.value) loadRankings(e.target.value);
  };

  const runAnalysis = async () => {
    if (!selectedJob) { toast.error("Select a job first"); return; }
    if (resumeList.length === 0) { toast.error("Upload some resumes first"); return; }
    setLoading(true);
    try {
      const res = await analyzeRankings({ job_id: parseInt(selectedJob) });
      const list = res.data.payload.rankingList || [];
      setRankingList(list);
      setIsRankingCompleted(true);
      toast.success(`${list.length} candidates ranked!`);
    } catch (err) {
      toast.error(err.response?.data?.detail?.error_detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const selectedJobTitle = jobList.find((j) => String(j.id) === String(selectedJob))?.title;

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Rankings</h1>
        <p className="page-subtitle">Run ML-powered candidate ranking analysis</p>
      </div>

      <div className="page-body">
        {/* Controls */}
        <div className="card mb-6">
          <div style={{ display: "flex", gap: "12px", alignItems: "flex-end" }}>
            <div style={{ flex: 1 }}>
              <label className="form-label">Select Job</label>
              <select id="job-select" className="form-input form-select" value={selectedJob} onChange={handleJobChange}>
                <option value="">-- Choose a job --</option>
                {jobList.map((j) => (
                  <option key={j.id} value={j.id}>{j.title}</option>
                ))}
              </select>
            </div>
            <div style={{ color: "var(--text-secondary)", fontSize: "13px", paddingBottom: "2px" }}>
              {resumeList.length} resume{resumeList.length !== 1 ? "s" : ""} available
            </div>
            <button
              id="run-analysis-btn"
              className="btn btn-primary"
              onClick={runAnalysis}
              disabled={loading || !selectedJob}
            >
              {loading ? <><div className="spinner spinner-sm" /> Analyzing…</> : <><Play size={15} /> Run Analysis</>}
            </button>
          </div>
        </div>

        {/* Results */}
        {isRankingCompleted && rankingList.length > 0 && (
          <>
            <div style={{ marginBottom: "12px", fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)" }}>
              RESULTS FOR: {selectedJobTitle} — {rankingList.length} candidates
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {rankingList.map((r) => (
                <div key={r.resume_id || r.id} className="card">
                  <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                    <div className={`rank-badge rank-${r.rank_position <= 3 ? r.rank_position : "other"}`}>
                      #{r.rank_position}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, marginBottom: "2px" }}>{r.candidate_name || "Candidate"}</div>
                      <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Resume #{r.resume_id}</div>
                    </div>
                    <div style={{ minWidth: "140px" }}>
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Overall Score</div>
                      <ScoreBar value={r.overall_score} />
                    </div>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setExpanding(expanding === r.resume_id ? null : r.resume_id)}
                    >
                      {expanding === r.resume_id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>

                  {expanding === r.resume_id && (
                    <div style={{ marginTop: "16px", paddingTop: "16px", borderTop: "1px solid var(--glass-border)", animation: "fadeIn 0.2s ease" }}>
                      <div className="grid-3" style={{ marginBottom: "16px" }}>
                        <div>
                          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Similarity</div>
                          <ScoreBar value={r.similarity_score} />
                        </div>
                        <div>
                          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Skill Match</div>
                          <ScoreBar value={r.skill_match_score} />
                        </div>
                        <div>
                          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Experience</div>
                          <ScoreBar value={r.experience_score} />
                        </div>
                      </div>
                      {r.explanation && (
                        <div style={{ background: "var(--glass-bg)", borderRadius: "var(--radius-sm)", padding: "12px", marginBottom: "12px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
                          💡 {r.explanation}
                        </div>
                      )}
                      <div style={{ display: "flex", gap: "24px" }}>
                        {r.matching_skills?.length > 0 && (
                          <div>
                            <div style={{ fontSize: "12px", color: "var(--accent-green)", fontWeight: 600, marginBottom: "6px" }}>✓ Matching Skills</div>
                            <div className="skill-tags">
                              {r.matching_skills.map((s) => <span key={s} className="skill-tag skill-tag-match">{s}</span>)}
                            </div>
                          </div>
                        )}
                        {r.skill_gap?.length > 0 && (
                          <div>
                            <div style={{ fontSize: "12px", color: "var(--accent-red)", fontWeight: 600, marginBottom: "6px" }}>✗ Skill Gap</div>
                            <div className="skill-tags">
                              {r.skill_gap.map((s) => <span key={s} className="skill-tag skill-tag-gap">{s}</span>)}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {selectedJob && !isRankingCompleted && !loading && (
          <div className="empty-state card">
            <div className="empty-state-icon">🏆</div>
            <h3>No rankings yet</h3>
            <p>Click "Run Analysis" to rank candidates against this job</p>
          </div>
        )}

        {!selectedJob && (
          <div className="empty-state card">
            <div className="empty-state-icon">🎯</div>
            <h3>Select a job to begin</h3>
            <p>Choose a job description above, then run the analysis</p>
          </div>
        )}
      </div>
    </>
  );
}
