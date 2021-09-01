from flask import Flask, render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from trading_bot.forms import RegistrationForm, LoginForm
from datetime import datetime
import trading_bot.bot_binance as b
import websocket, json, pprint, time, sys
import numpy as np
from binance.enums import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '4e22253d8b1f38c1ffb9f44535d4bea1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


closes = []
in_position = False
order_successful = False
rsi = []

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    global order_successful
    try:
        print("sending order")
        orderInfo = b.client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    
    order_successful = True
    return orderInfo

def on_open(ws):
    print("opened connection")

def on_close(ws):
    print("close connection")

def on_message(ws, message): # automated bot function that runs indefinitely
    global closes
    global in_position
    global order_successful
    global rsi
    print("received message")
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    if is_candle_closed:
        print("candle close at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > b.RSI_PERIOD:
            np_closes=np.array(closes)
            rsi = b.rsiFunc(np_closes, b.RSI_PERIOD)
            print("all rsis calc'd so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > b.RSI_OVERBOUGHT:
                if in_position:
                    print("overbought, sell!")
                    buy()
                    if order_successful:
                        in_position = False
                        order_successful = False
                    #put binance sell logic here
                else:
                    print("it is overbought but we don't own any so there's nothing to do.")
            
            if last_rsi < b.RSI_OVERSOLD:
                if in_position:
                    print("it is oversold, but you already own it, so there's nothing to do")
                else:
                    print("buy, buy, buy")
                    #put binance buy logic here
                    buy()
                    if order_successful:
                        in_position = True
                        order_successful = False

ws = websocket.WebSocketApp(b.SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)


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
    global rsi

    info = b.client.get_account()
    balances = info['balances']
    #print(balances)

    BTCprice = b.client.get_avg_price(symbol="BTCUSDT")
    BTCunit = BTCprice['price']


    if request.method == "POST":
        amount = "£300"
        tracker_amount_bought = Tracker(amountBought=amount, unitCost="£40000", buySell='Buy')
        try:
            db.session.add(tracker_amount_bought)
            db.session.commit()
            flash(f'Amount of stocks bought is {amount}!', 'success')
            return redirect(url_for('bot'))
        except:
            return 'There was an issue with the sale.'
    else:
        form = Tracker.query.order_by(Tracker.dateTime).all()
        return render_template('trading_bot.html', form=form, my_balances=balances, unitPrice=BTCunit, rsi=rsi)

@app.route('/buy')
def buy():
    orderBuy = order(SIDE_BUY, b.TRADE_QUANTITY, b.TRADE_SYMBOL, order_type=ORDER_TYPE_MARKET)
    amountBought = orderBuy['executedQty']
    fills = orderBuy['fills']
    unitCost = fills[0]['price']
    tracker_amount_bought = Tracker(amountBought=amountBought , unitCost=unitCost, buySell='Buy')

    try:
        db.session.add(tracker_amount_bought)
        db.session.commit()
        flash(f'Bought!', 'success')
        return redirect(url_for('bot'))
    except:
        return 'There was a problem buying'

@app.route('/sell')
def sell():
    orderBuy = order(SIDE_SELL, b.TRADE_QUANTITY, b.TRADE_SYMBOL, order_type=ORDER_TYPE_MARKET)
    amountBought = orderBuy['executedQty']
    fills = orderBuy['fills']
    unitCost = fills[0]['price']
    tracker_amount_bought = Tracker(amountBought=amountBought , unitCost=unitCost, buySell='Sell')

    try:
        db.session.add(tracker_amount_bought)
        db.session.commit()
        flash(f'Sold!', 'success')
        return redirect(url_for('bot'))
    except:
        return 'There was a problem selling'

@app.route('/startbot')
def startBot():
    global ws
    try:
        flash(f'Bot has been started!!', 'success')
        redirect(url_for('bot'))
        ws.run_forever()

    except:
        return 'There was a problem starting the bot'

@app.route('/stopbot')
def stopBot():
    global ws
    try:
        flash(f'Bot has been stopped!!', 'danger')
        ws.close()
        return redirect(url_for('bot'))
    except:
        return 'There was a problem starting the bot'


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



