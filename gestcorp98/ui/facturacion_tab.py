from tkinter import ttk

from gestcorp98 import database

COLUMNS = ("numero", "cliente", "fecha", "total", "estado")
HEADERS = {
    "numero": "Nº Factura",
    "cliente": "Cliente",
    "fecha": "Fecha",
    "total": "Total (€)",
    "estado": "Estado",
}


class FacturacionTab(ttk.Frame):
    def __init__(self, master, conn):
        super().__init__(master)
        self._conn = conn
        self._build()
        self._refresh()

    def _build(self) -> None:
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=14)
        for col in COLUMNS:
            self.tree.heading(col, text=HEADERS[col])
            self.tree.column(col, width=140)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Button(self, text="Actualizar", command=self._refresh).pack(pady=(0, 8))

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for factura in database.list_facturas(self._conn):
            self.tree.insert(
                "", "end",
                values=(
                    factura["numero"], factura["cliente_nombre"], factura["fecha"],
                    f"{factura['total']:.2f}", factura["estado"],
                ),
            )
