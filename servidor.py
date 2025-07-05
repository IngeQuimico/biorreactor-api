# servidor.py (Versión final con Turso)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from libsql_client import Client

app = Flask(__name__)
CORS(app)

def create_turso_client():
    url = os.environ.get("TURSO_DATABASE_URL")
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url:
        raise ValueError("No se encontró la variable de entorno TURSO_DATABASE_URL")
    return Client(url=url, auth_token=auth_token)

def init_db():
    try:
        client = create_turso_client()
        client.execute("""
            CREATE TABLE IF NOT EXISTS lecturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperatura_c REAL,
                ph_valor REAL
            )
        """)
        print("Conexión con Turso exitosa. Tabla 'lecturas' verificada.")
        client.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos en Turso: {e}")

@app.route('/datos', methods=['POST'])
def recibir_datos():
    try:
        datos = request.get_json()
        temp = datos.get('temperatura')
        ph = datos.get('ph')
        print(f"Dato recibido -> Temp: {temp} °C, pH: {ph}")
        client = create_turso_client()
        client.execute("INSERT INTO lecturas (temperatura_c, ph_valor) VALUES (?, ?)", (temp, ph))
        client.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error procesando la petición /datos: {e}")
        return jsonify({"status": "error en el servidor"}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        client = create_turso_client()
        rs = client.execute("SELECT timestamp, temperatura_c, ph_valor FROM lecturas ORDER BY timestamp DESC LIMIT 1000")
        data = list(rs)[::-1]
        timestamps = [row[0] for row in data]
        temperatures = [row[1] for row in data]
        phs = [row[2] for row in data]
        client.close()
        return jsonify({"timestamps": timestamps, "temperatures": temperatures, "phs": phs})
    except Exception as e:
        print(f"Error al obtener datos /get_data: {e}")
        return jsonify({"error": str(e)}), 500

init_db()