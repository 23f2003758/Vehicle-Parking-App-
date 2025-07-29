from flask import  render_template, request, session, redirect, flash, url_for
from flask_login import login_required
from datetime import datetime
from functools import wraps
from app import db, app
from models import *
import matplotlib 
matplotlib.use('agg')
import matplotlib.pyplot as plt




#==========================================AUTHORIZATION==================================#


#=== ADMIN CHECK ===#

def admin_required(f):
    @wraps(f)
    @login_required
    def inner_func(*args,**kwargs): 
        if session['user_id']!=1:
            flash('Unauthorized Access!','danger')
            return redirect('/')
        return f(*args,**kwargs) 
    return inner_func


#====== USER CHECK ======#


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):  
            flash('Please Log In!', 'danger')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


#================================ ROUTES ===================================#


#==== LANDING PAGE =====#

@app.route('/')
def home():
    return render_template('home.html') 




#==== SIGNUP PAGE =====#

@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template('Signup_page.html')
        
    else:
       
        username = request.form.get("username") 
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        address =  request.form.get("address")
        pin_code =  request.form.get("pin_code")

        if username.isspace() or password.isspace() or fullname.isspace() or address.isspace() or pin_code.isspace(): 
            flash("Can't have empty fields!", "danger") 
            return redirect("/signup")

        if user.query.filter_by(username=username).first():  
            flash("User already exists!", "danger")
            return redirect("/signup")
        
        if len(pin_code) != 6:
            flash("Pincode must be 6 digit!", "warning")
            return redirect("/signup")
        
        new_user = user(username=username,password=password,full_name=fullname,address=address,pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.","success")
        return redirect("/login")
    
    
    
#==== LOGIN PAGE =====#



@app.route("/login", methods=["GET","POST"])
def login():
   
    entered_username = request.form.get("username")
    entered_password = request.form.get("password")
    User = user.query.filter_by(username=entered_username).first()  
    
    
    if request.method=="GET":
        return render_template('login.html')

    elif entered_username=="Admin" and entered_password=='1234': 
        flash("Welcome Admin!","success")
        session['user_id']=User.id
        return redirect(url_for("admin_dash"))
    

    elif entered_username=="Admin" and entered_password!='1234':
        flash("Enter correct password !","danger")
        return redirect("/login")
    else:
        if User:
            if User.password == entered_password:  
                flash("Login Successful !", "success")
                session['user_id']=User.id
                uid = User.id
                return redirect(url_for("user_dash",uid=uid))
            else:
                flash("Password incorrect, Try again!", "danger")
                return redirect("/login")
        
        else:
            flash("Please Sign Up!", "danger")
            return redirect("/signup")



#===================== ADMIN ROUTES ========================#

#======== ADMIN DASHBOARD ========#

@app.route('/admin_dash', methods=['GET', 'POST'])
@admin_required
def admin_dash():
    Users = user.query.all()
    new_lots = parking_lot.query.all()
    return render_template('admin_dashboard.html', Users=Users, new_lots=new_lots)



#============== CRUD OPERATIONS ==================#

#======= ADD Parking Lot ========#

#=====CREATE


@app.route('/add_parking_lot', methods = ['GET', 'POST'])
@admin_required
def add_parking_lot():
    if request.method == 'POST':
        prime_location_name = request.form.get("prime_location_name")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        price = int(request.form.get("price"))
        
        if parking_lot.query.filter_by(address=address).first():  # checking if address already exists in the database.
            flash("Address already exists!", "warning")
            return render_template("add_parking_lot.html")
            
        if len(pin_code) != 6:
            flash("Pincode must be 6 digit!", "warning")
            return render_template("add_parking_lot.html")
        
       
        if price <= 0:
            flash("Price cannot be zero or negative!","warning")
            return render_template("add_parking_lot.html")
        
        maximum_number_of_spots = int(request.form.get("max_spots"))
        if maximum_number_of_spots <= 0:
            flash("Maximum parking spots cannot be zero or negative!","warning")
            return render_template("add_parking_lot.html")
        
        new_lot = parking_lot(prime_location_name=prime_location_name, address=address, pin_code=pin_code, price=price, maximum_number_of_spots=maximum_number_of_spots,available_spots=maximum_number_of_spots)
        db.session.add(new_lot)
        db.session.commit()
        
        for i in range(1, maximum_number_of_spots+1):
            new_spot = parking_spot(status="Unoccupied", spot_number=i, lot_id=new_lot.id)
            db.session.add(new_spot)
            db.session.commit()
        flash("Parking Lot added successfully" , "success")
        return redirect('/admin_dash')  
    
    return render_template("add_parking_lot.html")


#====READ


@app.route('/view_lot/<int:id>')
@admin_required
def view_parking_spots(id):
    
    
    lots = parking_lot.query.get(id)
    spots = parking_spot.query.filter_by(lot_id=id).order_by(parking_spot.spot_number).all()           
    reserve = reserve_parking_spot.query.filter_by(lot_id=id)
    
    return render_template('view_parking_spots.html', lot=lots, spots=spots, reserve=reserve)


#=======UPDATE


@app.route('/edit_lot/<int:id>', methods = ['GET', 'POST'])
@admin_required
def edit_lot(id):
    Parking_lot = parking_lot.query.get(id)
    spot = parking_spot.query.filter_by( lot_id= id).all()
    Old_max = Parking_lot.maximum_number_of_spots
    history = reserve_parking_spot.query.filter_by(lot_id = id).group_by(reserve_parking_spot.parking_spot_id).all()
    empty = True
    for s in spot:
        if s.status =="Occupied":
            empty = False
            break
            
    if empty:
    
        if request.method == 'POST':
            prime_location_name = request.form.get("prime_location_name")
            address = request.form.get("address")
            pin_code = request.form.get("pin_code")
            
            lot_active = parking_lot.query.filter_by(address=address).first() 
            
            if lot_active and Parking_lot.id != lot_active.id :  # checking if address already exists in the database.
                flash("Address already exists!", "warning")
                return render_template("add_parking_lot.html")
           
            if len(pin_code) != 6:
                flash("Pincode must be 6 digit!", "warning")
                return render_template("edit_parking_lot.html",id=id,Parking_lot=Parking_lot)
            
            price = int(request.form.get("price"))
            if price <= 0:
                flash("Price cannot be zero or negative!","warning")
                return render_template("edit_parking_lot.html",id=id,Parking_lot=Parking_lot)
            maximum_number_of_spots = int(request.form.get("max_spots"))
            
            if maximum_number_of_spots <= 0:
                flash("Maximum parking spots cannot be zero or negative!","warning")
                return render_template("edit_parking_lot.html",id=id,Parking_lot=Parking_lot)
              
            if maximum_number_of_spots <len(history):
                flash("Maximum number of spots cannot be less than previously reserved spot.","danger")  
                return render_template("edit_parking_lot.html",id=id,Parking_lot=Parking_lot)
            
            Parking_lot.prime_location_name = prime_location_name
            Parking_lot.address = address
            Parking_lot.pin_code = pin_code
            Parking_lot.price = price
            Parking_lot.maximum_number_of_spots = maximum_number_of_spots
            Parking_lot.available_spots = maximum_number_of_spots
            
            if maximum_number_of_spots != Old_max:
                 
                diff = int(maximum_number_of_spots-Old_max)
            
                if diff<0:      
                    spots = parking_spot.query.filter_by(lot_id=id).order_by(parking_spot.spot_number.desc()).limit(abs(diff)).all()
                    for spot in spots:
                        db.session.delete(spot)
                        
                else:
                    last_spots = parking_spot.query.filter_by(lot_id=id).order_by(parking_spot.spot_number.desc()).first()
                    last_spot_no = last_spots.spot_number        
                    for i in range(1,diff+1):
                        New_spot = parking_spot(status="Unoccupied",spot_number = last_spot_no+i, lot_id = id)
                        db.session.add(New_spot)

                    
            db.session.add(Parking_lot)
            db.session.commit()
            flash("Lot Edit Successfully","info")
            return redirect('/admin_dash')
        return render_template("edit_parking_lot.html", Parking_lot=Parking_lot,history=history)

    else:
        flash ( "Occupied Lots cannot be edited ","danger")
        
    return redirect('/admin_dash')  




#======DELETE


@app.route('/delete_lot/<int:id>')
@admin_required
def delete_lot(id):
    
    occupied_spot = parking_spot.query.filter_by(lot_id=id, status="Occupied").first()    
    if occupied_spot:
        flash("Parking lot cannot be deleted as it has occupied spots!", "danger")
        return redirect(url_for('admin_dash'))

    reservation_history = reserve_parking_spot.query.filter_by(lot_id=id).first()
    if reservation_history:
        flash("Cannot delete Parking Lot as it has reservation history.", "danger")
        return redirect(url_for('admin_dash'))

    
    lot_to_delete = parking_lot.query.get(id) 
    if lot_to_delete:
        parking_spot.query.filter_by(lot_id=id).delete() 
        db.session.delete(lot_to_delete)
        db.session.commit()
        flash("Parking Lot and all its spots have been deleted!", "info")
    else:
       
        flash("Parking Lot not found.", "warning")

    return redirect(url_for('admin_dash'))



#=========ADMIN USER==========#

@app.route('/admin_user', methods=['GET', 'POST'])
@admin_required
def admin_user():
    cust = user.query.all()
    
    return render_template("admin_user.html", cust=cust)



#============ ADMIN SUMMARY ===========#


@app.route('/admin_summary', methods=['GET', 'POST'])
@admin_required
def admin_summary():
    history = reserve_parking_spot.query.all()
   
    total = 0
    
    for booking in history:
        if booking.total_cost :
            total+=booking.total_cost
    
    
#==CHART===#

#CHART-01


    lots = parking_lot.query.all()
    location_id = [lot.id for lot in lots]
    maximum_spots = [lot.maximum_number_of_spots for lot in lots]
   
    plt.clf()
    plt.figure(figsize=(10, 8))
    plt.bar(location_id, maximum_spots, color='#FFA500', width=0.5, align='center' )
    plt.xticks(location_id)
    plt.title('Maximum Number of Spots per Parking Lot', fontsize=10)
    plt.ylabel('Maximum Number of Spots', fontsize=18)
    plt.xlabel('Parking Lot Location', fontsize=25)
    plt.tick_params(axis='x', labelsize=25) 
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('static/admin_chart.png')
    plt.close()
    


#CHART-02
    cost_by_lot = db.session.query(
    reserve_parking_spot.lot_id,db.func.sum(reserve_parking_spot.total_cost)).filter(reserve_parking_spot.total_cost.isnot(None)).group_by(reserve_parking_spot.lot_id).all()

    lot_ids = [item[0] for item in cost_by_lot]
    total_costs = [item[1] for item in cost_by_lot]
    plt.clf()  
    plt.figure(figsize=(9, 7)) 
    plt.bar(lot_ids, total_costs, color='#FFA500', align='center',width=0.5)   
    plt.title('Total Parking Cost per Lot ID', fontsize=20)
    plt.xlabel('Lot ID', fontsize=25)
    plt.ylabel('Total Cost', fontsize=18)
    plt.tick_params(axis='x', labelsize=25) 
   
    plt.xticks(lot_ids)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('static/admin_chart2.png')
    plt.close()

    return render_template("admin_summary.html", history=history,total=total)



#===================== USER ROUTES ========================#

#======== USER DASHBOARD ========#

@app.route('/user_dash/<int:uid>', methods=['GET', 'POST'])
@login_required
def user_dash(uid):
    cust = user.query.filter_by(id=uid).first()
    parking_spots = reserve_parking_spot.query.filter_by(user_id=uid).all() #showing active & past spot
    parking_lots = parking_lot.query.all()
    return render_template('user_dashboard.html',parking_spots=parking_spots,parking_lots=parking_lots,cust=cust,uid=uid )



#===========Booking Spot==========#

@app.route('/booking/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def booking(lot_id):
    spot = parking_spot.query.filter_by(lot_id=lot_id, status="Unoccupied").first()
    spot_id = spot.id
    lot = parking_lot.query.filter_by(id=lot_id).first()
    price = lot.price
    id = session['user_id']
    
    if request.method == 'POST':
        
        vehicle_number = request.form.get('vehicle_number')
        if not vehicle_number or vehicle_number.isspace():
            flash("Vehicle number cannot be empty!", "danger")   
            return render_template('booking.html', lot_id=lot_id, spot_id=spot_id, uid=id)
        
        user_name = user.query.filter_by(id = id).first()
        parking_time = datetime.now()
        new_booking = reserve_parking_spot(vehicle_number=vehicle_number, parking_time=parking_time, user_id= id , parking_spot_id = spot_id, parking_cost_per_hour=price,user_name=user_name.username,lot_id = lot_id)
        spot.status = "Occupied"
        db.session.add(new_booking)
        lot.available_spots -= 1
        db.session.commit()
        flash("Spot Booked!!","info")
        return redirect(url_for('user_dash', uid=id))
        
    return render_template('booking.html', lot_id=lot_id, spot_id=spot_id , uid=id)


#=============Release Parking Spot============#

@app.route('/release_parking_spot/<int:booking_id>', methods = ['GET', 'POST'])
@login_required
def release_parking_spot(booking_id):
    booking = reserve_parking_spot.query.filter_by(id=booking_id).first()
    start_time = booking.parking_time
    rate = booking.parking_cost_per_hour
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    total_duration = round(duration / 3600, 2)
    total_price = round(total_duration * rate, 1)
 
    if request.method == 'POST':
        booking.leaving_time = datetime.now()
        booking.total_duration = duration
        booking.total_cost = total_price
        spot = parking_spot.query.filter_by(id=booking.parking_spot_id).first()
        lot = parking_lot.query.filter_by(id=spot.lot_id).first()
        lot.available_spots += 1
        spot.status = "Unoccupied"
        db.session.commit()
        
        flash("Spot Released!!","info")
        return redirect(url_for("user_dash", uid=session['user_id']))
    
    return render_template("release_booking.html", booking=booking, duration=duration, total_cost=total_price, leaving_time=datetime.now())



#=========== USER SUMMARY ==========#


@app.route('/summary/<int:uid>', methods=['GET', 'POST'])
@login_required
def user_summary(uid):
    cust = user.query.filter_by(id=uid).first()
    parking_spots = reserve_parking_spot.query.filter_by(user_id=uid).all()
    booking = reserve_parking_spot.query.filter_by(user_id=uid, leaving_time = None ).all()
    if parking_spots == booking:
        message = True
    else:
        message = False
    parking_lots = parking_lot.query.all()
    
#==== USER CHARTS ===#

#CHART-01


    reservations_by_user = db.session.query(reserve_parking_spot.vehicle_number,db.func.count(reserve_parking_spot.id) ).filter_by(user_id=uid).group_by(reserve_parking_spot.vehicle_number).all()

    vehicle_id = [f'vehicle no {item[0]}' for item in reservations_by_user]
    reservation_counts = [item[1] for item in reservations_by_user]
      
    plt.clf()  
    plt.figure(figsize=(8, 6))
    plt.pie(
    reservation_counts,         
    labels=vehicle_id,            
    autopct='%1.1f%%',          
    startangle=140,              
    shadow=True,                 
    pctdistance=0.85
    )
    plt.title('Proportion of Parking Reservations by User', fontsize=16)
    plt.savefig('static/user_chart.png')
    plt.close()
    plt.clf()
    
    
#CHART-02

    cost_by_vehicle = db.session.query(reserve_parking_spot.vehicle_number,db.func.sum(reserve_parking_spot.total_cost).label('total')).filter(reserve_parking_spot.total_cost.isnot(None)).filter_by(user_id=uid).group_by(reserve_parking_spot.vehicle_number).order_by(db.func.sum(reserve_parking_spot.total_cost).desc()).all() 
    
    vehicle_numbers = [item[0] for item in cost_by_vehicle]
    total_costs = [item[1] for item in cost_by_vehicle] 

    plt.clf()
    plt.figure(figsize=(8, 5))
    plt.bar(vehicle_numbers, total_costs, color='#FFA500')
    plt.title('Total Parking Cost by Vehicle Number', fontsize=16)
    plt.xlabel('Vehicle Number', fontsize=12)
    plt.ylabel('Total Cost', fontsize=12)
    plt.xticks(rotation=40, ha='right') 
    plt.grid(axis='y', linestyle='--', alpha=0.6) 
    plt.tight_layout()
    plt.savefig('static/user_chart2.png')
    plt.close()
    
    return render_template('user_summary.html',parking_spots=parking_spots,parking_lots=parking_lots,cust=cust,uid=uid ,message=message)
    
    
    
#===== LOGOUT ======#

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout Successfully!!!" , "info")
    return redirect ('/')

