from db import db

class Influencer(db.Model):
    __tablename__ = "influencer_user_info"
    user_id = db.Column(db.string, primary_key = True)
    user_name = db.Column(db.string, nullable = False)
    password = db.Column(db.string, nullable = False)


class Sponsor(db.Model):
    __tablename__ = "sponsor_user_info"
    user_id = db.Column(db.string, primary_key = True)
    user_name = db.Column(db.string, nullable = False)
    password = db.Column(db.string, nullable = False)


class Admin(db.Model):
    __tablename__ = "admin_info"
    user_id = db.Column(db.string, primary_key = True)
    user_name = db.Column(db.string, nullable = False)
    password = db.Column(db.string, nullable = False)

