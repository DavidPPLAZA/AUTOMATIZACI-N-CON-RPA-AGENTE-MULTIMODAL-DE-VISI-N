import { Suspense } from "react";
import DetalleRobot from "@/components/DetalleRobot";

// El id del robot solo se conoce al pedir la pagina: la parte que lo lee va
// dentro de Suspense (lo exige Next con cacheComponents activado).
export default function Page() {
  return (
    <Suspense fallback={<div className="mx-auto h-40 w-full max-w-3xl animate-pulse rounded-2xl bg-panel" />}>
      <DetalleRobot />
    </Suspense>
  );
}
