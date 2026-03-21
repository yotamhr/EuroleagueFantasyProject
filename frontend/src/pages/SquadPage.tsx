import { useState } from "react";
import { getBreakdown } from "../api/client";

type Contribution = {
  player_id: number;
  name: string;
  position_slot: string;
  role: string;
  raw_fantasy_points: number;
  multiplier: number;
  contributed_points: number;
  note: string;
};

type Breakdown = {
  round: number;
  contributions: Contribution[];
  coach: { coach_id: number; name: string; fantasy_points: number };
  total_fantasy_points: number;
};

export default function SquadPage() {
  const [round, setRound] = useState(1);
  const [breakdown, setBreakdown] = useState<Breakdown | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadBreakdown = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getBreakdown(round);
      setBreakdown(data);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(`Could not load breakdown: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const roleColor = (role: string) => {
    if (role.includes("starter")) return "#e8f4fd";
    if (role.includes("auto-sub")) return "#fff3cd";
    if (role.includes("bench")) return "#f0f0f0";
    return "#fff";
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Squad Breakdown</h2>

      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 16 }}>
        <label>
          Round:&nbsp;
          <input
            type="number"
            min={1}
            value={round}
            onChange={(e) => setRound(Number(e.target.value))}
            style={{ width: 60 }}
          />
        </label>
        <button onClick={loadBreakdown} disabled={loading}>
          {loading ? "Loading…" : "Load Breakdown"}
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {breakdown && (
        <>
          <h3>Round {breakdown.round} — Total: {breakdown.total_fantasy_points} pts</h3>

          <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
            <thead>
              <tr style={{ background: "#1a1a2e", color: "#fff" }}>
                <th style={{ padding: "6px 10px", textAlign: "left" }}>Player</th>
                <th style={{ padding: "6px 10px" }}>Pos</th>
                <th style={{ padding: "6px 10px", textAlign: "left" }}>Role</th>
                <th style={{ padding: "6px 10px", textAlign: "right" }}>Raw FP</th>
                <th style={{ padding: "6px 10px", textAlign: "right" }}>×</th>
                <th style={{ padding: "6px 10px", textAlign: "right" }}>Contributed</th>
                <th style={{ padding: "6px 10px", textAlign: "left" }}>Note</th>
              </tr>
            </thead>
            <tbody>
              {breakdown.contributions.map((c, i) => (
                <tr key={i} style={{ background: roleColor(c.role) }}>
                  <td style={{ padding: "5px 10px" }}>{c.name}</td>
                  <td style={{ padding: "5px 10px", textAlign: "center" }}>{c.position_slot}</td>
                  <td style={{ padding: "5px 10px" }}>{c.role}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{c.raw_fantasy_points}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{c.multiplier}x</td>
                  <td style={{ padding: "5px 10px", textAlign: "right", fontWeight: "bold" }}>
                    {c.contributed_points}
                  </td>
                  <td style={{ padding: "5px 10px", color: "#666", fontStyle: "italic" }}>{c.note}</td>
                </tr>
              ))}
              {/* Coach row */}
              <tr style={{ background: "#e8f5e9" }}>
                <td style={{ padding: "5px 10px" }}>{breakdown.coach.name}</td>
                <td style={{ padding: "5px 10px", textAlign: "center" }}>—</td>
                <td style={{ padding: "5px 10px" }}>coach</td>
                <td style={{ padding: "5px 10px", textAlign: "right" }}>{breakdown.coach.fantasy_points}</td>
                <td style={{ padding: "5px 10px", textAlign: "right" }}>1x</td>
                <td style={{ padding: "5px 10px", textAlign: "right", fontWeight: "bold" }}>
                  {breakdown.coach.fantasy_points}
                </td>
                <td style={{ padding: "5px 10px" }}></td>
              </tr>
              {/* Total row */}
              <tr style={{ background: "#1a1a2e", color: "#fff", fontWeight: "bold" }}>
                <td colSpan={5} style={{ padding: "6px 10px", textAlign: "right" }}>TOTAL</td>
                <td style={{ padding: "6px 10px", textAlign: "right" }}>
                  {breakdown.total_fantasy_points}
                </td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
