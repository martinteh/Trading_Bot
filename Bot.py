import requests, json, datetime, time
import base64
import hmac
import hashlib

base_url = "https://api.sandbox.gemini.com"

gemini_api_key = "account-c3Tq5mXw3TFSbkQyKbcr"
gemini_api_secret = "3pbp8qvvqRzmpsjgSPAuL95oMNYY".encode()

t = datetime.datetime.now()
payload_nonce =  str(int(time.mktime(t.timetuple())*1000))

payload = {
    "nonce": payload_nonce,
    "request": "/v1/balances"
}

encoded_payload = json.dumps(payload).encode()
b64 = base64.b64encode(encoded_payload)
signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

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

    response = requests.post(url, data=None, headers=request_headers)
    Balance = response.json()
    print(Balance)



#def placeSellOrder():


def placeBuyOrder():

def attemptToMakeTrade():
    

#startBot()
getBalances()