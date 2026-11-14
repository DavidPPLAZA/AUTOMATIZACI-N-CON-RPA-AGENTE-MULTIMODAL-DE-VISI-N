import tkinter as tk
from tkinter import ttk

from gestcorp98 import config
from gestcorp98.ui.clientes_tab import ClientesTab
from gestcorp98.ui.facturacion_tab import FacturacionTab
from gestcorp98.ui.informes_tab import InformesTab
from gestcorp98.ui.pedidos_tab import PedidosTab


class MainWindow(tk.Frame):
    def __init__(self, master, conn):
        super().__init__(master, bg=config.BG_COLOR)
        self._conn = conn
        self._build()

    def _build(self) -> None:
        title = tk.Label(
            self,
            text=config.APP_TITLE,
            bg=config.TITLE_BG,
            fg="white",
            font=(config.FONT_FAMILY, 11, "bold"),
            pady=6,
        )
        title.pack(fill="x")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)

        notebook.add(ClientesTab(notebook, self._conn), text="Clientes")
        notebook.add(PedidosTab(notebook, self._conn), text="Pedidos")
        notebook.add(FacturacionTab(notebook, self._conn), text="Facturación")
        notebook.add(InformesTab(notebook, self._conn), text="Informes")
