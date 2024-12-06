from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_PERMANENT']=True
app.config['SESSION_TYPE']='filesystem'
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret key'
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String(15), nullable=False)
    type = db.Column(db.Integer, nullable=False, default=0) #  0 = normal, 1=admin

    def __init__(self, username, email, first_name, last_name, password, type=0):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.type = type

    def check_pass(self, password):
        return password== self.password

    def __repr__(self):
        return f"{self.username} - {self.first_name}"


class Busses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_name = db.Column(db.String(10), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    dest = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"{self.bus_name} - {self.source} to {self.dest}"


@app.route("/bus", methods=['GET','POST'])
def bus():
    if session.get('user_id')==None:
        return redirect('/')
    if session.get('type')==0:
        return redirect('/dashboard')
    
    if request.method == 'POST':
        bus_name = request.form['bus_name']
        source = request.form['source']
        destination = request.form['destination']
        time = request.form['time']

        bus = Busses(bus_name=bus_name, source=source, dest=destination, time=time)
        db.session.add(bus)
        db.session.commit()
        return redirect('/')

    bus = Busses.query.all()
    return render_template("index.html", bus=bus)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        password = request.form['password']

        user = Users(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')

    allusers = Users.query.all()
    return render_template("signup.html", allusers=allusers)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    print(session)
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('user_id')!=None:
        return redirect('/dashboard')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user and user.check_pass(password):
           

            session['user_id'] = user.id
            session['username'] = user.username
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['email'] = user.email
            session['type'] = user.type

            return redirect('/dashboard')
        else:
            flash("Invalid Username or Password")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if session.get('user_id')==None:
        return redirect('/')
    
    username = session['username']
    user = Users.query.filter_by(username=username).first()
    return render_template("dashboard.html", user=user)

# @app.route("/update/<int:sno>", methods=['GET', 'POST'])
# def update(sno):
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         first_name = request.form['first-name']
#         last_name = request.form['last-name']
#         password = request.form['password']

#         user = Users.query.filter_by(sno=sno).first()
#         user.username = username
#         user.email = email
#         user.first_name = first_name
#         user.last_name = last_name
#         user.password = password 

#         db.session.add(user)
#         db.session.commit()
#         return redirect('/')

#     user = Users.query.filter_by(sno=sno).first()
#     return render_template("update.html", user=user)


def create_db():
    with app.app_context():
        print("Creating tables...")
        try:
            db.create_all() 
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {e}")


if __name__ == "__main__":
    create_db()  
    app.run(debug=True)
