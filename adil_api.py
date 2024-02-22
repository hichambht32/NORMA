from flask import Flask, request, jsonify
from api.functions import views_app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.config')
db = SQLAlchemy(app)
app.register_blueprint(views_app)


if __name__ == '__main__':
    app.run(debug=True)
