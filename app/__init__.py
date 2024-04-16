from flask import Flask

app = Flask(__name__)

from app.routes import configure_routes
configure_routes(app)