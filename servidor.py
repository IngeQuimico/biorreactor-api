# servidor.py
from flask import Flask, request, jsonify
import sqlite3

# --- CONFIGURACIÓN ---
DB_FILE = "sensores.db"
app = Flask(__name__)

# --- RUTA PARA RECIBIR DATOS ---
@app.route('/datos', methods=['POST'])
def recibir_datos():
    """
    Escucha las peticiones POST del ESP32, extrae los datos
    de temperatura y pH, y los guarda en la base de datos.
    """
    try:
        # Obtener los datos JSON que nos envió el ESP32
        datos = request.get_json()
        
        # Extraer los valores. Usamos .get() para evitar errores si un dato no viene.
        temp = datos.get('temperatura')
        ph = datos.get('ph')
        
        print(f"Dato recibido -> Temp: {temp} °C, pH: {ph}")

        # Guardar los datos en la base de datos
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lecturas (temperatura_c, ph_valor) VALUES (?, ?)", (temp, ph))
        conn.commit()
        conn.close()
        
        # Responder al ESP32 que todo salió bien
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error procesando la petición: {e}")
        # Responder al ESP32 que hubo un error
        return jsonify({"status": "error en el servidor"}), 500

# --- INICIAR EL SERVIDOR ---
if __name__ == '__main__':
    # Usamos host='0.0.0.0' para que el servidor sea accesible
    # desde otros dispositivos en la misma red local (como el ESP32).
    app.run(host='0.0.0.0', port=5000, debug=True)
