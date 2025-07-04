# servidor.py (Versión Robusta con Inicialización de BD)
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

# --- CONFIGURACIÓN ---
DB_FILE = "sensores.db"
app = Flask(__name__)
CORS(app)

# --- FUNCIÓN PARA INICIALIZAR LA BASE DE DATOS ---
def init_db():
    """
    Verifica si la tabla 'lecturas' existe y, si no, la crea.
    Esto hace que el servidor sea robusto frente a reinicios.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lecturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperatura_c REAL,
        ph_valor REAL 
    );
    ''')
    conn.commit()
    conn.close()
    print(f"Base de datos '{DB_FILE}' inicializada y lista.")

# --- RUTA PARA RECIBIR DATOS DEL ESP32 ---
@app.route('/datos', methods=['POST'])
def recibir_datos():
    try:
        datos = request.get_json()
        temp = datos.get('temperatura')
        ph = datos.get('ph')
        print(f"Dato recibido -> Temp: {temp} °C, pH: {ph}")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lecturas (temperatura_c, ph_valor) VALUES (?, ?)", (temp, ph))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error procesando la petición /datos: {e}")
        return jsonify({"status": "error en el servidor"}), 500

# --- RUTA PARA ENTREGAR DATOS A LA PÁGINA WEB ---
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT timestamp, temperatura_c, ph_valor FROM lecturas ORDER BY timestamp DESC LIMIT 1000"
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()[::-1] # Invertir para orden cronológico
        conn.close()
        
        timestamps = [row[0] for row in data]
        temperatures = [row[1] for row in data]
        phs = [row[2] for row in data]

        return jsonify({
            "timestamps": timestamps,
            "temperatures": temperatures,
            "phs": phs
        })
    except Exception as e:
        print(f"Error al obtener datos /get_data: {e}")
        return jsonify({"error": str(e)}), 500

# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Al iniciar, llamamos a la función para asegurar que la BD está lista.
    init_db()
    # Esto es solo para pruebas locales. Render usará gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Esto se ejecutará cuando Render inicie la aplicación con Gunicorn.
    init_db()
