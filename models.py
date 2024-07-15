from db import db
from datetime import datetime, timedelta

class Influencer(db.Model):
    __tablename__ = "influencer_user_info"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String, nullable = False)
    email =  db.Column(db.String, nullable = False)
    fname = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    reach =  db.Column(db.Integer, nullable = False)
    link =  db.Column(db.String, nullable = False)
    age =  db.Column(db.Integer, nullable = False)
    niche =  db.Column(db.String, nullable = False)
    sp_requests=db.relationship("Sponsor_Requests",backref="influencer_user_info")
    in_requests=db.relationship("Influencer_Requests",backref="influencer_user_info")



class Sponsor(db.Model):
    __tablename__ = "sponsor_user_info"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String, nullable = False)
    email =  db.Column(db.String, nullable = False)
    fname = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    link =  db.Column(db.String, nullable = False)
    cname =  db.Column(db.Integer, nullable = False)
    industry =  db.Column(db.String, nullable = False)
    sp_requests=db.relationship("Sponsor_Requests",backref="sponsor_user_info")
    campaigns=db.relationship("Campaigns",backref="sponsor_user_info")
    in_requests=db.relationship("Influencer_Requests",backref="sponsor_user_info")


class Admin(db.Model):
    __tablename__ = "admin_info"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)


class Campaigns(db.Model):       ## table for all campaigns
    __tablename__ = "campaigns"
    cid = db.Column(db.Integer, primary_key = True, autoincrement = True)
    cname = db.Column(db.String, nullable = False)
    budget = db.Column(db.Integer, nullable = False)
    niche = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    requirements = db.Column(db.String, nullable = False)
    creator = db.Column(db.Integer,db.ForeignKey("sponsor_user_info.user_id"),nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_end = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=30))
    visibility = db.Column(db.String, default="public")
    sp_requests=db.relationship("Sponsor_Requests",backref="campaigns")
    in_requests=db.relationship("Influencer_Requests",backref="campaigns")
    


class Sponsor_Requests(db.Model):    ## requests from influencer to sponsor
    __tablename__ = "sp_requests"
    rid = db.Column(db.Integer, primary_key = True, autoincrement = True)
    cid = db.Column(db.Integer,db.ForeignKey("campaigns.cid"),nullable=False)
    payment = db.Column(db.Integer, nullable = False)
    message = db.Column(db.String, nullable = True)
    status = db.Column(db.Integer,nullable=False) ## 0 > pending, 1 > accepted, 2 > rejected
    sp = db.Column(db.Integer,db.ForeignKey("sponsor_user_info.user_id"),nullable=False)
    inf = db.Column(db.Integer,db.ForeignKey("influencer_user_info.user_id"),nullable=False)



class Influencer_Requests(db.Model):   ## requests from sponsor to influencer
    __tablename__ = "in_requests"
    rid = db.Column(db.Integer, primary_key = True, autoincrement = True)
    cid = db.Column(db.Integer,db.ForeignKey("campaigns.cid"),nullable=False)
    inf = db.Column(db.Integer,db.ForeignKey("influencer_user_info.user_id"),nullable=False)
    sp = db.Column(db.Integer,db.ForeignKey("sponsor_user_info.user_id"),nullable=False)
    payment = db.Column(db.Integer, nullable = False)
    message = db.Column(db.String, nullable = True)
    status = db.Column(db.Integer,nullable=False)

