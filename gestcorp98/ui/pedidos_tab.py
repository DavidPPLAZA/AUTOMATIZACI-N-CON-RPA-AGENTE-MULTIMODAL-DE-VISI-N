import tkinter as tk
from tkinter import messagebox, ttk

from gestcorp98 import database

COLUMNS = ("cliente", "producto", "cantidad", "total", "fecha", "estado")
HEADERS = {
    "cliente": "Cliente",
    "producto": "Producto",
    "cantidad": "Cantidad",
    "total": "Total (€)",
    "fecha": "Fecha",
    "estado": "Estado",
}


class PedidosTab(ttk.Frame):
    def __init__(self, master, conn):
        super().__init__(master)
        self._conn = conn
        self._clientes = []
        self._productos = []
        self._build()
        self._load_combos()
        self._refresh()

    def _build(self) -> None:
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=10)
        for col in COLUMNS:
            self.tree.heading(col, text=HEADERS[col])
            self.tree.column(col, width=130)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # clic derecho sobre una fila -> menu "Eliminar" (emergente, no mueve nada)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="✖ Eliminar pedido", command=self._delete_pedido)
        self.tree.bind("<Button-3>", self._show_menu)
        # recargar la tabla al entrar en la pestana: si se borro un cliente en
        # la pestana Clientes, sus pedidos ya no existen
        self.bind("<Map>", lambda _event: self._refresh())

        form = ttk.LabelFrame(self, text="Nuevo pedido")
        form.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Label(form, text="Cliente:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        # postcommand: se ejecuta justo antes de desplegar la lista, para que
        # aparezcan los clientes dados de alta despues de arrancar la app
        self.cliente_combo = ttk.Combobox(
            form, state="readonly", width=28, postcommand=self._load_combos
        )
        self.cliente_combo.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Producto:").grid(row=0, column=2, sticky="e", padx=4, pady=4)
        self.producto_combo = ttk.Combobox(
            form, state="readonly", width=28, postcommand=self._load_combos
        )
        self.producto_combo.grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(form, text="Cantidad:").grid(row=0, column=4, sticky="e", padx=4, pady=4)
        self.cantidad_entry = ttk.Entry(form, width=6)
        self.cantidad_entry.insert(0, "1")
        self.cantidad_entry.grid(row=0, column=5, padx=4, pady=4)

        ttk.Button(form, text="Crear pedido", command=self._add_pedido).grid(
            row=1, column=0, columnspan=6, pady=8
        )

    def _load_combos(self) -> None:
        self._clientes = database.list_clientes(self._conn)
        self._productos = database.list_productos(self._conn)
        self.cliente_combo["values"] = [c["nombre"] for c in self._clientes]
        self.producto_combo["values"] = [p["nombre"] for p in self._productos]

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for pedido in database.list_pedidos(self._conn):
            self.tree.insert(
                "", "end",
                iid=str(pedido["id"]),  # id de la BD, para saber que borrar
                values=(
                    pedido["cliente_nombre"], pedido["producto_nombre"], pedido["cantidad"],
                    f"{pedido['total']:.2f}", pedido["fecha"], pedido["estado"],
                ),
            )

    def _show_menu(self, event) -> None:
        fila = self.tree.identify_row(event.y)
        if not fila:
            return  # clic fuera de las filas (cabecera o hueco vacio)
        self.tree.selection_set(fila)
        self.menu.tk_popup(event.x_root, event.y_root)

    def _delete_pedido(self) -> None:
        seleccion = self.tree.selection()
        if not seleccion:
            return
        cliente, producto, cantidad = self.tree.item(seleccion[0], "values")[:3]
        if messagebox.askyesno(
            "Eliminar pedido", f"¿Eliminar el pedido de {cliente}: {cantidad} x {producto}?"
        ):
            database.delete_pedido(self._conn, int(seleccion[0]))
            self._refresh()

    def _add_pedido(self) -> None:
        if not self.cliente_combo.get() or not self.producto_combo.get():
            messagebox.showwarning("Datos incompletos", "Selecciona cliente y producto.")
            return

        try:
            cantidad = int(self.cantidad_entry.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "La cantidad debe ser un número entero positivo.")
            return

        cliente_id = self._clientes[self.cliente_combo.current()]["id"]
        producto_id = self._productos[self.producto_combo.current()]["id"]
        database.insert_pedido(self._conn, cliente_id=cliente_id, producto_id=producto_id, cantidad=cantidad)

        self.cantidad_entry.delete(0, "end")
        self.cantidad_entry.insert(0, "1")
        self._refresh()
