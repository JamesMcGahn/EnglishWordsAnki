import uuid
from concurrent.futures import ThreadPoolExecutor

import waitress
from flask import Flask, jsonify, request
from flask_cors import CORS
from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from models import Status, WordModel, WordsModel


class FlaskWorker(QObjectBase):
    add_word_to_model = Signal(WordModel)
    stop_signal = Signal()
    finished = Signal()

    server = Flask(__name__)
    CORS(server)

    def __init__(self):
        super().__init__()
        self.setup_routes()
        self.wordsModel = WordsModel()
        self.add_word_to_model.connect(self.wordsModel.add_word)
        self.stop_signal.connect(self.stop_server)
        self.PORT = 5002
        self.HOST = "127.0.0.1"
        self.server_create = None
        self.running = False

    def setup_routes(self):
        """Define Flask routes."""

        @self.server.route("/")
        def home():
            return "EnglishWords Dict - API"

        @self.server.route("/data", methods=["GET"])
        def route_data():
            return jsonify({"message": "Hello, World!"})

        @self.server.route("/word", methods=["POST"])
        def route_word():
            if request.method == "POST":
                return self.handle_word_post(request)

    def run(self):
        """Run the Flask server."""

        try:
            self.running = True
            self.logging(f"Starting server {self.HOST} on port {self.PORT}")
            self.server_create = waitress.create_server(
                self.server, host=self.HOST, port=self.PORT
            )
            self.executor = ThreadPoolExecutor(max_workers=8)
            self.executor.submit(self.server_create.run)

        except OSError as e:
            self.running = False
            if "Address already in use" in str(e):
                self.logging(
                    f"Server address already in use. Choose a different port. {self.PORT}",
                    "ERROR",
                )
            else:
                self.logging(f"Server interrupted: {e}", "ERROR")
            print("***************sss")
        except Exception as e:
            print("***************sssaaa")
            self.running = False
            self.logging(f"Server interrupted: {e}", "ERROR")

    @Slot()
    def stop_server(self):
        """Stop the server."""
        self.logging(f"Shutting down Server -  {self.HOST} on port {self.PORT}....")
        if self.server_create and self.running:
            self.running = False
            self.server_create.close()
            self.server_create = None
            self.logging(f"Server stopped - {self.HOST} on port {self.PORT} ")

        self.finished.emit()

    def handle_word_post(self, request):
        data = request.json
        if "word" not in data:
            return jsonify({"error": "Missing 'word' field"}), 400

        new_word = WordModel(
            Status.ADDED, str(uuid.uuid4()), data["word"], "", "", "", "", ""
        )
        self.add_word_to_model.emit(new_word)
        return jsonify({"word": data["word"]}), 201
