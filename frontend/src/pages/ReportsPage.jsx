import { useEffect, useState } from "react";
import { getJobs, generateReport, getReport, downloadReport } from "../api";
import toast from "react-hot-toast";
import { FileOutput, Download, Loader } from "lucide-react";

export default function ReportsPage() {
  const [jobList, setJobList] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [generating, setGenerating] = useState(false);
  const [reportList, setReportList] = useState([]);
  const [viewReport, setViewReport] = useState(null);

  useEffect(() => {
    getJobs().then((r) => setJobList(r.data.payload.jobList));
    const saved = JSON.parse(localStorage.getItem("tm_reports") || "[]");
    setReportList(saved);
  }, []);

  const handleGenerate = async () => {
    if (!selectedJob) { toast.error("Select a job"); return; }
    setGenerating(true);
    try {
      const res = await generateReport({ job_id: parseInt(selectedJob) });
      const payload = res.data.payload;
      const newReport = {
        report_id: payload.report_id,
        job_title: payload.job_title,
        total_candidates: payload.total_candidates,
        created_at: new Date().toISOString(),
      };
      const updated = [newReport, ...reportList];
      setReportList(updated);
      localStorage.setItem("tm_reports", JSON.stringify(updated));
      toast.success("Report generated!");
    } catch (err) {
      toast.error(err.response?.data?.detail?.error_detail || "Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const handleView = async (reportId) => {
    try {
      const res = await getReport(reportId);
      setViewReport(res.data.payload);
    } catch {
      toast.error("Failed to load report");
    }
  };

  const handleDownload = async (reportId, jobTitle) => {
    try {
      const res = await downloadReport(reportId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `${jobTitle.replace(/\s+/g, "_")}_report.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("Report downloaded!");
    } catch {
      toast.error("Download failed");
    }
  };

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Reports</h1>
        <p className="page-subtitle">Generate and download candidate ranking reports</p>
      </div>

      <div className="page-body">
        {/* Generate */}
        <div className="card mb-6">
          <div style={{ fontWeight: 600, marginBottom: "16px" }}>Generate New Report</div>
          <div style={{ display: "flex", gap: "12px", alignItems: "flex-end" }}>
            <div style={{ flex: 1 }}>
              <label className="form-label">Select Job</label>
              <select id="report-job-select" className="form-input form-select" value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)}>
                <option value="">-- Choose a job --</option>
                {jobList.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
              </select>
            </div>
            <button
              id="generate-report-btn"
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={generating || !selectedJob}
            >
              {generating ? <><Loader size={15} className="animate-spin" /> Generating…</> : <><FileOutput size={15} /> Generate Report</>}
            </button>
          </div>
        </div>

        {/* List */}
        {reportList.length > 0 ? (
          <>
            <div style={{ marginBottom: "12px", fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)" }}>
              GENERATED REPORTS
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {reportList.map((r) => (
                <div key={r.report_id} className="card" style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <div style={{ fontSize: "28px" }}>📋</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600 }}>{r.job_title}</div>
                    <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                      {r.total_candidates} candidates · Report #{r.report_id}
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
                      {new Date(r.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => handleView(r.report_id)}>
                      View
                    </button>
                    <button className="btn btn-primary btn-sm" onClick={() => handleDownload(r.report_id, r.job_title)}>
                      <Download size={13} /> Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="empty-state card">
            <div className="empty-state-icon">📋</div>
            <h3>No reports yet</h3>
            <p>Generate a report after running a ranking analysis</p>
          </div>
        )}

        {/* View Report Modal */}
        {viewReport && (
          <div className="modal-overlay" onClick={() => setViewReport(null)}>
            <div className="modal" style={{ maxWidth: "700px", maxHeight: "80vh", overflowY: "auto" }} onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <span className="modal-title">📋 {viewReport.job?.title} — Rankings Report</span>
                <button className="modal-close" onClick={() => setViewReport(null)}>✕</button>
              </div>
              <div style={{ marginBottom: "16px", display: "flex", gap: "12px" }}>
                <span className="badge badge-teal">Total: {viewReport.total_candidates}</span>
                <span className="badge badge-purple">Avg: {viewReport.summary?.average_score}%</span>
                <span className="badge badge-green">Top: {viewReport.summary?.top_candidate}</span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {(viewReport.rankings || []).map((r) => (
                  <div key={r.rank} style={{ background: "var(--glass-bg)", borderRadius: "var(--radius-md)", padding: "14px", border: "1px solid var(--glass-border)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                      <div style={{ fontWeight: 600 }}>#{r.rank} {r.candidate_name}</div>
                      <span className={`badge ${r.overall_score >= 75 ? "badge-green" : r.overall_score >= 50 ? "badge-amber" : "badge-red"}`}>
                        {r.overall_score}%
                      </span>
                    </div>
                    <div style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>{r.explanation}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
