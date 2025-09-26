import { create } from "zustand";

type UiState = {
  tab: "Dashboard" | "Orders" | "Portfolio" | "Backtest" | "Settings";
  setTab: (t: UiState["tab"]) => void;
  password: string | null;
  setPassword: (p: string) => void;
};

export const useUiStore = create<UiState>((set) => ({
  tab: "Dashboard",
  setTab: (t) => set({ tab: t }),
  password: null,
  setPassword: (p) => set({ password: p })
}));

type EquityPoint = { ts: number; equity: number };

type RealtimeState = {
  equity: EquityPoint[];
  setEquity: (pts: EquityPoint[]) => void;
};

export const useRealtimeStore = create<RealtimeState>((set) => ({
  equity: [],
  setEquity: (pts) => set({ equity: pts })
}));
