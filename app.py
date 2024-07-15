from flask import Flask, render_template, url_for, request, redirect, flash
from db import db
from models import *
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
db.init_app(app)


## Login and register

def check_user(name, pswd, role):
    # check if the user exists
    if role == 'sponsor':
        usr = Sponsor.query.filter_by(user_name = name, password = pswd).first()
    elif role == 'influencer':
        usr = Influencer.query.filter_by(user_name = name, password = pswd).first()
    else:
        usr = Admin.query.filter_by(user_name = name, password = pswd).first()
    
    if usr == None:
        return (False, usr)
    else:
        return (True, usr)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('user_login.html', msg = "")
    else:
        user = request.form['username']
        pswd = request.form['password']
        role = request.form['role']
        check, usr = check_user(user, pswd, role)
        if check:
            if usr.role == "influencer":
                return redirect(url_for('inf_dashboard', uname=usr.user_id))
            else:
                return redirect(url_for('sp_dashboard', uname = usr.user_id))
        else:
            return render_template('user_login.html', msg = 'Invalid username or password, try again.')



@app.route('/admin', methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    else:
        user = request.form['username']
        pswd = request.form['password']
        check, aid = check_user(user, pswd, 'admin')
        if check:
            return redirect(url_for('admin_dashboard'))



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


@app.route('/register/influencer', methods = ['GET', 'POST'])
def registerI():
    if request.method == 'GET':
        return render_template('influencer_register.html')
    elif request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        fname = request.form['full-name'] 
        age = request.form['age']
        reach = request.form['reach']
        niche = request.form['niche']
        link = request.form['link']
        pswd = request.form['password']
        user = Influencer(user_name = uname, fname = fname, age = age, reach = reach, niche = niche, link = link, email = email, password = pswd)
        db.session.add(user)
        db.session.commit()
        return redirect('/')

@app.route('/register/sponsor', methods = ['GET', 'POST'])
def registerS():
    if request.method == 'GET':
        return render_template('sponsor_register.html')
    elif request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        fname = request.form['full-name'] 
        cname = request.form['company']
        indus = request.form['Industry']
        link = request.form['link']
        pswd = request.form['password']
        user = Influencer(user_name = uname, fname = fname, cname = cname, industry = indus, link = link, email = email, password = pswd)
        db.session.add(user)
        db.session.commit()
        return redirect('/')


################ ADMIN DASHBOARD AND FEATURES ###############################
###########################################################################

@app.route('/dash')
def admin_dashboard():
    return render_template('admin_dash.html')

@app.route('/dash/influencers')
def admin_inf():
    if request.method == 'GET':
        content = Influencer.query.all()
        return render_template('admin_info.html', content = content)
    
@app.route('/dash/sponsors')
def admin_sp():
    if request.method == 'GET':
        content = Sponsor.query.all()
        return render_template('admin_info.html', content = content)


@app.route('/dash/allcampaigns')
def admin_allcamp():
    if request.method == 'GET':
        content = Campaigns.query.all()
        return render_template('admin_info.html', content = content)
    
@app.route('/dash/activecampaigns')
def admin_actcamp():
    if request.method == 'GET':
        content = Campaigns.query.filter(Campaigns.date_end < datetime.now()).all()
        return render_template('admin_info.html', content = content)
    
@app.route('/dash/adrequests')
def admin_adreq():
    if request.method == 'GET':
        content = Influencer_Requests.query.all()
        content += Sponsor_Requests.query.all()
        return render_template('admin_info', content = content)


#####################################################
#########################################################
@app.route('/influencer/<string:uname>', methods=['GET', 'POST'])
def inf_dashboard(uname):
    if request.method == 'GET':
        usr = Influencer.query.filter_by(user_id = uname)
        new = Influencer_Requests.query.filter_by(inf = usr.user_id, status = 0)
        subquery = db.session.query(Influencer_Requests.cid).filter_by(inf=usr.user_id, status=1).subquery()
        subquery += db.session.query(Sponsor_Requests.cid).filter_by(inf=usr.user_id, status=1).subquery()
        active = db.session.query(Campaigns).filter(Campaigns.cid.in_(subquery),Campaigns.date_end <= datetime.now()).all()

        return render_template('profile.html', user = usr.user_name, new = new, active = active)



@app.route('/sponsor/<string:uname>', methods=['GET', 'POST'])
def sp_dashboard(uname):
    if request.method == 'GET':
        usr = Sponsor.query.filter_by(user_id = uname)
        active = Campaigns.query.filter(Campaigns.creator == usr.user_id, Campaigns.date_end <= datetime.now()).all()
        new = Sponsor_Requests.query.filter_by(sp = usr.user_id, status = 0)
        return render_template('profile.html', user = uname, active = active, new= new)



@app.route('/influencer/find')
def ifind():
    if request.method == "GET":
        search = request.args.get("search")
        if search:
            cmp = Campaigns.query.filter(Campaigns.cname.like(search)).all()
            cmp += Campaigns.query.filter(Campaigns.niche.like(search)).all()
            cmp += Campaigns.query.filter(Campaigns.description.like(search)).all()
        else:
            cmp = Campaigns.query.filter_by(visibility="public")

    return render_template('infind.html', content = cmp)
   
        

@app.route('/sponsor/find')
def sfind():
    if request.method == "GET":
        search = request.args.get("search")
        if search:
            print(search)
            content = Influencer.query.filter(Influencer.user_name.like(search)).all()
            content += Influencer.query.filter(Influencer.fname.like(search)).all()
            content += Influencer.query.filter(Influencer.niche.like(search)).all()
            content += Influencer.query.filter(Influencer.age.like(search)).all()
        else:
            content = Influencer.query.all()

    return render_template('spfind.html', content = content)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()