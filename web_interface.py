from flask import Flask, render_template, jsonify, request
import threading
from datetime import datetime

from settings import FEATURES


class KitchenWebInterface:
    def __init__(self, main_ref):
        self.app = Flask(__name__, template_folder="templates")
        self.main = main_ref

        # ---- DATA ----
        self.prediction = None
        self.action = None
        self.features = None

        self._setup_routes()

        # ---- RUN FLASK ----
        self.thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.thread.start()

    # ================= ROUTES =================
    def _setup_routes(self):

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/data')
        def get_data():
            return jsonify({
                "prediction": self.prediction,
                "action": self.action,
                "features": self.features,
            })

        @self.app.route('/submit_features', methods=['POST'])
        def receive_from_web():
            try:
                data = request.get_json()
                print("[INFO] Received from web:", data)
                self.main.input_mode = "web"
                # ordered = [
                #     data["fire"],
                #     data["gas"],
                #     data["temp"],
                #     data["human"],
                #     data["stove_on"],
                #     data["stove_time"],
                #     data["gas_delta"],
                #     data["temp_delta"]
                # ]
                self.main.process_sample(data, source="web")
                self.main.input_mode = "serial"
                return jsonify({"status": "ok"})
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                })

        @self.app.route('/resume')
        def resume_serial():
            self.main.input_mode = "serial"
            return jsonify({
                "status": "ok",
                "message": "Resumed serial mode"
            })

        @self.app.route('/stop')
        def stop_serial():
            self.main.input_mode = "web"
            return jsonify({
                "status": "ok",
                "message": "Stopped serial mode"
            })

        @self.app.route('/train')
        def train_model():
            self.main.input_mode = "web"
            threading.Thread(target=self.main.train_model, daemon=True).start()
            self.main.input_mode = "serial"
            return jsonify({
                "status": "ok",
                "message": "Model training started"
            })

    # ================= RUN SERVER =================
    def _run_server(self):
        print("Web interface running at http://127.0.0.1:5000")
        self.app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False
        )

    # ================= UPDATE DATA =================
    def update_data(self, prediction, action, features):
        self.prediction = prediction
        self.action = action
        self.features = features
