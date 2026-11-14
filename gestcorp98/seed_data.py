import sqlite3
from datetime import date, timedelta

PRODUCTOS_DEMO = [
    ("Caja cartón reforzada", 3.50),
    ("Palet de madera estándar", 18.90),
    ("Rollo film retráctil", 12.25),
    ("Cinta adhesiva embalaje", 2.10),
    ("Flejadora manual", 45.00),
    ("Pallet plástico industrial", 62.75),
]

CLIENTES_DEMO = [
    ("Distribuciones Hermanos Ruiz S.L.", "B12345678", "pedidos@hermanosruiz.es", "956112233", "Jerez de la Frontera"),
    ("Almacenes del Sur S.A.", "A87654321", "compras@almacenesdelsur.es", "954223344", "Sevilla"),
    ("Suministros Industriales Levante", "B11223344", "info@suminlevante.es", "963334455", "Valencia"),
    ("Logística Castilla S.L.", "B55667788", "pedidos@logisticacastilla.es", "983445566", "Valladolid"),
    ("Comercial Norte Ibérica", "A99887766", "ventas@nortevica.es", "944556677", "Bilbao"),
]

# (cliente_id, producto_id, cantidad, días desde hoy, estado)
PEDIDOS_DEMO = [
    (1, 1, 20, 10, "Facturado"),
    (2, 2, 5, 8, "Facturado"),
    (3, 3, 12, 5, "Pendiente"),
    (4, 4, 3, 2, "Pendiente"),
    (1, 5, 2, 1, "Facturado"),
    (5, 6, 15, 0, "Pendiente"),
]


def seed_if_empty(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    if existing > 0:
        return

    for nombre, precio in PRODUCTOS_DEMO:
        conn.execute(
            "INSERT INTO productos (nombre, precio_unitario) VALUES (?, ?)", (nombre, precio)
        )

    hoy = date.today()
    for i, (nombre, nif, email, telefono, ciudad) in enumerate(CLIENTES_DEMO):
        fecha_alta = (hoy - timedelta(days=365 * (i + 1))).isoformat()
        conn.execute(
            "INSERT INTO clientes (nombre, nif, email, telefono, ciudad, fecha_alta) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, nif, email, telefono, ciudad, fecha_alta),
        )
    conn.commit()

    numero_factura = 1000
    for cliente_id, producto_id, cantidad, dias_atras, estado in PEDIDOS_DEMO:
        fecha_pedido = (hoy - timedelta(days=dias_atras)).isoformat()
        cursor = conn.execute(
            "INSERT INTO pedidos (cliente_id, producto_id, cantidad, fecha, estado) "
            "VALUES (?, ?, ?, ?, ?)",
            (cliente_id, producto_id, cantidad, fecha_pedido, estado),
        )
        pedido_id = cursor.lastrowid

        if estado == "Facturado":
            precio_unitario = conn.execute(
                "SELECT precio_unitario FROM productos WHERE id = ?", (producto_id,)
            ).fetchone()[0]
            total = round(cantidad * precio_unitario, 2)
            numero_factura += 1
            conn.execute(
                "INSERT INTO facturas (pedido_id, numero, fecha, total, estado) "
                "VALUES (?, ?, ?, ?, 'Pagada')",
                (pedido_id, f"F-2024-{numero_factura}", fecha_pedido, total),
            )
    conn.commit()
