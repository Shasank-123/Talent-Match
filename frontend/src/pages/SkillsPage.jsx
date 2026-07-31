import { useEffect, useState } from "react";
import { getSkills, extractSkills } from "../api";
import toast from "react-hot-toast";
import { Search, Zap } from "lucide-react";

export default function SkillsPage() {
  const [skillList, setSkillList] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [extractText, setExtractText] = useState("");
  const [extractedSkills, setExtractedSkills] = useState([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [tab, setTab] = useState("browse");

  useEffect(() => {
    getSkills()
      .then((res) => setSkillList(res.data.payload.skillList))
      .catch(() => toast.error("Failed to load skills"));
  }, []);

  const handleExtract = async () => {
    if (!extractText.trim()) { toast.error("Enter some text"); return; }
    setIsExtracting(true);
    try {
      const res = await extractSkills(extractText);
      setExtractedSkills(res.data.payload.skillList);
      if (res.data.payload.skillList.length === 0) {
        toast("No recognized skills found", { icon: "ℹ️" });
      }
    } catch {
      toast.error("Extraction failed");
    } finally {
      setIsExtracting(false);
    }
  };

  const filtered = skillList.filter((s) =>
    s.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const categories = {
    "Programming Languages": ["python", "javascript", "java", "c++", "c#", "typescript", "go", "rust", "ruby", "php"],
    "Frontend": ["react", "vue", "angular", "next.js", "html", "css"],
    "Backend": ["node.js", "express", "django", "fastapi", "flask", "spring", "laravel", "rails", "asp.net"],
    "Databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "sqlite"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "jenkins", "github actions"],
    "AI/ML": ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn"],
  };

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Skills</h1>
        <p className="page-subtitle">Browse known skills and extract them from text</p>
      </div>

      <div className="page-body">
        <div className="tabs mb-6">
          <button className={`tab ${tab === "browse" ? "active" : ""}`} onClick={() => setTab("browse")}>Browse Skills</button>
          <button className={`tab ${tab === "extract" ? "active" : ""}`} onClick={() => setTab("extract")}>Extract from Text</button>
        </div>

        {tab === "browse" && (
          <>
            <div className="form-group mb-6" style={{ maxWidth: "400px" }}>
              <div style={{ position: "relative" }}>
                <Search size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input
                  id="skill-search"
                  className="form-input"
                  placeholder="Search skills..."
                  style={{ paddingLeft: "38px" }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {searchTerm ? (
              <div>
                <div style={{ marginBottom: "12px", fontSize: "13px", color: "var(--text-secondary)" }}>
                  {filtered.length} result{filtered.length !== 1 ? "s" : ""}
                </div>
                <div className="skill-tags">
                  {filtered.map((s) => <span key={s} className="skill-tag">{s}</span>)}
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                {Object.entries(categories).map(([cat, catSkills]) => (
                  <div key={cat} className="card">
                    <div style={{ fontWeight: 600, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ fontSize: "16px" }}>
                        {cat === "Programming Languages" ? "💻" : cat === "Frontend" ? "🎨" : cat === "Backend" ? "⚙️" : cat === "Databases" ? "🗄️" : cat === "Cloud & DevOps" ? "☁️" : "🤖"}
                      </span>
                      {cat}
                    </div>
                    <div className="skill-tags">
                      {catSkills.map((s) => <span key={s} className="skill-tag">{s}</span>)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {tab === "extract" && (
          <div className="card">
            <div style={{ fontWeight: 600, marginBottom: "16px" }}>Paste resume or job description text:</div>
            <textarea
              id="extract-text"
              className="form-input form-textarea"
              placeholder="Paste any text here and we'll extract recognized technical skills..."
              style={{ minHeight: "160px", marginBottom: "12px" }}
              value={extractText}
              onChange={(e) => setExtractText(e.target.value)}
            />
            <button
              id="extract-btn"
              className="btn btn-primary"
              onClick={handleExtract}
              disabled={isExtracting}
            >
              {isExtracting ? <><div className="spinner spinner-sm" /> Extracting…</> : <><Zap size={15} /> Extract Skills</>}
            </button>

            {extractedSkills.length > 0 && (
              <div style={{ marginTop: "24px" }}>
                <div style={{ fontWeight: 600, marginBottom: "10px" }}>
                  Found {extractedSkills.length} skill{extractedSkills.length !== 1 ? "s" : ""}:
                </div>
                <div className="skill-tags">
                  {extractedSkills.map((s) => (
                    <span key={s} className="skill-tag skill-tag-match">{s}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
