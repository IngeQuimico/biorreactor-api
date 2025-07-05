# servidor.py (Versión final con inicialización corregida)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import libsql_client
from asgiref.wsgi import WsgiToAsgi
import asyncio

app = Flask(__name__)
CORS(app)
asgi_app = WsgiToAsgi(app) # Puente para que Flask hable con el servidor ASGI

# --- FUNCIÓN ASÍNCRONA PARA INICIALIZAR LA BASE DE DATOS ---
async def init_db():
    """Asegura que la tabla 'lecturas' exista en la base de datos de Turso."""
    url = os.environ.get("TURSO_DATABASE_URL")
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url or not auth_token:
        print("ERROR CRÍTICO: Faltan las variables de entorno de Turso.")
        return

    try:
        async with libsql_client.create_client(url=url, auth_token=auth_token) as client:
            await client.execute("""
                CREATE TABLE IF NOT EXISTS lecturas (
                    id INTEGER PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperatura_c REAL,
                    ph_valor REAL
                )
            """)
        print("Conexión con Turso exitosa. Tabla 'lecturas' verificada.")
    except Exception as e:
        print(f"Error al inicializar la base de datos en Turso: {e}")

# --- RUTAS DE LA API (AHORA ASÍNCRONAS) ---

@app.route('/datos', methods=['POST'])
async def recibir_datos():
    try:
        datos = await request.get_json()
        temp = datos.get('temperatura')
        ph = datos.get('ph')
        print(f"Dato recibido -> Temp: {temp} °C, pH: {ph}")
        
        async with libsql_client.create_client(url=os.environ.get("TURSO_DATABASE_URL"), auth_token=os.environ.get("TURSO_AUTH_TOKEN")) as client:
            await client.execute("INSERT INTO lecturas (temperatura_c, ph_valor) VALUES (?, ?)", (temp, ph))
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error procesando la petición /datos: {e}")
        return jsonify({"status": "error en el servidor"}), 500

@app.route('/get_data', methods=['GET'])
async def get_data():
    try:
        async with libsql_client.create_client(url=os.environ.get("TURSO_DATABASE_URL"), auth_token=os.environ.get("TURSO_AUTH_TOKEN")) as client:
            rs = await client.execute("SELECT timestamp, temperatura_c, ph_valor FROM lecturas ORDER BY timestamp DESC LIMIT 1000")
            data = list(rs)[::-1]
        
        timestamps = [row[0] for row in data]
        temperatures = [row[1] for row in data]
        phs = [row[2] for row in data]
        
        return jsonify({"timestamps": timestamps, "temperatures": temperatures, "phs": phs})
    except Exception as e:
        print(f"Error al obtener datos /get_data: {e}")
        return jsonify({"error": str(e)}), 500

# --- INICIALIZACIÓN DE LA APLICACIÓN ---
# Cuando el script se ejecuta, llamamos a la función de inicialización de la BD.
# Usamos asyncio.run() para ejecutar nuestra función asíncrona en este contexto síncrono.
try:
    asyncio.run(init_db())
except RuntimeError:
    # Si ya hay un bucle de eventos corriendo (común en servidores de producción),
    # simplemente lo usamos para ejecutar nuestra función.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

