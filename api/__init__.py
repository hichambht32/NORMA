from flask import Flask
from api.api_api.functions import views_app
from api.connection import db




def create_app():
    app = Flask(__name__)
    app.config.from_object('config.config')

    db.init_app(app)
    app.register_blueprint(views_app)  

    return app 