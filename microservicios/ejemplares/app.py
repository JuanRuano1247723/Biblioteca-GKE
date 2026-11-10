import os

import psycopg
from flask import Flask, jsonify, request
from psycopg import errors
from psycopg.rows import dict_row

app = Flask(__name__)


def get_db_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    )


def error(msg, code):
    return jsonify({"error": msg}), code


def leer_json():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def validar(data, parcial=False):
    """Devuelve (titulo, autor, anio, mensaje_error)."""
    titulo = (data.get("titulo") or "").strip() if isinstance(data.get("titulo"), str) else None
    autor = (data.get("autor") or "").strip() if isinstance(data.get("autor"), str) else None
    if not titulo or not autor:
        return None, None, None, "Los campos titulo y autor son obligatorios"
    anio = data.get("anio")
    if anio is not None and (isinstance(anio, bool) or not isinstance(anio, int)):
        return None, None, None, "El campo anio debe ser un entero"
    return titulo, autor, anio, None


@app.errorhandler(psycopg.OperationalError)
def db_down(e):
    return error("Base de datos no disponible", 503)


@app.errorhandler(404)
def no_encontrada(e):
    return error("Ruta no encontrada", 404)


@app.route("/healthz", methods=["GET"])
@app.route("/health", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200


# ---------- Integrantes (solo lectura) ----------
@app.route("/api/integrantes", methods=["GET"])
def integrantes():
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT carne, nombre FROM integrantes ORDER BY nombre")
        return jsonify(cur.fetchall()), 200


# ---------- Ejemplares (CRUD) ----------
@app.route("/api/ejemplares", methods=["POST"])
def crear():
    titulo, autor, anio, msg = validar(leer_json())
    if msg:
        return error(msg, 400)
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ejemplares (titulo, autor, anio) VALUES (%s, %s, %s) RETURNING *",
            (titulo, autor, anio),
        )
        return jsonify(cur.fetchone()), 201


@app.route("/api/ejemplares", methods=["GET"])
def listar():
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM ejemplares ORDER BY id")
        return jsonify(cur.fetchall()), 200


@app.route("/api/ejemplares/<int:id>", methods=["GET"])
def obtener(id):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM ejemplares WHERE id = %s", (id,))
        fila = cur.fetchone()
    if fila is None:
        return error("Ejemplar no encontrado", 404)
    return jsonify(fila), 200


@app.route("/api/ejemplares/<int:id>", methods=["PUT"])
def actualizar(id):
    titulo, autor, anio, msg = validar(leer_json())
    if msg:
        return error(msg, 400)
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE ejemplares SET titulo = %s, autor = %s, anio = %s WHERE id = %s RETURNING *",
            (titulo, autor, anio, id),
        )
        fila = cur.fetchone()
    if fila is None:
        return error("Ejemplar no encontrado", 404)
    return jsonify(fila), 200


@app.route("/api/ejemplares/<int:id>", methods=["DELETE"])
def eliminar(id):
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM ejemplares WHERE id = %s RETURNING id", (id,))
            fila = cur.fetchone()
    except errors.ForeignKeyViolation:
        return error("No se puede eliminar: el ejemplar tiene préstamos", 409)
    if fila is None:
        return error("Ejemplar no encontrado", 404)
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
