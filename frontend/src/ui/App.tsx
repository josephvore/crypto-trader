import { useEffect } from "react";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import AppBar from "@mui/material/AppBar";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Container from "@mui/material/Container";
import { useUiStore } from "../utils/store";
import Dashboard from "./pages/Dashboard";
import Orders from "./pages/Orders";
import Portfolio from "./pages/Portfolio";
import Settings from "./pages/Settings";
import Backtest from "./pages/Backtest";
import Login from "./pages/Login";
import { useRealtime } from "../utils/realtime";

const drawerWidth = 240;

export default function App() {
  const tab = useUiStore(s => s.tab);
  const setTab = useUiStore(s => s.setTab);
  const password = useUiStore(s => s.password);
  const { status, connect, disconnect } = useRealtime();

  useEffect(() => {
    if (password) connect();
    return () => disconnect();
  }, [password]);

  if (!password) return <Login />;

  return (
    <Box sx={{ display: "flex" }}>
      <AppBar position="fixed" sx={{ zIndex: theme => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Crypto Trader
          </Typography>
          <Typography variant="body2">WS: {status}</Typography>
        </Toolbar>
      </AppBar>
      <Drawer variant="permanent" sx={{ width: drawerWidth, [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: "border-box" } }}>
        <Toolbar />
        <Divider />
        <List>
          {["Dashboard","Orders","Portfolio","Backtest","Settings"].map((text, idx) => (
            <ListItem key={text} disablePadding>
              <ListItemButton selected={tab===text} onClick={() => setTab(text as any)}>
                <ListItemText primary={text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Container maxWidth="xl" sx={{ py: 2 }}>
          {tab==="Dashboard" && <Dashboard />}
          {tab==="Orders" && <Orders />}
          {tab==="Portfolio" && <Portfolio />}
          {tab==="Backtest" && <Backtest />}
          {tab==="Settings" && <Settings />}
        </Container>
      </Box>
    </Box>
  );
}
