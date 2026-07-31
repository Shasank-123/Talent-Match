import { useEffect, useState } from "react";
import { getJobs, getResumes, generateInterviewQuestions, getInterviewQuestions } from "../api";
import toast from "react-hot-toast";
import { Sparkles } from "lucide-react";

const DIFFICULTY_COLORS = { easy: "badge-green", medium: "badge-amber", hard: "badge-red" };
const CATEGORY_ICONS = { behavioral: "🧠", technical: "💻", skill_gap: "📈", strategic: "🎯" };

export default function InterviewsPage() {
  const [jobList, setJobList] = useState([]);
  const [resumeList, setResumeList] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [selectedResume, setSelectedResume] = useState("");
  const [interviewQuestionList, setInterviewQuestionList] = useState([]);
  const [hasInterviewQuestions, setHasInterviewQuestions] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getJobs().then((r) => setJobList(r.data.payload.jobList));
    getResumes().then((r) => setResumeList(r.data.payload.resumeList));
  }, []);

  const loadQuestions = (resumeId, jobId) => {
    if (!resumeId) return;
    getInterviewQuestions(resumeId, jobId || null).then((res) => {
      const payload = res.data.payload;
      setInterviewQuestionList(payload.interviewQuestionList || []);
      setHasInterviewQuestions(payload.hasInterviewQuestions);
    }).catch(() => {});
  };

  const handleResumeChange = (e) => {
    setSelectedResume(e.target.value);
    if (e.target.value && selectedJob) loadQuestions(e.target.value, selectedJob);
  };

  const handleJobChange = (e) => {
    setSelectedJob(e.target.value);
    if (selectedResume && e.target.value) loadQuestions(selectedResume, e.target.value);
  };

  const handleGenerate = async () => {
    if (!selectedJob || !selectedResume) { toast.error("Select both a job and a candidate"); return; }
    setLoading(true);
    try {
      const res = await generateInterviewQuestions({
        job_id: parseInt(selectedJob),
        resume_id: parseInt(selectedResume),
      });
      const payload = res.data.payload;
      setInterviewQuestionList(payload.interviewQuestionList);
      setHasInterviewQuestions(payload.hasInterviewQuestions);
      toast.success(`${payload.interviewQuestionList.length} questions generated!`);
    } catch (err) {
      toast.error(err.response?.data?.detail?.error_detail || "Generation failed");
    } finally {
      setLoading(false);
    }
  };

  const grouped = interviewQuestionList.reduce((acc, q) => {
    acc[q.category] = acc[q.category] || [];
    acc[q.category].push(q);
    return acc;
  }, {});

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Interview Questions</h1>
        <p className="page-subtitle">AI-generated targeted interview questions per candidate</p>
      </div>

      <div className="page-body">
        {/* Controls */}
        <div className="card mb-6">
          <div className="grid-2" style={{ marginBottom: "12px" }}>
            <div>
              <label className="form-label">Select Job</label>
              <select id="interview-job" className="form-input form-select" value={selectedJob} onChange={handleJobChange}>
                <option value="">-- Choose a job --</option>
                {jobList.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label">Select Candidate</label>
              <select id="interview-resume" className="form-input form-select" value={selectedResume} onChange={handleResumeChange}>
                <option value="">-- Choose a candidate --</option>
                {resumeList.map((r) => (
                  <option key={r.id} value={r.id}>{r.candidate_name || `Resume #${r.id}`}</option>
                ))}
              </select>
            </div>
          </div>
          <button
            id="generate-questions-btn"
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={loading || !selectedJob || !selectedResume}
          >
            {loading ? <><div className="spinner spinner-sm" /> Generating…</> : <><Sparkles size={15} /> Generate Questions</>}
          </button>
        </div>

        {/* Questions */}
        {hasInterviewQuestions && interviewQuestionList.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {Object.entries(grouped).map(([category, questions]) => (
              <div key={category}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                  <span style={{ fontSize: "18px" }}>{CATEGORY_ICONS[category] || "❓"}</span>
                  <span style={{ fontWeight: 600, textTransform: "capitalize" }}>{category.replace("_", " ")} Questions</span>
                  <span className="badge badge-gray">{questions.length}</span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {questions.map((q, i) => (
                    <div key={q.id} className="interview-card">
                      <div className="interview-q-text">
                        <span style={{ color: "var(--text-muted)", marginRight: "8px" }}>Q{i + 1}.</span>
                        {q.question}
                      </div>
                      <div className="interview-meta">
                        <span className={`badge ${DIFFICULTY_COLORS[q.difficulty] || "badge-gray"}`}>
                          {q.difficulty}
                        </span>
                        <span className="badge badge-purple">{q.category}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state card">
            <div className="empty-state-icon">💬</div>
            <h3>No questions generated yet</h3>
            <p>Select a job and candidate, then click "Generate Questions"</p>
          </div>
        )}
      </div>
    </>
  );
}
