# servidor.py (Versión final con puente ASGI-WSGI)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import libsql_client
from asgiref.wsgi import WsgiToAsgi # <--- IMPORTAR EL TRADUCTOR

app = Flask(__name__)
CORS(app)

# --- APLICAR EL TRADUCTOR ---
# Esto envuelve nuestra aplicación Flask para que pueda "hablar" con el servidor ASGI (Uvicorn)
asgi_app = WsgiToAsgi(app) # <--- APLICAR EL TRADUCTOR

def create_turso_client():
    url = os.environ.get("TURSO_DATABASE_URL")
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url: raise ValueError("Variable TURSO_DATABASE_URL no encontrada.")
    if not auth_token: raise ValueError("Variable TURSO_AUTH_TOKEN no encontrada.")
    return libsql_client.create_client(url=url, auth_token=auth_token)

def init_db():
    try:
        client = create_turso_client()
        client.execute("CREATE TABLE IF NOT EXISTS lecturas (id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, temperatura_c REAL, ph_valor REAL)")
        print("Conexión con Turso exitosa. Tabla 'lecturas' verificada.")
        client.close()
    except Exception as e:
        print(f"Error al inicializar la base de datos en Turso: {e}")

@app.route('/datos', methods=['POST'])
def recibir_datos():
    try:
        datos = request.get_json()
        client = create_turso_client()
        client.execute("INSERT INTO lecturas (temperatura_c, ph_valor) VALUES (?, ?)", (datos.get('temperatura'), datos.get('ph')))
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
