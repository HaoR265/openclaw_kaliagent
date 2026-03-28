import { NavLink, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";
import { CatalogPage } from "../pages/CatalogPage";
import { CampaignPage } from "../pages/CampaignPage";
import { CommandBoardPage } from "../pages/CommandBoardPage";
import { ExecutionPage } from "../pages/ExecutionPage";
import { IntelKnowledgePage } from "../pages/IntelKnowledgePage";
import { MissionPage } from "../pages/MissionPage";
import { ResearchPage } from "../pages/ResearchPage";
import { StatusBar } from "../components/StatusBar";
import { getOverview } from "../shared/api/client";

const links = [
  { to: "/", label: "Mission" },
  { to: "/execution", label: "Execution" },
  { to: "/campaigns", label: "Campaigns" },
  { to: "/command", label: "Command Board" },
  { to: "/research", label: "Research Studio" },
  { to: "/intel", label: "Intel / Knowledge" },
  { to: "/catalog", label: "Catalog" },
];

export function AppRouter() {
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    getOverview().then(setOverview).catch(console.error);
    const timer = window.setInterval(() => {
      getOverview().then(setOverview).catch(() => undefined);
    }, 15000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">K</div>
          <div>
            <div className="brand-title">OpenClaw</div>
            <div className="brand-sub">Command Board vNext</div>
          </div>
        </div>
        <nav className="nav">
          {links.map((link) => (
            <NavLink
              key={link.to}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
              to={link.to}
              end={link.to === "/"}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <StatusBar overview={overview} />
        <Routes>
          <Route path="/" element={<MissionPage />} />
          <Route path="/execution" element={<ExecutionPage />} />
          <Route path="/campaigns" element={<CampaignPage />} />
          <Route path="/command" element={<CommandBoardPage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/intel" element={<IntelKnowledgePage />} />
          <Route path="/catalog" element={<CatalogPage />} />
        </Routes>
      </main>
    </div>
  );
}
