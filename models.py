from app import db, app
from datetime import datetime

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120), unique=True, nullable=False)
    address =   db.Column(db.String(200))
    pin_code =  db.Column(db.String(200))  
    reserve_parking_spot = db.relationship('reserve_parking_spot', backref='user')  
        
class parking_lot(db.Model):  # user role = 0
    id = db.Column(db.Integer(), primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(100),unique=True ,nullable=False)
    pin_code = db.Column(db.Integer(), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer(), nullable=False)
    available_spots = db.Column(db.Integer(), nullable=False)
    
        
        
class parking_spot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    spot_number = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    lot_id = db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    
class reserve_parking_spot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    parking_spot_id = db.Column(db.Integer())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(100), nullable=False)
    parking_time = db.Column(db.DateTime(), nullable=False)
    leaving_time = db.Column(db.DateTime())
    parking_cost_per_hour = db.Column(db.Integer())
    total_cost = db.Column(db.Integer()) 
    total_duration = db.Column(db.Integer()) 
    user_name = db.Column(db.String(100))
    lot_id = db.Column(db.Integer())
    


def init_db(*args,**kwargs):
    if not user.query.filter_by(id=1).first():
        admin = user(id=1, username='Admin', password='1234', full_name='Admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin created.")
    else:
        print("Admin already exists.")

               
def create_tables():
    with app.app_context():
        db.create_all()
        init_db()  

create_tables()