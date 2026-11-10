import os
from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)


def get_db_connection():
  conn = psycopg.connect(
      host=os.environ.get('DB_HOST', 'localhost'),
      dbname=os.environ.get('DB_NAME', 'biblioteca'),
      user=os.environ.get('DB_USER', 'postgres'),
      password=os.environ.get('DB_PASSWORD', 'password'),
      port=int(os.environ.get('DB_PORT', 5432)),
      row_factory=dict_row,
  )
  return conn


# Inicializar la tabla de Ejemplares si no existe
def init_db():
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS ejemplares (
                        id SERIAL PRIMARY KEY,
                        isbn VARCHAR(50) UNIQUE NOT NULL,
                        titulo VARCHAR(150) NOT NULL,
                        autor VARCHAR(100) NOT NULL,
                        editorial VARCHAR(100),
                        stock INT NOT NULL DEFAULT 1
                    );
                """)
      conn.commit()
  except Exception as e:
    print(f"Error al conectar/inicializar la base de datos: {e}")


@app.route("/health", methods=["GET"])
def health_check():
  try:
    with get_db_connection() as conn:
      pass
    return jsonify({"status": "healthy", "database": "connected"}), 200
  except Exception as e:
    return (
        jsonify({"status": "unhealthy", "error": str(e)}),
        500,
    )


# 1. CREAR un ejemplar (POST)
@app.route("/ejemplares", methods=["POST"])
def crear_ejemplar():
  data = request.get_json()
  isbn = data.get("isbn")
  titulo = data.get("titulo")
  autor = data.get("autor")
  editorial = data.get("editorial")
  stock = data.get("stock", 1)

  if not isbn or not titulo or not autor:
    return (
        jsonify(
            {"error": "Los campos isbn, titulo y autor son obligatorios"}
        ),
        400,
    )

  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
            """
                    INSERT INTO ejemplares (isbn, titulo, autor, editorial, stock) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING id, isbn, titulo, autor, editorial, stock;
                """,
            (isbn, titulo, autor, editorial, stock),
        )
        nuevo = cur.fetchone()
      conn.commit()

    return jsonify(nuevo), 201
  except Exception as e:
    return jsonify({"error": str(e)}), 500


# 2. CONSULTAR todos los ejemplares (GET)
@app.route("/ejemplares", methods=["GET"])
def obtener_ejemplares():
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute("SELECT * FROM ejemplares ORDER BY id ASC;")
        ejemplares = cur.fetchall()
    return jsonify(ejemplares), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500


# 2.1 CONSULTAR un ejemplar por ID (GET)
@app.route("/ejemplares/<int:id>", methods=["GET"])
def obtener_ejemplar_por_id(id):
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute("SELECT * FROM ejemplares WHERE id = %s;", (id,))
        ejemplar = cur.fetchone()

    if not ejemplar:
      return jsonify({"error": "Ejemplar no encontrado"}), 404

    return jsonify(ejemplar), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500


# 3. ACTUALIZAR un ejemplar (PUT)
@app.route("/ejemplares/<int:id>", methods=["PUT"])
def actualizar_ejemplar(id):
  data = request.get_json()
  isbn = data.get("isbn")
  titulo = data.get("titulo")
  autor = data.get("autor")
  editorial = data.get("editorial")
  stock = data.get("stock")

  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
            """
                    UPDATE ejemplares 
                    SET isbn = COALESCE(%s, isbn), 
                        titulo = COALESCE(%s, titulo), 
                        autor = COALESCE(%s, autor), 
                        editorial = COALESCE(%s, editorial), 
                        stock = COALESCE(%s, stock)
                    WHERE id = %s RETURNING *;
                """,
            (isbn, titulo, autor, editorial, stock, id),
        )
        actualizado = cur.fetchone()
      conn.commit()

    if not actualizado:
      return jsonify({"error": "Ejemplar no encontrado"}), 404

    return jsonify(actualizado), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500


# 4. ELIMINAR un ejemplar (DELETE)
@app.route("/ejemplares/<int:id>", methods=["DELETE"])
def eliminar_ejemplar(id):
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute("DELETE FROM ejemplares WHERE id = %s RETURNING id;", (id,))
        eliminado = cur.fetchone()
      conn.commit()

    if not eliminado:
      return jsonify({"error": "Ejemplar no encontrado"}), 404

    return jsonify({"mensaje": f"Ejemplar con id {id} eliminado correctamente"}), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  init_db()
  app.run(host="0.0.0.0", port=5000)