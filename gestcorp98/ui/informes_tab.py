from tkinter import ttk

from gestcorp98 import database

ROWS = [
    ("total_clientes", "Clientes registrados:"),
    ("pedidos_pendientes", "Pedidos pendientes:"),
    ("total_facturado", "Total facturado (€):"),
]


class InformesTab(ttk.Frame):
    def __init__(self, master, conn):
        super().__init__(master)
        self._conn = conn
        self._labels: dict[str, ttk.Label] = {}
        self._build()
        self._refresh()

    def _build(self) -> None:
        box = ttk.LabelFrame(self, text="Resumen comercial")
        box.pack(fill="x", padx=12, pady=12)

        for i, (key, label) in enumerate(ROWS):
            ttk.Label(box, text=label, font=("", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=8
            )
            value_label = ttk.Label(box, text="-")
            value_label.grid(row=i, column=1, sticky="w", padx=10, pady=8)
            self._labels[key] = value_label

        ttk.Button(self, text="Actualizar informe", command=self._refresh).pack(pady=8)

    def _refresh(self) -> None:
        stats = database.get_informe_stats(self._conn)
        self._labels["total_clientes"].config(text=str(stats["total_clientes"]))
        self._labels["pedidos_pendientes"].config(text=str(stats["pedidos_pendientes"]))
        self._labels["total_facturado"].config(text=f"{stats['total_facturado']:.2f}")
