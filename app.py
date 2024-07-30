from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from db import db
from models import *
from datetime import datetime, timedelta
from sqlalchemy import select, func

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
            if role == "influencer":
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
            return redirect(url_for('admin_dashboard', uid = aid.user_id))



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
        user = Sponsor(user_name = uname, fname = fname, cname = cname, industry = indus, link = link, email = email, password = pswd)
        db.session.add(user)
        db.session.commit()
        return redirect('/')


################ ADMIN DASHBOARD AND FEATURES ###############################
###########################################################################

@app.route('/dash/<int:uid>')
def admin_dashboard(uid):
    if request.method == 'GET':
        inf = Flagged_users.query.filter_by(role = 0).all()
        spn = Flagged_users.query.filter_by(role = 1).all()
        return render_template('admin_dash.html', influencer = inf, sponsor = spn, user_id = uid, role = "admin")
    

@app.route('/dash/<int:uid>/influencers')
def admin_inf(uid):
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
        
    return render_template('admin_inf.html', content = content, user_id = uid, role = "admin")
    

@app.route('/dash/<int:uid>/sponsors')
def admin_sp(uid):
    if request.method == "GET":
        search = request.args.get("search")
        if search:
            print(search)
            content = Sponsor.query.filter(Sponsor.user_name.like(search)).all()
            content += Sponsor.query.filter(Sponsor.fname.like(search)).all()
            content += Sponsor.query.filter(Sponsor.cname.like(search)).all()
            content += Sponsor.query.filter(Sponsor.industry.like(search)).all()
        else:
            content = Sponsor.query.all()
        
    return render_template('admin_sp.html', content = content, user_id = uid, role = "admin")


@app.route('/dash/allcampaigns')
def admin_allcamp():
    if request.method == 'GET':
        content = Campaigns.query.all()
        return render_template('campaign.html', campaign = content)
    

@app.route('/dash/activecampaigns')
def admin_actcamp():
    if request.method == 'GET':
        content = Campaigns.query.filter(Campaigns.date_end >= datetime.now()).all()
        return render_template('campaign.html', campaign = content)
    

@app.route('/dash/<int:uid>/adrequests')
def admin_adreq(uid):
    if request.method == 'GET':
        # in_req = Influencer_Requests.query.all()
        in_req = db.session.query(Campaigns.cid, Campaigns.cname, Influencer_Requests.payment, Influencer_Requests.status, 
                                  Sponsor.user_id, Sponsor.user_name, Sponsor.industry,
                                  Influencer.user_id, Influencer.user_name, Influencer.niche)\
            .join(Influencer_Requests, Campaigns.cid == Influencer_Requests.cid)\
            .join(Influencer, Influencer.user_id == Influencer_Requests.inf)\
            .join(Sponsor, Sponsor.user_id == Influencer_Requests.sp)\
            .all()

        # sp_req = Sponsor_Requests.query.all()
        sp_req = db.session.query(Campaigns.cid, Campaigns.cname, Sponsor_Requests.payment, Sponsor_Requests.status, 
                                  Sponsor.user_id, Sponsor.user_name, Sponsor.industry,
                                  Influencer.user_id, Influencer.user_name, Influencer.niche)\
            .join(Sponsor_Requests, Campaigns.cid == Sponsor_Requests.cid)\
            .join(Influencer, Influencer.user_id == Sponsor_Requests.inf)\
            .join(Sponsor, Sponsor.user_id == Sponsor_Requests.sp)\
            .all()

        return render_template('admin_adreq.html', in_req = in_req, sp_req = sp_req, user_id = uid, role = "admin")


@app.route('/flag/<int:role>/<int:uid>', methods = ['POST'])
def flag(uid, role):
    flag_user = Flagged_users(user_id = uid, role = role)
    db.session.add(flag_user)
    db.session.commit()
    return f"<h4>Flagged User {uid}</h4>"


@app.route('/unflag/<int:role>/<int:uid>', methods = ['POST'])
def unflag(uid, role):
    user = Flagged_users.query.filter_by(user_id = uid, role = role).delete()
    db.session.commit()
    return f"<h4>UnFlagged User {uid}</h4>"


#####################################################
#########################################################

@app.route('/handle_request/<int:cid>/<int:inf>/<string:action>', methods=['POST'])
def handle_request(cid, inf, action):
    request = Influencer_Requests.query.filter_by(cid=cid, inf=inf).first()
    
    if not request:
        return redirect(url_for('inf_dashboard', uname=inf, msg='Request not found.', status='error'))
    
    if action == 'accept':
        request.status = 1  # Accepted
        msg = 'Request accepted successfully.'
        status = 'success'
    elif action == 'reject':
        request.status = 2  # Rejected
        msg = 'Request rejected successfully.'
        status = 'success'
    else:
        return redirect(url_for('inf_dashboard', uname=inf, msg='Invalid action.', status='error'))
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))  # Log the error for debugging
        return redirect(url_for('inf_dashboard', uname=inf, msg='An error occurred while processing your request.', status='error'))
    
    return redirect(url_for('inf_dashboard', uname=inf, msg=msg, status=status))


@app.route('/camp_complete/<int:cid>/<int:inf>', methods = ['POST'])
def camp_complete(cid, inf):
    r1 = Influencer_Requests.query.filter_by(cid=cid, inf=inf).first()
    r2 = Sponsor_Requests.query.filter_by(cid=cid, inf=inf).first()

    if r1:
        r1.status = 3
        msg = 'Campaign marked as completed'
        status = 'success'
    if r2:
        r2.status = 3
        msg = 'Campaign marked as completed'
        status = 'success'
    else:
        return redirect(url_for('inf_dashboard', uname=inf, msg='Ad Request not found.', status='error'))
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))  # Log the error for debugging
        return redirect(url_for('inf_dashboard', uname=inf, msg='An error occurred while processing your request.', status='error'))
    
    return redirect(url_for('inf_dashboard', uname=inf, msg=msg, status=status))




@app.route('/influencer/<string:uname>', methods=['GET', 'POST'])
def inf_dashboard(uname):
    msg = request.args.get('msg')
    status = request.args.get('status')
    if request.method == 'GET':
        usr = Influencer.query.filter_by(user_id=int(uname)).first()
        sub = db.session.query(Influencer_Requests.cid).filter_by(inf=usr.user_id, status=0).subquery()
        new = db.session.query(Campaigns, Influencer_Requests.payment, Influencer_Requests.message)\
            .join(Influencer_Requests, Campaigns.cid == Influencer_Requests.cid)\
            .filter(Campaigns.cid.in_(select(sub)))\
            .filter(Influencer_Requests.inf == usr.user_id)\
            .all()

        subquery1 = db.session.query(Influencer_Requests.cid).filter_by(inf=usr.user_id, status=1)
        subquery2 = db.session.query(Sponsor_Requests.cid).filter_by(inf=usr.user_id, status=1)
        combined_subquery = subquery1.union(subquery2).subquery()
        active = db.session.query(Campaigns).filter(Campaigns.cid.in_(select(combined_subquery)), Campaigns.date_end >= datetime.now()).all()

        return render_template('profilein.html', user=usr, new=new, active=active, role="influencer", msg = msg, status = status)


@app.route('/sponsor/<string:uname>', methods=['GET', 'POST'])
def sp_dashboard(uname):
    msg = request.args.get('msg')
    status = request.args.get('status')
    if request.method == 'GET':
        usr = Sponsor.query.filter_by(user_id=int(uname)).first()
        active = Campaigns.query.filter(Campaigns.creator == usr.user_id, Campaigns.date_end >= datetime.now()).all()
        
        # Campaign ids for which sponsor has received requests
        sub = select(Sponsor_Requests.cid).filter_by(sp=usr.user_id, status=0).subquery()

        # Query for new requests
        new = db.session.query(Campaigns, Sponsor_Requests.payment, Sponsor_Requests.message, Influencer)\
            .join(Sponsor_Requests, Campaigns.cid == Sponsor_Requests.cid)\
            .join(Influencer, Influencer.user_id == Sponsor_Requests.inf)\
            .filter(Campaigns.cid.in_(select(sub)))\
            .filter(Sponsor_Requests.sp == usr.user_id)\
            .filter(Sponsor_Requests.status == 0)\
            .all()

        return render_template('profilesp.html', user=usr, active=active, new=new, role="sponsor", msg=msg, status=status)


@app.route('/c/<string:cid>')
def camp_influencers(cid):
    infs = Influencer_Requests.query.filter(Influencer_Requests.cid == cid).all()
    infs += Sponsor_Requests.query.filter(Sponsor_Requests.cid == cid, Sponsor_Requests.status != 2).all()
    return render_template('sp_extra.html', content = infs)

@app.route('/handle_sp_request/<int:cid>/<int:inf>/<string:action>', methods=['POST'])
def handle_sp_request(cid, inf, action):
    request = Sponsor_Requests.query.filter_by(cid=cid, inf=inf).first()
    
    if not request:
        return redirect(url_for('sp_dashboard', uname=inf, msg='Request not found.', status='error'))
    
    if action == 'accept':
        request.status = 1  # Accepted
        msg = 'Request accepted successfully.'
        status = 'success'

    elif action == 'reject':
        request.status = 2  # Rejected
        msg = 'Request rejected successfully.'
        status = 'success'

    else:
        return redirect(url_for('sp_dashboard', uname=inf, msg='Invalid action.', status='error'))
    
    try:
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(str(e))  # Log the error for debugging
        return redirect(url_for('sp_dashboard', uname=inf, msg='An error occurred while processing your request.', status='error'))
    
    return redirect(url_for('sp_dashboard', uname=inf, msg=msg, status=status))


@app.route('/influencer/find/<string:uid>')
def ifind(uid):
    if request.method == "GET":
        search = request.args.get("search")
        if search:
            cmp = Campaigns.query.filter(Campaigns.cname.like(search)).all()
            cmp += Campaigns.query.filter(Campaigns.niche.like(search)).all()
            cmp += Campaigns.query.filter(Campaigns.description.like(search)).all()
        else:
            cmp = Campaigns.query.filter_by(visibility="public")
    influencer = Influencer.query.filter_by(user_id = int(uid)).first()
    return render_template('infind.html', content = cmp, influencer = influencer)
   
@app.route('/camp_request', methods=['POST'])
def camp_request():
    data = request.json
    influencer_id = data.get('influencer_id')
    campaign_id = data.get('campaign_id')
    campaign = Campaigns.query.filter_by(cid = campaign_id).first()
    sponsor_id = campaign.creator
    payment = data.get('payment')
    message = data.get('message')
    
    if influencer_id and campaign_id and sponsor_id and payment:
        new_request = Sponsor_Requests(
            cid=campaign_id,
            inf=influencer_id,
            sp=sponsor_id,
            payment=payment,
            message=message,
            status=0  # 0 for pending
        )

        db.session.add(new_request)
        db.session.commit()
        return jsonify({"success": True, "message": "Request sent successfully"}), 200
    else:
        print(influencer_id, campaign_id, payment, message)
        return jsonify({"success": False, "message": "Missing required data"}), 400


@app.route('/sponsor/find/<string:cname>')
def sfind(cname):
    if request.method == "GET":
        camp = Campaigns.query.filter_by(cname).first()
        search = request.args.get("search")
        if search:
            print(search)
            content = Influencer.query.filter(Influencer.user_name.like(search)).all()
            content += Influencer.query.filter(Influencer.fname.like(search)).all()
            content += Influencer.query.filter(Influencer.niche.like(search)).all()
            content += Influencer.query.filter(Influencer.age.like(search)).all()
        else:
            content = Influencer.query.all()
        

        return render_template('spfind.html', content = content, campaign = camp)


@app.route('/send_request', methods=['POST'])
def send_request():
    data = request.json
    influencer_id = data.get('influencer_id')
    campaign_id = data.get('campaign_id')
    sponsor_id = data.get('sponsor_id')
    payment = data.get('payment')
    message = data.get('message')
    
    if influencer_id and campaign_id and sponsor_id and payment:
        new_request = Influencer_Requests(
            cid=campaign_id,
            inf=influencer_id,
            sp=sponsor_id,
            payment=payment,
            message=message,
            status=0  # 0 for pending
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"success": True, "message": "Request sent successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Missing required data"}), 400


@app.route('/add/<string:uname>', methods  = ['GET', 'POST'])
def add_camp(uname):
    sp = Sponsor.query.filter_by(user_id = int(uname)).first()

    if request.method == "POST":
        cname = request.form['cname']
        desc = request.form['desc']
        niche = request.form['niche']
        budget = request.form['budget']
        req = request.form['req']
        vis = request.form['vis']
        camp = Campaigns(cname = cname, description = desc, niche = niche, budget = budget, requirements = req, visibility = vis, creator = sp.user_id)
        db.session.add(camp)
        db.session.commit()
        camp = Campaigns.query.filter_by(cname = cname, description = desc, niche = niche, budget = budget, creator = sp.user_id).first()
        campid = str(camp.cid)
        return redirect(url_for('sfind', cname = campid))
    
    return render_template('addcamp.html', user = sp)



###############################################################################
############################   STATS PAGE   ###################################
###############################################################################


@app.route('/stats/<string:user_type>/<int:user_id>')
def stats(user_type, user_id):
     
    chart_data = {}
    is_admin = False

    if user_type == 'influencer':
        influencer = Influencer.query.filter_by(user_id = user_id).first()
        if not influencer:
            return "Influencer not found", 404
        
        # Chart 1: Campaign requests over time
        thirty_days_ago = datetime.now() - timedelta(days=30)
        requests_data = db.session.query(
            func.date(Campaigns.date_created).label('date'),
            func.count(Influencer_Requests.rid).label('count')
        ).join(Influencer_Requests, Influencer_Requests.cid == Campaigns.cid)\
         .filter(
            Influencer_Requests.inf == user_id,
            Campaigns.date_created >= thirty_days_ago
         ).group_by(func.date(Campaigns.date_created)).all()

        chart_data['chart1'] = {
            'type': 'line',
            'data': {
                'labels': [str(r.date) for r in requests_data],
                'datasets': [{
                    'label': 'Campaign Requests',
                    'data': [r.count for r in requests_data],
                    'fill': False,
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                }]
            }
        }

        # Chart 2: Request status distribution
        status_data = db.session.query(
            Influencer_Requests.status,
            func.count(Influencer_Requests.rid)
        ).filter(Influencer_Requests.inf == user_id).group_by(Influencer_Requests.status).all()

        chart_data['chart2'] = {
            'type': 'pie',
            'data': {
                'labels': ['Pending', 'Accepted', 'Rejected', 'Completed'],
                'datasets': [{
                    'data': [next((count for status, count in status_data if status == i), 0) for i in range(4)],
                    'backgroundColor': ['#FFCE56', '#36A2EB', '#FF6384', '#4BC0C0']
                }]
            }
        }

    elif user_type == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id = user_id).first()
        if not sponsor:
            return "Sponsor not found", 404
        
        # Chart 1: Active campaigns over time
        thirty_days_ago = datetime.now() - timedelta(days=30)
        campaign_data = db.session.query(
            func.date(Campaigns.date_created).label('date'),
            func.count(Campaigns.cid).label('count')
        ).filter(
            Campaigns.creator == user_id,
            Campaigns.date_created >= thirty_days_ago
        ).group_by(func.date(Campaigns.date_created)).all()

        chart_data['chart1'] = {
            'type': 'line',
            'data': {
                'labels': [str(r.date) for r in campaign_data],
                'datasets': [{
                    'label': 'Active Campaigns',
                    'data': [r.count for r in campaign_data],
                    'fill': False,
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                }]
            }
        }

        # Chart 2: Influencer requests by niche
        niche_data = db.session.query(
            Influencer.niche,
            func.count(Sponsor_Requests.rid)
        ).join(Sponsor_Requests, Sponsor_Requests.inf == Influencer.user_id)\
         .filter(Sponsor_Requests.sp == user_id)\
         .group_by(Influencer.niche).all()

        chart_data['chart2'] = {
            'type': 'bar',
            'data': {
                'labels': [niche for niche, _ in niche_data],
                'datasets': [{
                    'label': 'Influencer Requests by Niche',
                    'data': [count for _, count in niche_data],
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)'
                }]
            }
        }

    elif user_type == 'admin':
        admin = Admin.query.filter_by(user_id = user_id).first()
        if not admin:
            return "Admin not found", 404
        
        is_admin = True
        
        # Chart 1: New campaigns over time
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_campaigns_data = db.session.query(
            func.date(Campaigns.date_created).label('date'),
            func.count(Campaigns.cid).label('count')
        ).filter(Campaigns.date_created >= thirty_days_ago)\
         .group_by(func.date(Campaigns.date_created)).all()

        chart_data['chart1'] = {
            'type': 'line',
            'data': {
                'labels': [str(r.date) for r in new_campaigns_data],
                'datasets': [{
                    'label': 'New Campaigns',
                    'data': [r.count for r in new_campaigns_data],
                    'borderColor': 'rgb(75, 192, 192)',
                    'fill': False
                }]
            }
        }

        # Chart 2: Campaign distribution by industry
        industry_data = db.session.query(
            Sponsor.industry,
            func.count(Campaigns.cid)
        ).join(Campaigns, Campaigns.creator == Sponsor.user_id)\
         .group_by(Sponsor.industry).all()

        chart_data['chart2'] = {
            'type': 'pie',
            'data': {
                'labels': [industry for industry, _ in industry_data],
                'datasets': [{
                    'data': [count for _, count in industry_data],
                    'backgroundColor': [f'hsl({i * 360 / len(industry_data)}, 70%, 50%)' for i in range(len(industry_data))]
                }]
            }
        }

        # Chart 3: Request status distribution
        status_data = db.session.query(
            Sponsor_Requests.status,
            func.count(Sponsor_Requests.rid)
        ).group_by(Sponsor_Requests.status).all()

        chart_data['chart3'] = {
            'type': 'bar',
            'data': {
                'labels': ['Pending', 'Accepted', 'Rejected', 'Completed'],
                'datasets': [{
                    'label': 'Request Status Distribution',
                    'data': [next((count for status, count in status_data if status == i), 0) for i in range(4)],
                    'backgroundColor': ['#FFCE56', '#36A2EB', '#FF6384', '#4BC0C0']
                }]
            }
        }

        # Chart 4: Top 10 influencers by reach
        top_influencers = Influencer.query.order_by(Influencer.reach.desc()).limit(10).all()

        chart_data['chart4'] = {
            'type': 'horizontalBar',
            'data': {
                'labels': [inf.user_name for inf in top_influencers],
                'datasets': [{
                    'label': 'Top Influencers by Reach',
                    'data': [inf.reach for inf in top_influencers],
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)'
                }]
            },
            'options': {
                'indexAxis': 'y'
            }
        }

    else:
        return "Invalid user type", 400

    return render_template('stats.html', chart_data=chart_data, is_admin=is_admin, user_type=user_type, user_id=user_id)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()