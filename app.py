from flask import Flask, render_template, url_for, request, redirect, flash
from db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://project.db"
db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()