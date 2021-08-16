from flask import Flask, render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, BotDash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '4e22253d8b1f38c1ffb9f44535d4bea1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #tracker = db.relationship('Tracker', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amountBought = db.Column(db.String(30), nullable=True)
    unitCost = db.Column(db.String(30), nullable=True)
    buySell = db.Column(db.String(10), nullable=True)
    dateTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Tracker('{self.amountBought}','{self.unitCost}', '{self.buySell}', '{self.dateTime}')"

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

buy = True

@app.route('/botdashboard', methods=['GET', 'POST'])
def bot():
    global buy
    if request.method == "POST":
        amount = '£300'
        unit = '£30000'

        if buy == True:
            tracker_amount_bought = Tracker(amountBought=amount, unitCost=unit, buySell='Buy')
            buy = False
        
        else:
            tracker_amount_bought = Tracker(amountBought=amount, unitCost=unit, buySell='Sell')
            buy = True

        try:
            db.session.add(tracker_amount_bought)
            db.session.commit()
            flash(f'Amount of stocks bought is {amount}!', 'success')
            return redirect(url_for('bot'))
        except:
            return 'There was an issue with the sale.'
    else:
        form = Tracker.query.order_by(Tracker.dateTime).all()
        return render_template('trading_bot.html', form=form)

@app.route('/delete')
def delete():
    try:
        db.session.query(Tracker).delete()
        db.session.commit()
        flash(f'Cleared tracking history!', 'success')
        return redirect(url_for('bot'))
    except:
        return 'There was a problem deleting'

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for { form.username.data }!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #test the login form
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('bot'))
        else:
            flash('Login unsuccessful, check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



if __name__== '__main__':
    app.run(debug=True)