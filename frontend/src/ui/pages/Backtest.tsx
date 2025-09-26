import { useState } from "react";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { Line } from "react-chartjs-2";
import { useUiStore } from "../../utils/store";
import { api } from "../../utils/http";

export default function Backtest() {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1m");
  const [curve, setCurve] = useState<{ ts: number; equity: number }[]>([]);
  const password = useUiStore(s => s.password);

  const run = async () => {
    const res = await api.post<{ equity_curve: { ts: number; equity: number }[] }>("/api/backtest", { symbol, timeframe, start: new Date(Date.now() - 7*24*60*60*1000).toISOString() }, { headers: { "X-API-Password": password! } });
    setCurve(res.data.equity_curve);
  };

  const data = {
    labels: curve.map(p => p.ts),
    datasets: [{ label: "Equity", data: curve.map(p => p.equity), borderColor: "#66bb6a" }]
  };

  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Stack direction="row" spacing={2}>
          <TextField label="Symbol" value={symbol} onChange={e => setSymbol(e.target.value)} />
          <TextField label="Timeframe" value={timeframe} onChange={e => setTimeframe(e.target.value)} />
          <Button variant="contained" onClick={run}>Run Backtest</Button>
        </Stack>
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Results</Typography>
        <Line data={data as any} />
      </Paper>
    </Stack>
  );
}
