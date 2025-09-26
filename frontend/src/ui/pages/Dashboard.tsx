import Grid from "@mui/material/Grid2";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { Line } from "react-chartjs-2";
import { Chart, LineElement, LinearScale, PointElement, TimeScale, Tooltip, Legend } from "chart.js";
import "chartjs-adapter-date-fns";
import { useRealtimeStore } from "../../utils/store";

Chart.register(LineElement, LinearScale, PointElement, TimeScale, Tooltip, Legend);

export default function Dashboard() {
  const equity = useRealtimeStore(s => s.equity);
  const data = {
    labels: equity.map(p => p.ts),
    datasets: [
      {
        label: "Equity",
        data: equity.map(p => p.equity),
        borderColor: "#42a5f5",
        backgroundColor: "rgba(66,165,245,0.2)"
      }
    ]
  };
  const options = {
    responsive: true,
    parsing: false,
    scales: {
      x: { type: "time" as const, time: { unit: "minute" as const } },
      y: { beginAtZero: false }
    }
  };

  return (
    <Grid container spacing={2}>
      <Grid size={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Equity Curve</Typography>
          <Line data={data as any} options={options as any} />
        </Paper>
      </Grid>
    </Grid>
  );
}
