import requests, json, datetime, time
import base64
import hmac
import hashlib

base_url = "https://api.sandbox.gemini.com"
gemini_api_key = "account-c3Tq5mXw3TFSbkQyKbcr"
gemini_api_secret = "3pbp8qvvqRzmpsjgSPAuL95oMNYY".encode()
t = datetime.datetime.now()
payload_nonce =  str(int(time.mktime(t.timetuple())*1000))
request_headers = {}
close = 0




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
    print("candle closed at {}".format(close))
    return close


def startBot():
    while True:
        getMarketPrice()
        time.sleep(10)
        #attemptToMakeTrade()

def getBalances():
    
    endpoint = "/v1/balances"
    url = base_url + endpoint

    payload = {
    "nonce": payload_nonce,
    "request": "/v1/balances"
    }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    Balance = response.json()
    
    for type in Balance:
        print("Currency is {}".format(type['currency']), "and the amount available is {}".format(type['availableForWithdrawal']))
    
    return [type['availableForWithdrawal'][0], type['availableForWithdrawal'][0]]



def placeSellOrder(close):
    endpoint = "/v1/order/new"
    url = base_url + endpoint
    balances = getBalances()
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": str(0.1*balances[0]),
        "price": close-100,
        "side": "sell",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
        }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    newOrder = response.json()
    #print(newOrder)
    print("A sell order of ${}".format(float(newOrder['executed_amount'])*float(newOrder['price'])), "has been completed.")

def placeBuyOrder(close):
    endpoint = "/v1/order/new"
    url = base_url + endpoint
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": str(0.1*balances[1]),
        "price": close+1000,
        "side": "buy",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
        }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    newOrder = response.json()
    print("A buy order of ${}".format(float(newOrder['executed_amount'])*float(newOrder['price'])), "has been completed.")


isNextOperationBuy = True
UPWARD_TREND_THRESHOLD = 1.5
DIP_THRESHOLD = -2.25
PROFIT_THRESHOLD = 1.25
STOP_LOSS_THRESHOLD = -2.00
lastOpPrice = getMarketPrice()

def tryToBuy(percentageDiff, currentPrice):
    if percentageDiff >= UPWARD_TREND_THRESHOLD or percentageDiff <= DIP_THRESHOLD:
        placeBuyOrder(currentPrice)
        lastOpPrice = currentPrice
        isNextOperationBuy = False

def tryToSell(percentageDiff, currentPrice):
    if percentageDiff >= PROFIT_THRESHOLD or percentageDiff <= STOP_LOSS_THRESHOLD:
        placeSellOrder(currentPrice)
        lastOpPrice = currentPrice
        isNextOperationBuy = True


def attemptToMakeTrade():
    currentPrice = getMarketPrice()
    percentageDiff = ((currentPrice - lastOpPrice)/lastOpPrice)*100
    if isNextOperationBuy:
        tryToBuy(percentageDiff, currentPrice)
    else:
        tryToSell(percentageDiff, currentPrice)





#startBot()
getBalances()
#getMarketPrice()
#time.sleep(2)
#placeBuyOrder(close)
#placeSellOrder(close)