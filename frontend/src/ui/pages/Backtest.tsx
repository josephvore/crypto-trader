import { useMemo, useState } from "react";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, TimeScale } from "chart.js";
import "chartjs-adapter-date-fns";
import { useUiStore } from "../../utils/store";
import { api } from "../../utils/http";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, TimeScale);

export default function Backtest() {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1m");
  const [curve, setCurve] = useState<{ ts: number; equity: number }[]>([]);
  const password = useUiStore(s => s.password);

  const run = async () => {
    const res = await api.post<{ equity_curve: { ts: number; equity: number }[] }>(
      "/api/backtest",
      { symbol, timeframe, start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() }
    );
    setCurve(res.data.equity_curve);
  };

  const chartData = useMemo(() => {
    return {
      datasets: [
        {
          label: "Equity",
          data: curve.map(p => ({ x: p.ts, y: p.equity })),
          borderColor: "#66bb6a",
          backgroundColor: "rgba(102,187,106,0.2)",
          pointRadius: 0,
          tension: 0.1
        }
      ]
    };
  }, [curve]);

  const options = useMemo(() => {
    return {
      responsive: true,
      maintainAspectRatio: false,
      parsing: false,
      scales: {
        x: {
          type: "time" as const,
          time: { unit: "minute" as const }
        },
        y: {
          ticks: { callback: (v: any) => `${v}` }
        }
      },
      interaction: { mode: "index" as const, intersect: false }
    };
  }, []);

  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Stack direction="row" spacing={2}>
          <TextField label="Symbol" value={symbol} onChange={e => setSymbol(e.target.value)} />
          <TextField label="Timeframe" value={timeframe} onChange={e => setTimeframe(e.target.value)} />
          <Button variant="contained" onClick={run}>Run Backtest</Button>
        </Stack>
      </Paper>
      <Paper sx={{ p: 2, height: 360 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Results</Typography>
        <div style={{ height: 300 }}>
          <Line key="equity-chart" data={chartData as any} options={options as any} redraw />
        </div>
      </Paper>
    </Stack>
  );
}
