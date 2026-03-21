import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import StatsPage from "./pages/StatsPage";
import SquadPage from "./pages/SquadPage";

const navStyle = ({ isActive }: { isActive: boolean }) => ({
  padding: "8px 16px",
  color: isActive ? "#fff" : "#aaa",
  textDecoration: "none",
  fontWeight: isActive ? "bold" : "normal",
  borderBottom: isActive ? "2px solid #fff" : "2px solid transparent",
});

export default function App() {
  return (
    <BrowserRouter>
      <header style={{ background: "#1a1a2e", color: "#fff", display: "flex", alignItems: "center", gap: 8, padding: "0 16px" }}>
        <span style={{ fontWeight: "bold", fontSize: 18, marginRight: 24, padding: "12px 0" }}>
          Euroleague Fantasy
        </span>
        <NavLink to="/" end style={navStyle}>Stats</NavLink>
        <NavLink to="/squad" style={navStyle}>My Squad</NavLink>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<StatsPage />} />
          <Route path="/squad" element={<SquadPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
