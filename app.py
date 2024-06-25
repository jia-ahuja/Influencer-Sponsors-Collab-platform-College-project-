from flask import Flask, render_template, url_for, request, redirect, flash
from db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
db.init_app(app)

def check_user(name, pswd, role):
    pass

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('user_login.html')
    else:
        user = request.form['username']
        pswd = request.form['password']
        role = request.form['role']
        check_user(user, pswd, role)

@app.route('/admin', methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    else:
        user = request.form['username']
        pswd = request.form['password']
        check_user(user, pswd, 'admin')

@app.route('/register', methods = ['GET', 'POST'])
def get_role():
    if request.method == 'GET':
        return render_template('roles.html')
    else:
        role = request.form['role']
        if role == "influencer":
            return redirect('/register/influencer')
        else:
            return redirect('/register/sponsor')

@app.route('/register/influencer')
def registerI():
    return render_template('influencer_register.html')

@app.route('/register/sponsor')
def registerS():
    return render_template('sponsor_register.html')


        
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()