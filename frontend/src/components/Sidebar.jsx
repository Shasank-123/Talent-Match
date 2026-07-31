import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard, FileText, Briefcase, TrendingUp,
  Lightbulb, BarChart3, FileOutput, BookOpen, LogOut
} from "lucide-react";

const navItems = [
  { to: "/dashboard", icon: <LayoutDashboard />, label: "Dashboard" },
  { to: "/resumes", icon: <FileText />, label: "Resumes" },
  { to: "/jobs", icon: <Briefcase />, label: "Jobs" },
  { to: "/rankings", icon: <TrendingUp />, label: "Rankings" },
  { to: "/skills", icon: <Lightbulb />, label: "Skills" },
  { to: "/interviews", icon: <BookOpen />, label: "Interviews" },
  { to: "/reports", icon: <FileOutput />, label: "Reports" },
  { to: "/analytics", icon: <BarChart3 />, label: "Analytics" },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🎯</div>
        <div className="sidebar-logo-text">
          <span>Talent</span>Match
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `sidebar-nav-item ${isActive ? "active" : ""}`
            }
          >
            {icon}
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">
            {user?.full_name?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user?.full_name || "User"}</div>
            <div className="sidebar-user-role">{user?.role || "recruiter"}</div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              background: "none",
              color: "var(--text-muted)",
              padding: "4px",
              borderRadius: "4px",
              display: "flex",
              alignItems: "center",
              transition: "var(--transition)",
            }}
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
