import os

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "biblioteca")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")

import psycopg2
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def ejemplar_id():
    """Crea un ejemplar de prueba (solo para tests) y lo limpia al terminar."""
    conn = psycopg2.connect(host=os.environ["DB_HOST"], port=os.environ["DB_PORT"],
                            dbname=os.environ["DB_NAME"], user=os.environ["DB_USER"],
                            password=os.environ["DB_PASSWORD"])
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO ejemplares (titulo, autor, anio) "
                    "VALUES ('Libro de prueba', 'Autor de prueba', 2000) RETURNING id")
        eid = cur.fetchone()[0]
    yield eid
    with conn, conn.cursor() as cur:
        cur.execute("DELETE FROM prestamos WHERE ejemplar_id = %s", (eid,))
        cur.execute("DELETE FROM ejemplares WHERE id = %s", (eid,))
    conn.close()


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_crud_completo(client, ejemplar_id):
    # CREATE
    r = client.post("/api/prestamos", json={"ejemplar_id": ejemplar_id, "prestatario": "Ana"})
    assert r.status_code == 201
    p = r.json()
    assert p["ejemplar_id"] == ejemplar_id and p["prestatario"] == "Ana"
    assert p["fecha_prestamo"] == str(__import__("datetime").date.today())  # por defecto hoy
    assert p["fecha_devolucion"] is None
    pid = p["id"]

    # READ (lista y uno)
    assert any(x["id"] == pid for x in client.get("/api/prestamos").json())
    assert client.get(f"/api/prestamos/{pid}").status_code == 200

    # UPDATE (registrar devolución)
    r = client.put(f"/api/prestamos/{pid}", json={
        "ejemplar_id": ejemplar_id, "prestatario": "Ana", "fecha_devolucion": "2026-11-09"})
    assert r.status_code == 200 and r.json()["fecha_devolucion"] == "2026-11-09"

    # DELETE
    assert client.delete(f"/api/prestamos/{pid}").status_code == 204
    assert client.get(f"/api/prestamos/{pid}").status_code == 404


def test_ejemplar_inexistente_da_400(client):
    r = client.post("/api/prestamos", json={"ejemplar_id": 999999, "prestatario": "X"})
    assert r.status_code == 400 and "error" in r.json()


def test_put_ejemplar_inexistente_da_400(client, ejemplar_id):
    pid = client.post("/api/prestamos",
                      json={"ejemplar_id": ejemplar_id, "prestatario": "Y"}).json()["id"]
    r = client.put(f"/api/prestamos/{pid}", json={"ejemplar_id": 999999, "prestatario": "Y"})
    assert r.status_code == 400 and "error" in r.json()


def test_falta_prestatario_da_400(client, ejemplar_id):
    r = client.post("/api/prestamos", json={"ejemplar_id": ejemplar_id})
    assert r.status_code == 400 and "error" in r.json()


def test_prestatario_vacio_da_400(client, ejemplar_id):
    r = client.post("/api/prestamos", json={"ejemplar_id": ejemplar_id, "prestatario": "   "})
    assert r.status_code == 400


def test_404_en_inexistentes(client, ejemplar_id):
    assert client.get("/api/prestamos/999999").status_code == 404
    assert client.delete("/api/prestamos/999999").status_code == 404
    r = client.put("/api/prestamos/999999", json={"ejemplar_id": ejemplar_id, "prestatario": "Z"})
    assert r.status_code == 404 and "error" in r.json()