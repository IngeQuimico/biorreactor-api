# crear_db.py
import sqlite3

# --- NOMBRE DEL ARCHIVO DE LA BASE DE DATOS ---
DB_FILE = "sensores.db"

try:
    # Conectarse (creará el archivo si no existe)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # --- DEFINICIÓN DE LA TABLA ---
    # Creamos la tabla 'lecturas' si no existe ya.
    # Incluimos columnas para temperatura y pH, ambas pueden ser nulas
    # si un sensor falla pero el otro no.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lecturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperatura_c REAL,
        ph_valor REAL 
    );
    ''')

    print(f"Base de datos '{DB_FILE}' y tabla 'lecturas' verificadas/creadas exitosamente.")

except Exception as e:
    print(f"Ocurrió un error al crear la base de datos: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.commit()
        conn.close()
