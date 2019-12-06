from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quote_dash.db'
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
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False) 
    author = db.relationship('User', foreign_keys=[author_id], backref="posts") 
    created_at = db.Column(db.DateTime, server_default=func.now())   
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    saves_rec = db.relationship("User", secondary=saves_table)

    @property
    def num_saves(self):
        return len(self.saves_rec)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/new_user')
def create():
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
        return redirect('/search')

    return redirect("/")

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

# @app.route('/login')
# def login():

# @app.route('/search')
# def search():

# @app.route('/details')
# def details():


if __name__ == "__main__":
    app.run(debug=True)