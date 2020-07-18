from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

@login.user_loader
def load_user(id):
    return User.query.get(id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    date_joined = db.Column(db.Date)
    password_hash = db.Column(db.String(128))
    verified = db.Column(db.Boolean(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)    


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    position = db.Column(db.String(32))
    machine_certified = db.Column(db.Boolean(128), default=False)
    date_joined = db.Column(db.Date)

    def days_employed(self):
        date_today = date.today()
        return (date_today - self.date_joined).days

    def __repr__(self):
        return '<Member {}>'.format(self.name)    


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    assignments = db.Column(db.Integer)


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    processed_samples = db.relationship('ProcessedSamples', backref=db.backref('shift', lazy=True))


class ProcessedSamples(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_date = db.Column(db.Date)
    quantity = db.Column(db.Integer)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    

class AssignedMemberToStations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assigned_date = db.Column(db.Date)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    station = db.relationship('Station', backref=db.backref('member_assignment', lazy=True))
    member = db.relationship('Member', backref=db.backref('station_assignment', lazy=True))


class AssignedMemberToShift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assigned_date = db.Column(db.Date)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    shift = db.relationship('Shift', backref=db.backref('member_assignment', lazy=True))
    member = db.relationship('Member', backref=db.backref('shift_assignment', lazy=True))
	
	
class Retests(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sample_id = db.Column(db.String(64))
	plate_id = db.Column(db.String(64))
	well = db.Column(db.String(32))
	fam = db.Column(db.Numeric(10,2))
	vic = db.Column(db.Numeric(10,2))
	analyst = db.Column(db.String(64))
	retest_type = db.Column(db.String(64))
	reason = db.Column(db.String(512))
	remarks = db.Column(db.String(512))
	admin_comment = db.Column(db.String(512))	
	
	
class RunSummary(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	plate_id = db.Column(db.String(64))
	shift = db.Column(db.String(64))
	blank_lot = db.Column(db.String(64))
	pc_lot = db.Column(db.String(64))
	sample_dispensing = db.Column(db.String(64))
	verifier = db.Column(db.String(64))
	dispensing_start = db.Column(db.DateTime)
	dispensing_finish = db.Column(db.DateTime)
	sample_qty = db.Column(db.Integer)
	extraction_rgt_lot = db.Column(db.String(64))
	machine_id = db.Column(db.Integer)
	plate_load_time = db.Column(db.DateTime)
	mlb_load_time = db.Column(db.DateTime)
	qpcr_mix_lot = db.Column(db.String(64))
	mgisp_tips_lot = db.Column(db.String(64))
	machine_operator = db.Column(db.String(64))
	
	
class RunSummary1(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	plate_id = db.Column(db.String(64))
	shift = db.Column(db.String(64))
	blank_lot = db.Column(db.String(64))
	pc_lot = db.Column(db.String(64))
	sample_dispensing = db.Column(db.String(64))
	verifier = db.Column(db.String(64))
	dispensing_start = db.Column(db.Time)
	dispensing_finish = db.Column(db.Time)
	sample_qty = db.Column(db.Integer)
	extraction_rgt_lot = db.Column(db.String(64))
	machine_id = db.Column(db.Integer)
	plate_load_time = db.Column(db.Time)
	mlb_load_time = db.Column(db.Time)
	qpcr_mix_lot = db.Column(db.String(64))
	mgisp_tips_lot = db.Column(db.String(64))
	machine_operator = db.Column(db.String(64))