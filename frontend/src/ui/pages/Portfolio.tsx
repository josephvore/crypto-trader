import { useEffect, useState } from "react";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Stack from "@mui/material/Stack";
import { api } from "../../utils/http";
import { useUiStore } from "../../utils/store";

type Position = { exchange: string; symbol: string; qty: number; avg_price: number; realized_pnl: number; updated_at: string; };
type Portfolio = { cash: number; positions_value: number; equity: number; realized_pnl: number; };

export default function Portfolio() {
  const password = useUiStore(s => s.password);
  const [positions, setPositions] = useState<Position[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);

  const load = async () => {
    const [pos, port] = await Promise.all([
      api.get<Position[]>("/api/positions", { headers: { "X-API-Password": password! } }),
      api.get<Portfolio>("/api/portfolio", { headers: { "X-API-Password": password! } })
    ]);
    setPositions(pos.data);
    setPortfolio(port.data);
  };

  useEffect(() => { load(); }, []);

  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Portfolio Summary</Typography>
        {portfolio && <Typography variant="body2">Cash: {portfolio.cash.toFixed(2)} | Positions: {portfolio.positions_value.toFixed(2)} | Equity: {portfolio.equity.toFixed(2)} | Realized PnL: {portfolio.realized_pnl.toFixed(2)}</Typography>}
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Positions</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell><TableCell>Qty</TableCell><TableCell>Avg Price</TableCell><TableCell>Realized PnL</TableCell><TableCell>Updated</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {positions.map(p => (
              <TableRow key={p.symbol}>
                <TableCell>{p.symbol}</TableCell><TableCell>{p.qty}</TableCell><TableCell>{p.avg_price}</TableCell><TableCell>{p.realized_pnl}</TableCell><TableCell>{new Date(p.updated_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Stack>
  );
}
