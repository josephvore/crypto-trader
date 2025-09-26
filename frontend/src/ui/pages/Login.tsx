import { useState } from "react";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useUiStore } from "../../utils/store";

export default function Login() {
  const [pwd, setPwd] = useState("");
  const setPassword = useUiStore(s => s.setPassword);

  return (
    <Container maxWidth="sm" sx={{ mt: 12 }}>
      <Paper sx={{ p: 4 }}>
        <Stack spacing={2}>
          <Typography variant="h5">Enter API Password</Typography>
          <TextField
            type="password"
            label="API Password"
            value={pwd}
            onChange={e => setPwd(e.target.value)}
            fullWidth
          />
          <Button variant="contained" onClick={() => setPassword(pwd)} disabled={!pwd}>
            Continue
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
}
