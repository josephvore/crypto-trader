import { useState } from "react";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import { useUiStore } from "../../utils/store";

export default function Login() {
  const [pwd, setPwd] = useState("");
  const [remember, setRemember] = useState(true);
  const setPassword = useUiStore(s => s.setPassword);

  const onSubmit = () => {
    setPassword(pwd);
    try {
      if (remember) {
        localStorage.setItem("ct_api_password", pwd);
      } else {
        localStorage.removeItem("ct_api_password");
      }
    } catch {
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 12 }}>
      <Paper sx={{ p: 4 }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <Stack spacing={2}>
            <Typography variant="h5">Enter API Password</Typography>
            <TextField
              type="password"
              label="API Password"
              value={pwd}
              onChange={e => setPwd(e.target.value)}
              fullWidth
            />
            <FormControlLabel
              control={<Checkbox checked={remember} onChange={(e) => setRemember(e.target.checked)} />}
              label="Remember me"
            />
            <Button type="submit" variant="contained" disabled={!pwd}>
              Continue
            </Button>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
}
