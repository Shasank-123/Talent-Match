import { useEffect, useState } from "react";
import { getJobs, createJob, deleteJob } from "../api";
import toast from "react-hot-toast";
import { Plus, Trash2, X, Briefcase } from "lucide-react";

const EMPTY_FORM = {
  title: "", company: "", description: "",
  required_skills: [], preferred_skills: [],
  experience_years: 0, location: ""
};

export default function JobsPage() {
  const [jobList, setJobList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [skillInput, setSkillInput] = useState("");
  const [prefSkillInput, setPrefSkillInput] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchJobs = () => {
    setLoading(true);
    getJobs()
      .then((res) => setJobList(res.data.payload.jobList))
      .catch(() => toast.error("Failed to load jobs"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchJobs(); }, []);

  const addSkill = (e, field, input, setInput) => {
    if (e.key === "Enter" && input.trim()) {
      e.preventDefault();
      const tag = input.trim().toLowerCase();
      if (!form[field].includes(tag)) {
        setForm({ ...form, [field]: [...form[field], tag] });
      }
      setInput("");
    }
  };

  const removeSkill = (field, skill) => {
    setForm({ ...form, [field]: form[field].filter((s) => s !== skill) });
  };

  const handleSave = async () => {
    if (!form.title || !form.description) {
      toast.error("Title and description are required");
      return;
    }
    setSaving(true);
    try {
      await createJob(form);
      toast.success("Job created!");
      setShowModal(false);
      setForm(EMPTY_FORM);
      fetchJobs();
    } catch (err) {
      toast.error(err.response?.data?.detail?.error_detail || "Failed to create job");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Delete "${title}"?`)) return;
    try {
      await deleteJob(id);
      toast.success("Job deleted");
      fetchJobs();
    } catch {
      toast.error("Failed to delete");
    }
  };

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Jobs</h1>
            <p className="page-subtitle">Manage job descriptions for candidate matching</p>
          </div>
          <button id="create-job-btn" className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> New Job
          </button>
        </div>
      </div>

      <div className="page-body">
        {loading ? (
          <div className="flex items-center gap-3"><div className="spinner" /><span style={{ color: "var(--text-secondary)" }}>Loading...</span></div>
        ) : jobList.length === 0 ? (
          <div className="empty-state card">
            <div className="empty-state-icon">💼</div>
            <h3>No jobs yet</h3>
            <p>Create your first job description to start matching candidates</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setShowModal(true)}>
              <Plus size={16} /> Create Job
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {jobList.map((job) => (
              <div key={job.id} className="card" style={{ display: "flex", gap: "16px", alignItems: "flex-start" }}>
                <div style={{
                  width: 44, height: 44, borderRadius: "var(--radius-md)",
                  background: "rgba(20,184,166,0.15)", display: "flex", alignItems: "center",
                  justifyContent: "center", fontSize: "20px", flexShrink: 0
                }}>
                  <Briefcase size={20} color="var(--accent-teal)" />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
                    <span style={{ fontWeight: 600, fontSize: "16px" }}>{job.title}</span>
                    <span className={`badge ${job.is_active ? "badge-green" : "badge-gray"}`}>
                      {job.is_active ? "Active" : "Closed"}
                    </span>
                  </div>
                  {job.company && <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "8px" }}>🏢 {job.company}{job.location ? ` · 📍 ${job.location}` : ""}</div>}
                  <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "10px" }}>
                    {job.description.length > 140 ? job.description.slice(0, 140) + "…" : job.description}
                  </p>
                  <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
                    <div className="skill-tags">
                      {(job.required_skills || []).slice(0, 4).map((s) => (
                        <span key={s} className="skill-tag">{s}</span>
                      ))}
                      {(job.required_skills || []).length > 4 && (
                        <span className="badge badge-gray">+{job.required_skills.length - 4} more</span>
                      )}
                    </div>
                    {job.experience_years > 0 && (
                      <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                        {job.experience_years}+ yr exp
                      </span>
                    )}
                  </div>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(job.id, job.title)}>
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal" style={{ maxHeight: "90vh", overflowY: "auto" }}>
            <div className="modal-header">
              <span className="modal-title">Create Job Description</span>
              <button className="modal-close" onClick={() => setShowModal(false)}><X size={18} /></button>
            </div>

            <div className="form-group">
              <label className="form-label">Job Title *</label>
              <input id="job-title" className="form-input" placeholder="e.g. Senior Python Developer" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Company</label>
                <input className="form-input" placeholder="Acme Corp" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Location</label>
                <input className="form-input" placeholder="Remote / City" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Experience Required (years)</label>
              <input type="number" className="form-input" min="0" max="30" value={form.experience_years} onChange={(e) => setForm({ ...form, experience_years: parseInt(e.target.value) || 0 })} />
            </div>
            <div className="form-group">
              <label className="form-label">Job Description *</label>
              <textarea id="job-desc" className="form-input form-textarea" placeholder="Describe the role, responsibilities..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Required Skills <span style={{ color: "var(--text-muted)" }}>(press Enter to add)</span></label>
              <input id="job-skills" className="form-input" placeholder="e.g. python" value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => addSkill(e, "required_skills", skillInput, setSkillInput)}
              />
              <div className="skill-tags mt-4">
                {form.required_skills.map((s) => (
                  <span key={s} className="skill-tag" style={{ cursor: "pointer" }} onClick={() => removeSkill("required_skills", s)}>
                    {s} <X size={10} />
                  </span>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Preferred Skills <span style={{ color: "var(--text-muted)" }}>(press Enter)</span></label>
              <input className="form-input" placeholder="e.g. docker" value={prefSkillInput}
                onChange={(e) => setPrefSkillInput(e.target.value)}
                onKeyDown={(e) => addSkill(e, "preferred_skills", prefSkillInput, setPrefSkillInput)}
              />
              <div className="skill-tags mt-4">
                {form.preferred_skills.map((s) => (
                  <span key={s} className="skill-tag badge-teal" style={{ cursor: "pointer" }} onClick={() => removeSkill("preferred_skills", s)}>
                    {s} <X size={10} />
                  </span>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end", marginTop: "8px" }}>
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button id="save-job-btn" className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? <><div className="spinner spinner-sm" /> Saving…</> : "Create Job"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
