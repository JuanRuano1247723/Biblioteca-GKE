import os
from contextlib import contextmanager
from datetime import date
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="Microservicio Préstamos")


# ---------- Conexión (solo variables de entorno) ----------
def _connect():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


@contextmanager
def cursor():
    conn = _connect()
    try:
        with conn:                      # commit o rollback
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()


# ---------- Errores siempre con la forma {"error": "..."} ----------
@app.exception_handler(StarletteHTTPException)
async def http_error(request, exc):
    return JSONResponse({"error": str(exc.detail)}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    primero = exc.errors()[0]
    campo = ".".join(str(x) for x in primero["loc"] if x != "body")
    return JSONResponse({"error": f"Dato inválido en '{campo}': {primero['msg']}"},
                        status_code=400)


@app.exception_handler(psycopg2.OperationalError)
async def db_down(request, exc):
    return JSONResponse({"error": "Base de datos no disponible"}, status_code=503)


# ---------- Modelo ----------
class PrestamoIn(BaseModel):
    ejemplar_id: int
    prestatario: str = Field(min_length=1, max_length=120)
    fecha_prestamo: Optional[date] = None
    fecha_devolucion: Optional[date] = None


def validar_ejemplar(cur, ejemplar_id: int):
    cur.execute("SELECT 1 FROM ejemplares WHERE id = %s", (ejemplar_id,))
    if cur.fetchone() is None:
        raise HTTPException(400, f"El ejemplar {ejemplar_id} no existe")


def validar_prestatario(p: PrestamoIn):
    if not p.prestatario.strip():
        raise HTTPException(400, "El prestatario no puede estar vacío")


# ---------- Endpoints ----------
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/prestamos")
def listar():
    with cursor() as cur:
        cur.execute("SELECT * FROM prestamos ORDER BY id")
        return cur.fetchall()


@app.get("/api/prestamos/{id}")
def obtener(id: int):
    with cursor() as cur:
        cur.execute("SELECT * FROM prestamos WHERE id = %s", (id,))
        fila = cur.fetchone()
    if fila is None:
        raise HTTPException(404, "Préstamo no encontrado")
    return fila


@app.post("/api/prestamos", status_code=201)
def crear(p: PrestamoIn):
    validar_prestatario(p)
    with cursor() as cur:
        validar_ejemplar(cur, p.ejemplar_id)
        cur.execute(
            """INSERT INTO prestamos (ejemplar_id, prestatario, fecha_prestamo, fecha_devolucion)
               VALUES (%s, %s, COALESCE(%s, CURRENT_DATE), %s) RETURNING *""",
            (p.ejemplar_id, p.prestatario.strip(), p.fecha_prestamo, p.fecha_devolucion),
        )
        return cur.fetchone()


@app.put("/api/prestamos/{id}")
def actualizar(id: int, p: PrestamoIn):
    validar_prestatario(p)
    with cursor() as cur:
        cur.execute("SELECT 1 FROM prestamos WHERE id = %s", (id,))
        if cur.fetchone() is None:
            raise HTTPException(404, "Préstamo no encontrado")
        validar_ejemplar(cur, p.ejemplar_id)
        cur.execute(
            """UPDATE prestamos
                  SET ejemplar_id = %s, prestatario = %s,
                      fecha_prestamo = COALESCE(%s, fecha_prestamo),
                      fecha_devolucion = %s
                WHERE id = %s RETURNING *""",
            (p.ejemplar_id, p.prestatario.strip(), p.fecha_prestamo, p.fecha_devolucion, id),
        )
        return cur.fetchone()


@app.delete("/api/prestamos/{id}", status_code=204)
def eliminar(id: int):
    with cursor() as cur:
        cur.execute("DELETE FROM prestamos WHERE id = %s", (id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Préstamo no encontrado")
    return Response(status_code=204)