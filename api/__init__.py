from flask import Flask
from api.api_api.functions import views_app




def create_app():
    app = Flask(__name__)
    app.config.from_object('config.config')

    app.register_blueprint(views_app)  

    return app 