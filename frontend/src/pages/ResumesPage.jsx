import { useEffect, useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { getResumes, uploadResume, deleteResume } from "../api";
import toast from "react-hot-toast";
import { Upload, Trash2, RefreshCw, Eye } from "lucide-react";

export default function ResumesPage() {
  const [resumeList, setResumeList] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchResumes = () => {
    setLoading(true);
    getResumes()
      .then((res) => setResumeList(res.data.payload.resumeList))
      .catch(() => toast.error("Failed to load resumes"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchResumes(); }, []);

  const onDrop = useCallback(async (files) => {
    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);
      setIsUploading(true);
      try {
        await uploadResume(formData);
        toast.success(`${file.name} uploaded successfully!`);
      } catch (err) {
        const msg = err.response?.data?.detail?.error_detail || "Upload failed";
        toast.error(msg);
      }
    }
    setIsUploading(false);
    fetchResumes();
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"], "text/plain": [".txt"] },
    multiple: true,
  });

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete resume for ${name}?`)) return;
    try {
      await deleteResume(id);
      toast.success("Resume deleted");
      fetchResumes();
    } catch {
      toast.error("Failed to delete");
    }
  };

  return (
    <>
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Resumes</h1>
            <p className="page-subtitle">Upload and manage candidate resumes</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={fetchResumes}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      <div className="page-body">
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`dropzone mb-6 ${isDragActive ? "active" : ""}`}
        >
          <input {...getInputProps()} id="resume-file-input" />
          <div className="dropzone-icon">{isUploading ? "⏳" : "📤"}</div>
          <div className="dropzone-title">
            {isUploading ? "Uploading..." : isDragActive ? "Drop files here" : "Drop resumes here or click to browse"}
          </div>
          <div className="dropzone-subtitle">Supports PDF, DOCX, TXT — up to 10MB each</div>
          {isUploading && <div className="spinner" style={{ margin: "16px auto 0" }} />}
        </div>

        {/* List */}
        {loading ? (
          <div className="flex items-center justify-between" style={{ gap: 12 }}>
            <div className="spinner" /><span style={{ color: "var(--text-secondary)" }}>Loading resumes...</span>
          </div>
        ) : resumeList.length === 0 ? (
          <div className="empty-state card">
            <div className="empty-state-icon">📄</div>
            <h3>No resumes yet</h3>
            <p>Upload candidate resumes to get started</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Candidate</th>
                  <th>Email</th>
                  <th>File</th>
                  <th>Skills</th>
                  <th>Exp.</th>
                  <th>Parsed</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {resumeList.map((r, i) => (
                  <tr key={r.id}>
                    <td style={{ color: "var(--text-muted)", fontSize: "13px" }}>{i + 1}</td>
                    <td style={{ fontWeight: 500 }}>{r.candidate_name || "—"}</td>
                    <td style={{ color: "var(--text-secondary)", fontSize: "13px" }}>{r.candidate_email || "—"}</td>
                    <td>
                      <span className="badge badge-gray">{r.file_type}</span>
                      <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "6px" }}>
                        {r.file_name?.length > 20 ? r.file_name.slice(0, 20) + "…" : r.file_name}
                      </span>
                    </td>
                    <td>
                      <div className="skill-tags" style={{ maxWidth: "200px" }}>
                        {(r.skills || []).slice(0, 3).map((s) => (
                          <span key={s} className="skill-tag">{s}</span>
                        ))}
                        {(r.skills || []).length > 3 && (
                          <span className="badge badge-gray">+{r.skills.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td>{r.experience_years > 0 ? `${r.experience_years} yr` : "—"}</td>
                    <td>
                      <span className={`badge ${r.is_parsed ? "badge-green" : "badge-amber"}`}>
                        {r.is_parsed ? "✓ Parsed" : "Pending"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(r.id, r.candidate_name)}
                        title="Delete resume"
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
