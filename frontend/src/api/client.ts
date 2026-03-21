import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

// --- Players ---
export const getPlayers = (params?: { position?: string; team?: string; search?: string }) =>
  api.get("/players", { params }).then((r) => r.data);

export const getCoaches = () => api.get("/coaches").then((r) => r.data);

// --- Stats ---
export const fetchRoundStats = (round: number) =>
  api.post(`/stats/fetch/${round}`).then((r) => r.data);

export const getRoundStats = (round: number) =>
  api.get(`/stats/round/${round}`).then((r) => r.data);

// --- Squad ---
export const getSquad = (round: number) =>
  api.get(`/squad/${round}`).then((r) => r.data);

export const saveSquad = (round: number, squad: object) =>
  api.put(`/squad/${round}`, squad).then((r) => r.data);

export const getBreakdown = (round: number) =>
  api.get(`/squad/${round}/breakdown`).then((r) => r.data);
