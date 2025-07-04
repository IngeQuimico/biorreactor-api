# servidor.py (listo para producción)
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

DB_FILE = "sensores.db"
app = Flask(__name__)
CORS(app) 

@app.route('/datos', methods=['POST'])
def recibir_datos():
    # ... (esta función no cambia)
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
        print(f"Error procesando la petición: {e}")
        return jsonify({"status": "error en el servidor"}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    # ... (esta función no cambia)
    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT timestamp, temperatura_c, ph_valor FROM lecturas ORDER BY timestamp DESC LIMIT 1000"
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()[::-1]
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
        print(f"Error al obtener datos: {e}")
        return jsonify({"error": str(e)}), 500

# La sección if __name__ == '__main__': se puede borrar o dejar, 
# Render no la usará.
