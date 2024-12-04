from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret key'
db = SQLAlchemy(app)


class Users(db.Model):
    username = db.Column(db.String(10), primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String(15), nullable=False)

    def __init__(self, username, email, first_name, last_name, password):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_pass(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return f"{self.username} - {self.first_name}"


class Busses(db.Model):
    bus_no = db.Column(db.String(10), primary_key=True)
    u = db.Column(db.String(50), nullable=False)
    v = db.Column(db.String(30), nullable=False)
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)

    def __repr__(self):
        return f"{self.bus_no} - {self.u} to {self.v}"


@app.route("/")
def home():
    if request.method == 'POST':
        bus_no = request.form['bus-number']
        u = request.form['initial-location']
        v = request.form['final-location']
        from_date = request.form['from-date']
        to_date = request.form['to-date']

        bus = Busses(bus_no=bus_no, u=u, v=v, from_date=from_date, to_date=to_date)
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
        return redirect('/login')

    allusers = Users.query.all()
    return render_template("signup.html", allusers=allusers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']

    #     user = Users.query.filter_by(username=username).first()
    #     if user and user.check_pass(password):
    #         session['username'] = user.username
    #         session['first_name'] = user.first_name
    #         session['last_name'] = user.last_name
    #         session['email'] = user.email
    #         print(f"Session data after login: {session}")
    #         return redirect('/dashboard')
    #     else:
    #         return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


# @app.route("/update/<int:username>", methods=['GET','POST'])
# def update(username):
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         first_name = request.form['first-name']
#         last_name = request.form['last-name']
#         password = request.form['password']

#         user = Users.query.filter_by(username=username).first()
#         user.username = username
#         user.email = email
#         user.first_name = first_name
#         user.last_name = last_name
#         password = password

#         db.session.add(user)
#         db.session.commit()
#         return redirect(('/'))

#     user = Users.query.filter_by(username=username).first()
#     return render_template("update.html", user=user)


@app.route("/dashboard")
def dashboard():
    user = Users.query.filter_by(username=session['username']).first()
    return render_template("dashboard.html", user=user)


@app.route("/search")
def search():
    return redirect("/")


@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        password = request.form['password']

        user = Users.query.filter_by(sno=sno).first()
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.password = password 

        db.session.add(user)
        db.session.commit()
        return redirect('/')

    user = Users.query.filter_by(sno=sno).first()
    return render_template("update.html", user=user)


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
