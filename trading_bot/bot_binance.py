import websocket, json, pprint, time, sys
import numpy as np
from binance.client import Client
from binance.enums import *


# if the time isn't synced, go to control panel and sync up the time with the server on windows

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.001

api_key = "WAoawdV3kdvtQpKj8SxVAT0H6GDKUMFdH7r4SncRjcSnxB6I8r7QXF1Cqyd6RmGi"
api_secret = "QwDRjAe7kIJcEOZRMGC5ao5Q85vzGoWMQIGZ9Sa661MVmfazkaMhViAjy9NIhCGw"

client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'


def rsiFunc(prices, n):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi




def on_message_marketPrice(ws, message): # automated bot function that runs indefinitely
    global closes
    global in_position
    print("received message")
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    #is_candle_closed = candle['x']
    close = candle['c']
    return close
    #if is_candle_closed:
        #print("candle closed at {}".format(close))
        #closes.append(float(close))
        #print("closes")
        #print(closes)

#ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
#ws.run_forever()

#ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message_marketPrice)
#ws.run_forever()

#order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
#print(client.get_avg_price(symbol="BTCUSDT")['price'])