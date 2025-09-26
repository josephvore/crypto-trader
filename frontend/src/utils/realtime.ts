import { useCallback, useEffect, useRef, useState } from "react";
import { API_BASE } from "./http";
import { useRealtimeStore, useUiStore } from "./store";

export function useRealtime() {
  const password = useUiStore(s => s.password);
  const setEquity = useRealtimeStore(s => s.setEquity);
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<"disconnected"|"connecting"|"connected">("disconnected");

  const connect = useCallback(() => {
    if (!password || wsRef.current) return;
    setStatus("connecting");
    const url = API_BASE.replace(/^http/, "ws") + `/ws?token=${encodeURIComponent(password)}`;
    const ws = new WebSocket(url);
    ws.onopen = () => setStatus("connected");
    ws.onclose = () => { setStatus("disconnected"); wsRef.current = null; };
    ws.onerror = () => { /* ignore */ };
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.event === "equity") {
          setEquity(msg.payload.points);
        }
      } catch { /* ignore */ }
    };
    wsRef.current = ws;
  }, [password]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setStatus("disconnected");
  }, []);

  useEffect(() => () => disconnect(), []);

  return { status, connect, disconnect };
}
