import requests, json, datetime, time
import base64
import hmac
import hashlib
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

base_url = "https://api.sandbox.gemini.com"
gemini_api_key = "account-c3Tq5mXw3TFSbkQyKbcr"
gemini_api_secret = "3pbp8qvvqRzmpsjgSPAuL95oMNYY".encode()
t = datetime.datetime.now()
payload_nonce =  str(int(time.mktime(t.timetuple())*1000))
request_headers = {}
close = 0
buyOrder = 0


def APILogin(payload):

    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()
    global request_headers
    request_headers = { 'Content-Type': "text/plain",
                        'Content-Length': "0",
                        'X-GEMINI-APIKEY': gemini_api_key,
                        'X-GEMINI-PAYLOAD': b64,
                        'X-GEMINI-SIGNATURE': signature,
                        'Cache-Control': "no-cache" }




def getMarketPrice():

    response = requests.get(base_url + "/v2/candles/btcusd/1m")
    btc_data = response.json()
    #print(btc_data)
    global close
    close = btc_data[0][4]
    #print("candle closed at {}".format(close))
    return close


def startBot():
    while True:
        attemptToMakeTrade()
        time.sleep(30)
        

def getBalance(Currency):


    endpoint = "/v1/balances"
    url = base_url + endpoint

    payload = {
    "nonce": payload_nonce,
    "request": "/v1/balances"
    }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    Balance = response.json()
    #print(Balance)

    for type in Balance:
        if type['currency'] == Currency:
            #print("Currency is {}".format(type['currency']), "and the amount available is {}".format(type['availableForWithdrawal']))
            #print(type['availableForWithdrawal'])
            return type['availableForWithdrawal']
    


def placeSellOrder(close):
    endpoint = "/v1/order/new"
    url = base_url + endpoint
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": "0.01", #str(0.01 * float(USD)),
        "price": close-100,
        "side": "sell",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
        }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    newOrder = response.json()
    print(newOrder)
    print("A sell order of ${}".format(float(newOrder['executed_amount'])*float(newOrder['price'])), "has been completed.")

    if float(newOrder['executed_amount']) > 0:
        global isNextOperationBuy
        isNextOperationBuy = False

def placeBuyOrder(close):
    endpoint = "/v1/order/new"
    url = base_url + endpoint
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": "0.01", #str(0.01 * float(USD)),
        "price": close+1000,
        "side": "buy",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
        }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    newOrder = response.json()
    #print(newOrder)
    print("A buy order of ${}".format(float(newOrder['executed_amount'])*float((newOrder['price']))), "has been completed.")
    global buyOrder
    buyOrder = str(float(newOrder['executed_amount'])*float((newOrder['price'])))

    if float(newOrder['executed_amount']) > 0:
        global isNextOperationBuy
        isNextOperationBuy = False


isNextOperationBuy = True
UPWARD_TREND_THRESHOLD = 1.5
DIP_THRESHOLD = -2.25
PROFIT_THRESHOLD = 1.25
STOP_LOSS_THRESHOLD = -2.00
lastOpPrice = 100.00

def tryToBuy(percentageDiff):
    global lastOpPrice
    if percentageDiff >= UPWARD_TREND_THRESHOLD or percentageDiff <= DIP_THRESHOLD:
        placeBuyOrder(close)
        lastOpPrice = getMarketPrice()
        #getBalances()
    else:
        print("No buy order has been completed.")
        #lastOpPrice = getMarketPrice()
    

def tryToSell(percentageDiff):
    global lastOpPrice
    if percentageDiff >= PROFIT_THRESHOLD or percentageDiff <= STOP_LOSS_THRESHOLD:
        placeSellOrder(close)
        #time.sleep(2)
        #getBalances()
        lastOpPrice = getMarketPrice()
    else:
        print("No sell order has been completed.")
        #lastOpPrice = getMarketPrice()


def attemptToMakeTrade():
    percentageDiff = ((getMarketPrice() - lastOpPrice)/lastOpPrice)*100
    print(percentageDiff)
    #time.sleep(2)
    if isNextOperationBuy:
        tryToBuy(percentageDiff)
        #time.sleep(2)
        #getBalances()
    else:
        tryToSell(percentageDiff)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index2.html", tasks=tasks)


if __name__ == "__main__":
    app.run(debug=True)