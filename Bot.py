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
    



def placeSellOrder(close):
    endpoint = "/v1/order/new"
    url = base_url + endpoint
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": "0.01",
        "price": close-1000,
        "side": "sell",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
        }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    newOrder = response.json()
    print(newOrder)
    #print("A sell order of ${}".format(float(newOrder['executed_amount'])*float(newOrder['price'])), "has been completed.")

def placeBuyOrder(close):
    endpoint = "/v1/order/new"
    url = base_url + endpoint
    payload = {
        "request": "/v1/order/new",
        "nonce": payload_nonce,
        "symbol": "btcusd",
        "amount": "0.01",
        "price": close+1000,
        "side": "buy",
        "type": "exchange limit",
        "options": ["immediate-or-cancel"] 
        }
    APILogin(payload)

    response = requests.post(url, data=None, headers=request_headers)
    newOrder = response.json()
    print("A buy order of ${}".format(float(newOrder['executed_amount'])*float(newOrder['price'])), "has been completed.")

#def attemptToMakeTrade():


#startBot()
#getBalances()
getMarketPrice()
time.sleep(2)
#placeBuyOrder(close)
placeSellOrder(close)