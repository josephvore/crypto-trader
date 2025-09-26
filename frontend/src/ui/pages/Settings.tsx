import { useEffect, useState } from "react";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { api } from "../../utils/http";
import { useUiStore } from "../../utils/store";

export default function Settings() {
  const password = useUiStore(s => s.password);
  const [env, setEnv] = useState("");
  const [log, setLog] = useState("INFO");
  const [apiHost, setApiHost] = useState("0.0.0.0");
  const [apiPort, setApiPort] = useState(8080);

  const load = async () => {
    const res = await api.get<any>("/api/config/settings", { headers: { "X-API-Password": password! } });
    setEnv(res.data.env); setLog(res.data.log_level); setApiHost(res.data.api_host); setApiPort(res.data.api_port);
  };

  useEffect(() => { load(); }, []);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>System Settings</Typography>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <TextField label="Env" value={env} onChange={e => setEnv(e.target.value)} />
        <TextField label="Log Level" value={log} onChange={e => setLog(e.target.value)} />
        <TextField label="API Host" value={apiHost} onChange={e => setApiHost(e.target.value)} />
        <TextField label="API Port" type="number" value={apiPort} onChange={e => setApiPort(Number(e.target.value))} />
      </Stack>
      <Button variant="contained" onClick={load}>Reload</Button>
    </Paper>
  );
}
