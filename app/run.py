from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='dist/js', template_folder='dist') # Ajusta static_folder si Vue usa otro nombre para JS
CORS(app) # Habilita CORS para todas las rutas, útil para desarrollo con Vue dev server

DATA_FILE_PATH = "/tmp/cansat_latest_data.json" # Mismo path que en lora_receiver.py

@app.route('/api/cansat_data')
def get_cansat_data():
    try:
        if os.path.exists(DATA_FILE_PATH):
            with open(DATA_FILE_PATH, "r") as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({"error": "No data available yet"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<path:subpath>')
def serve_vue_assets(subpath):
    # Comprueba si el subpath es un directorio conocido de assets de Vue
    known_asset_dirs = ['js', 'css', 'img', 'fonts'] # Añade otros si es necesario
    path_parts = subpath.split('/')
    if path_parts[0] in known_asset_dirs:
        return send_from_directory(os.path.join(app.root_path, 'dist', path_parts[0]), path_parts[1] if len(path_parts) > 1 else '')
    # Si no es un asset conocido, podría ser una ruta de Vue Router, así que sirve index.html
    return send_from_directory(os.path.join(app.root_path, 'dist'), 'index.html')


# Servir el index.html de Vue para la ruta raíz y cualquier otra ruta no API (manejo de Vue Router)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>') # Captura todas las rutas no manejadas por la API o assets
def serve_vue_app(path):
    # Si el archivo solicitado existe en dist (ej. favicon.ico), sírvelo.
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)): # app.static_folder es 'dist'
         return send_from_directory(app.static_folder, path)
    # De lo contrario, sirve el index.html principal de Vue
    # (Vue Router se encargará del enrutamiento del lado del cliente)
    index_path = os.path.join(app.root_path, 'dist', 'index.html')
    if not os.path.exists(index_path):
        return jsonify({"error": "Vue app not built or index.html not found in dist folder."}), 404
    return send_file(index_path)


if __name__ == '__main__':
    # Asegúrate que corre en 0.0.0.0 para ser accesible en la red
    app.run(host='0.0.0.0', port=5000, debug=False) # debug=False para "producción"