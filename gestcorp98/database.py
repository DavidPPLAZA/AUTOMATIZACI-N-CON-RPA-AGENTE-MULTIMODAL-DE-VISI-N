import sqlite3
from datetime import date

from gestcorp98 import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nif TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    ciudad TEXT,
    fecha_alta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio_unitario REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'Pendiente'
);

CREATE TABLE IF NOT EXISTS facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
    numero TEXT NOT NULL UNIQUE,
    fecha TEXT NOT NULL,
    total REAL NOT NULL,
    estado TEXT NOT NULL DEFAULT 'Pendiente'
);
"""


def get_connection() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def list_clientes(conn: sqlite3.Connection):
    return conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()


def insert_cliente(conn: sqlite3.Connection, *, nombre, nif, email, telefono, ciudad) -> None:
    conn.execute(
        "INSERT INTO clientes (nombre, nif, email, telefono, ciudad, fecha_alta) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, nif, email, telefono, ciudad, date.today().isoformat()),
    )
    conn.commit()


def count_pedidos_cliente(conn: sqlite3.Connection, cliente_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM pedidos WHERE cliente_id = ?", (cliente_id,)
    ).fetchone()[0]


def delete_cliente(conn: sqlite3.Connection, cliente_id: int) -> None:
    """Borra el cliente y, en cascada, sus pedidos y las facturas de esos
    pedidos (si no, quedarian pedidos de un cliente que ya no existe)."""
    conn.execute(
        "DELETE FROM facturas WHERE pedido_id IN (SELECT id FROM pedidos WHERE cliente_id = ?)",
        (cliente_id,),
    )
    conn.execute("DELETE FROM pedidos WHERE cliente_id = ?", (cliente_id,))
    conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()


def list_productos(conn: sqlite3.Connection):
    return conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()


def list_pedidos(conn: sqlite3.Connection):
    rows = conn.execute(
        """
        SELECT p.id, c.nombre AS cliente_nombre, pr.nombre AS producto_nombre,
               p.cantidad, pr.precio_unitario, p.fecha, p.estado
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        JOIN productos pr ON pr.id = p.producto_id
        ORDER BY p.fecha DESC, p.id DESC
        """
    ).fetchall()
    pedidos = []
    for row in rows:
        pedido = dict(row)
        pedido["total"] = pedido["cantidad"] * pedido["precio_unitario"]
        pedidos.append(pedido)
    return pedidos


def insert_pedido(conn: sqlite3.Connection, *, cliente_id, producto_id, cantidad) -> None:
    conn.execute(
        "INSERT INTO pedidos (cliente_id, producto_id, cantidad, fecha, estado) "
        "VALUES (?, ?, ?, ?, 'Pendiente')",
        (cliente_id, producto_id, cantidad, date.today().isoformat()),
    )
    conn.commit()


def delete_pedido(conn: sqlite3.Connection, pedido_id: int) -> None:
    """Borra el pedido y su factura, si la tiene."""
    conn.execute("DELETE FROM facturas WHERE pedido_id = ?", (pedido_id,))
    conn.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    conn.commit()


def list_facturas(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT f.numero, c.nombre AS cliente_nombre, f.fecha, f.total, f.estado
        FROM facturas f
        JOIN pedidos p ON p.id = f.pedido_id
        JOIN clientes c ON c.id = p.cliente_id
        ORDER BY f.fecha DESC, f.id DESC
        """
    ).fetchall()


def get_informe_stats(conn: sqlite3.Connection) -> dict:
    total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    pedidos_pendientes = conn.execute(
        "SELECT COUNT(*) FROM pedidos WHERE estado = 'Pendiente'"
    ).fetchone()[0]
    total_facturado = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM facturas WHERE estado = 'Pagada'"
    ).fetchone()[0]
    return {
        "total_clientes": total_clientes,
        "pedidos_pendientes": pedidos_pendientes,
        "total_facturado": total_facturado,
    }
