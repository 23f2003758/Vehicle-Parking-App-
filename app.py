from flask import Flask
from flask_login import LoginManager
from application.database import db
import datetime

app = None

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.debug = True

    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.sqlite3'
    db.init_app(app)
    my_login_manager = LoginManager()
    my_login_manager.init_app(app)
    
    from application.models import mtr_usr, admin, user, parking_spot, parking_lot, reserve_parking_spot 
    with app.app_context():
        db.create_all()
        db.session.commit()
        
        
        admin_username = "Admin"
        admin_password = "1234"
        existing_master = mtr_usr.query.filter_by(username=admin_username, user_role=0).first()
        if not existing_master:
            master_admin = mtr_usr(username=admin_username, user_role=0)
            db.session.add(master_admin)
            db.session.commit()
            admin_entry = admin(username=admin_username, password=admin_password, admin_id=master_admin.id)
            db.session.add(admin_entry)
            db.session.commit()
        
# add the functionality to add the admin
# Create a new user first in the User Table and provide the user role as 0
# After that using the same user_id as foreign key create the Admin id in the Admin table
        

#
    
    @my_login_manager.user_loader
    def load_user(user_id):
        return user.query.get(int(user_id))
    
    app.app_context().push()
    return app

app = create_app()
from application.routes import *

if __name__ == '__main__':
    app.run(debug=True)
