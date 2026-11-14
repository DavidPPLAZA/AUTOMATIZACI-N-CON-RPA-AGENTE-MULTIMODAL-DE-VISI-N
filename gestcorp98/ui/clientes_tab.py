import tkinter as tk
from tkinter import messagebox, ttk

from gestcorp98 import database

COLUMNS = ("nombre", "nif", "email", "telefono", "ciudad", "fecha_alta")
HEADERS = {
    "nombre": "Nombre",
    "nif": "NIF",
    "email": "Email",
    "telefono": "Teléfono",
    "ciudad": "Ciudad",
    "fecha_alta": "Fecha alta",
}
FIELDS = [
    ("nombre", "Nombre"),
    ("nif", "NIF"),
    ("email", "Email"),
    ("telefono", "Teléfono"),
    ("ciudad", "Ciudad"),
]


class ClientesTab(ttk.Frame):
    def __init__(self, master, conn):
        super().__init__(master)
        self._conn = conn
        self.entries: dict[str, tk.Entry] = {}
        self._build()
        self._refresh()

    def _build(self) -> None:
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=10)
        for col in COLUMNS:
            self.tree.heading(col, text=HEADERS[col])
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(self, text="Alta de cliente")
        form.pack(fill="x", padx=8, pady=(0, 8))

        for i, (key, label) in enumerate(FIELDS):
            row, col = divmod(i, 3)
            ttk.Label(form, text=f"{label}:").grid(row=row, column=col * 2, sticky="e", padx=4, pady=4)
            entry = ttk.Entry(form, width=22)
            entry.grid(row=row, column=col * 2 + 1, sticky="w", padx=4, pady=4)
            self.entries[key] = entry

        ttk.Button(form, text="Añadir cliente", command=self._add_cliente).grid(
            row=2, column=0, columnspan=6, pady=8
        )

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for cliente in database.list_clientes(self._conn):
            self.tree.insert(
                "", "end",
                values=(
                    cliente["nombre"], cliente["nif"], cliente["email"],
                    cliente["telefono"], cliente["ciudad"], cliente["fecha_alta"],
                ),
            )

    def _add_cliente(self) -> None:
        nombre = self.entries["nombre"].get().strip()
        nif = self.entries["nif"].get().strip()
        if not nombre or not nif:
            messagebox.showwarning("Datos incompletos", "Nombre y NIF son obligatorios.")
            return

        database.insert_cliente(
            self._conn,
            nombre=nombre,
            nif=nif,
            email=self.entries["email"].get().strip(),
            telefono=self.entries["telefono"].get().strip(),
            ciudad=self.entries["ciudad"].get().strip(),
        )
        for entry in self.entries.values():
            entry.delete(0, "end")
        self._refresh()
