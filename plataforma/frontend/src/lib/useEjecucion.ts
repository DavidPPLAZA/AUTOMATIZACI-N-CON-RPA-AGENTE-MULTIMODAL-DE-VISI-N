"use client";

import { useEffect, useState } from "react";
import { WS, type Evento } from "./api";

// Se suscribe al stream de una ejecucion y acumula sus eventos.
// El backend manda primero lo que ya paso y luego lo nuevo en tiempo real.
export function useEjecucion(id: string | null) {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [conectado, setConectado] = useState(false);

  useEffect(() => {
    // el panel se monta con key=id, asi que cada ejecucion empieza con estado limpio
    if (!id) return;
    const ws = new WebSocket(`${WS}/ws/ejecuciones/${id}`);
    ws.onopen = () => setConectado(true);
    ws.onclose = () => setConectado(false);
    ws.onmessage = (m) => setEventos((prev) => [...prev, JSON.parse(m.data) as Evento]);
    return () => ws.close();
  }, [id]);

  const fin = eventos.find((e) => e.tipo === "fin");
  return {
    eventos,
    conectado,
    terminada: Boolean(fin),
    estadoFinal: fin && fin.tipo === "fin" ? fin.estado : null,
  };
}
