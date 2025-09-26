import { useEffect, useState } from "react";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { api } from "../../utils/http";
import { useUiStore } from "../../utils/store";

type Order = {
  id: number;
  client_order_id: string;
  symbol: string;
  side: "buy" | "sell";
  type: string;
  qty: number;
  price?: number | null;
  status: string;
};

export default function Orders() {
  const [rows, setRows] = useState<Order[]>([]);
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [qty, setQty] = useState(0.001);
  const [price, setPrice] = useState<number | "">("");
  const [side, setSide] = useState<"buy"|"sell">("buy");
  const password = useUiStore(s => s.password);

  const load = async () => {
    const res = await api.get<Order[]>("/api/orders", { headers: { "X-API-Password": password! } });
    setRows(res.data);
  };

  useEffect(() => { load(); }, []);

  const place = async () => {
    await api.post<Order>("/api/orders", { symbol, qty, side, type: price ? "limit" : "market", price: price || null }, { headers: { "X-API-Password": password! } });
    await load();
  };

  const cancel = async (id: number) => {
    await api.post<Order>(`/api/orders/${id}/cancel`, {}, { headers: { "X-API-Password": password! } });
    await load();
  };

  return (
    <Stack spacing={2}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Place Order</Typography>
        <Stack direction="row" spacing={2}>
          <TextField label="Symbol" value={symbol} onChange={e => setSymbol(e.target.value)} />
          <TextField label="Qty" type="number" value={qty} onChange={e => setQty(Number(e.target.value))} />
          <TextField label="Price (optional)" type="number" value={price} onChange={e => setPrice(e.target.value===""? "" : Number(e.target.value))} />
          <Button variant={side==="buy"?"contained":"outlined"} onClick={()=>setSide("buy")}>Buy</Button>
          <Button variant={side==="sell"?"contained":"outlined"} onClick={()=>setSide("sell")}>Sell</Button>
          <Button variant="contained" onClick={place}>Submit</Button>
        </Stack>
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Orders</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell><TableCell>Client ID</TableCell><TableCell>Symbol</TableCell><TableCell>Side</TableCell><TableCell>Type</TableCell><TableCell>Qty</TableCell><TableCell>Price</TableCell><TableCell>Status</TableCell><TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map(r => (
              <TableRow key={r.id}>
                <TableCell>{r.id}</TableCell><TableCell>{r.client_order_id}</TableCell><TableCell>{r.symbol}</TableCell><TableCell>{r.side}</TableCell><TableCell>{r.type}</TableCell><TableCell>{r.qty}</TableCell><TableCell>{r.price ?? "-"}</TableCell><TableCell>{r.status}</TableCell>
                <TableCell><Button size="small" onClick={() => cancel(r.id)}>Cancel</Button></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Stack>
  );
}
