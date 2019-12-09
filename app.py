from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neighborhood_iq.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "QaWsEdRfTgYh12345!!"

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

saves_table = db.Table('saves', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True), 
    db.Column('business_id', db.Integer, db.ForeignKey('business.id', ondelete="cascade"), primary_key=True)
)

class User(db.Model):	
    __tablename__ = "users"    		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())  
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    saves_made = db.relationship("Business", secondary=saves_table)

    def __repr__(self):
        return f"<User: {self.first_name}>"

class Business(db.Model):
    __tablename__ = "businesses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    info = db.Column(db.Text)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False) 
    user = db.relationship("User", foreign_keys=[users_id], backref="users", cascade="all") 
    created_at = db.Column(db.DateTime, server_default=func.now())   
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    saves_rec = db.relationship("User", secondary=saves_table)

    @property
    def num_saves(self):
        return len(self.saves_rec)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/new_user', methods=['POST'])
def new_user():
    errors = []

    if len(request.form['first_name']) < 2:
        errors.append("Your first name must be at least 2 characters long.")
        valid = False

    if len(request.form['last_name']) < 2:
        errors.append("Your last name must be at least 2 characters long.")
        valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        errors.append("Your email address is invalid. Please try again.")
        valid = False

    if len(request.form['password']) < 8:
        errors.append("Your password must be at least 8 characters long.")
        valid = False

    user_check = User.query.filter_by(email=request.form["email"]).first() 
    if user_check is not None:
        errors.append("Your email is already in use. Please log in.")
    
    if request.form['password'] != request.form['confirm']:
        errors.append("Your passwords must match. Please try again.")
        valid = False

    if errors:
        for e in errors:
            flash(e)
    else:
        hashed = bcrypt.generate_password_hash(request.form["password"])
        new_user = None

        new_user = User(
            first_name = request.form["first_name"],
            last_name = request.form["last_name"],
            email = request.form["email"],
            password = hashed
        )
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        return redirect('/saves')

    return redirect('/login')

@app.route('/myaccount/<user_id>')
def show(user_id):
    user = User.query.get(user_id)
    return render_template("edit.html", user=user)

@app.route('/myaccount/<user_id>/edit', methods=['POST'])
def edit(user_id):
    errors = []

    if len(request.form['first_name']) < 2:
        errors.append("Your first name must be at least 2 characters long.")
        valid = False

    if len(request.form['last_name']) < 2:
        errors.append("Your last name must be at least 2 characters long.")
        valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        errors.append("Your email address is invalid. Please try again.")
        valid = False

    if errors:
        for e in errors:
            flash(e)
    else:
        user = None
    
        user = User.query.get(user_id)
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        db.session.commit()
        return redirect('/search')

    return redirect('/')

@app.route('/user/login', methods=['POST'])
def user_login():
    errors = []

    user_attempt = User.query.filter_by(email=request.form["email"]).first()
    
    if not user_attempt:
        flash("Your email and password combination is incorrect.")
        return redirect("/login")

    if not bcrypt.check_password_hash(user_attempt.password, request.form["password"]):
        flash("Your email and password combination is incorrect.")
        return redirect("/login")

    session["user_id"] = user_attempt.id
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/saves')
def saves():
    if not "user_id" in session:
        return redirect("/")
    logged_in = User.query.get(session["user_id"])
    all_saves = Business.query.all() 
    return render_template("saves.html", user=logged_in, saves=all_saves)

# @app.route('/details')
# def details():

@app.route('/saves/<user_id>')
def add_save(business_id):
    user = User.query.get(session["user_id"])
    business = Business.query.get(business_id)
    user.saves_sent.append(business)
    db.session.commit()
    return redirect('/saves')

if __name__ == "__main__":
    app.run(debug=True)