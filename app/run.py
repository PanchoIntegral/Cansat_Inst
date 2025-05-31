from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='dist', template_folder='dist')
CORS(app)  # Habilita CORS para todas las rutas

# Usar la misma ruta que en Lora.py
DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cansat_latest_data.json")

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


@app.route('/<path:filename>')
def serve_vue_assets(filename):
    try:
        return send_from_directory(app.static_folder, filename)
    except:
        return send_from_directory(app.static_folder, 'index.html')


# Servir el index.html de Vue para la ruta raíz
@app.route('/')
def serve_vue_app():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({
            "error": "Vue app not built or index.html not found in dist folder.",
            "details": str(e)
        }), 404


if __name__ == '__main__':
    print("Iniciando servidor CANSAT...")
    print("- Frontend: http://localhost:5000")
    print("- API: http://localhost:5000/api/cansat_data")
    app.run(host='0.0.0.0', port=5000, debug=False)