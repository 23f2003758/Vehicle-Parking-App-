from flask_login import UserMixin
from .database import db
from datetime import datetime as dt

class mtr_usr(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    user_role = db.Column(db.Integer(), nullable=False) # 0 = admin, 1 = user
    admin = db.relationship('admin', backref='mtr_usr')
    user = db.relationship('user', backref='mtr_usr')
    
    
    def get_id(self):
        return str(self.id)
    
class admin(UserMixin, db.Model): #user role = 0
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer(), db.ForeignKey('mtr_usr.id'), nullable=False)
        
class user(db.Model): #user role = 1
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('mtr_usr.id'), nullable=False)
    
       
class parking_spot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    lot_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer(), db.ForeignKey('admin.id'), nullable=False)
   
class parking_lot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.Integer(), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer(), nullable=False)
    admin_id = db.Column(db.Integer(), db.ForeignKey('admin.id'), nullable=False)
   
    
       
class reserve_parking_spot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    parking_spot_id = db.Column(db.Integer(), db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(100), nullable=False)
    parking_time = db.Column(db.DateTime(), nullable=False)
    leaving_time = db.Column(db.DateTime(), nullable=False)
    parking_cost_per_hour = db.Column(db.Integer(), nullable=False)
    
    