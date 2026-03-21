import { useState } from "react";
import { fetchRoundStats, getRoundStats } from "../api/client";

type PlayerStat = {
  player_name: string;
  team_code: string;
  minutes_played: string;
  points: number;
  rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;
  fouls_drawn: number;
  fouls_committed: number;
  fantasy_points: number;
};

type SortKey = keyof PlayerStat;

export default function StatsPage() {
  const [round, setRound] = useState(1);
  const [players, setPlayers] = useState<PlayerStat[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("fantasy_points");
  const [sortAsc, setSortAsc] = useState(false);

  const handleFetch = async () => {
    setLoading(true);
    setError("");
    try {
      await fetchRoundStats(round);
      const data = await getRoundStats(round);
      setPlayers(data.players);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(`Failed to fetch stats: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getRoundStats(round);
      setPlayers(data.players);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(`Could not load stats. Try fetching first. (${msg})`);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  };

  const sorted = [...players].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (typeof av === "number" && typeof bv === "number") {
      return sortAsc ? av - bv : bv - av;
    }
    return sortAsc
      ? String(av).localeCompare(String(bv))
      : String(bv).localeCompare(String(av));
  });

  const col = (label: string, key: SortKey) => (
    <th
      onClick={() => handleSort(key)}
      style={{ cursor: "pointer", userSelect: "none", padding: "6px 10px" }}
    >
      {label} {sortKey === key ? (sortAsc ? "▲" : "▼") : ""}
    </th>
  );

  return (
    <div style={{ padding: 24 }}>
      <h2>Round Stats</h2>

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
        <button onClick={handleFetch} disabled={loading}>
          {loading ? "Loading…" : "Fetch from API"}
        </button>
        <button onClick={handleLoad} disabled={loading}>
          Load saved
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {sorted.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
            <thead>
              <tr style={{ background: "#1a1a2e", color: "#fff" }}>
                {col("Player", "player_name")}
                {col("Team", "team_code")}
                {col("Min", "minutes_played")}
                {col("PTS", "points")}
                {col("REB", "rebounds")}
                {col("AST", "assists")}
                {col("STL", "steals")}
                {col("BLK", "blocks")}
                {col("TO", "turnovers")}
                {col("FD", "fouls_drawn")}
                {col("FC", "fouls_committed")}
                {col("FP", "fantasy_points")}
              </tr>
            </thead>
            <tbody>
              {sorted.map((p, i) => (
                <tr
                  key={i}
                  style={{ background: i % 2 === 0 ? "#f9f9f9" : "#fff" }}
                >
                  <td style={{ padding: "5px 10px" }}>{p.player_name}</td>
                  <td style={{ padding: "5px 10px" }}>{p.team_code}</td>
                  <td style={{ padding: "5px 10px" }}>{p.minutes_played}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.points}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.rebounds}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.assists}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.steals}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.blocks}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.turnovers}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.fouls_drawn}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right" }}>{p.fouls_committed}</td>
                  <td style={{ padding: "5px 10px", textAlign: "right", fontWeight: "bold" }}>
                    {p.fantasy_points}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
