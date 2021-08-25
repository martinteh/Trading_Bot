import websocket, json, pprint, time, sys
import numpy as np
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.001

closes = []
in_position = False

api_key = "f2606K2O8H4g2amhSTKiGG1XCLdVjyurVgEPxZSnK59opAvAsgYnSEg8xfFcFsd7"
api_secret = "bWJe4WEv2DsPkPiAcQGYwhWLgHXOgw6fAoxAPsAqKr8kQPjlFdH4FNydcCeyXwWX"

client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'

order_successful = False

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    global order_successful
    try:
        print("sending order")
        orderInfo = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    
    order_successful = True
    return orderInfo


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

def on_open(ws):
    print("opened connection")

def on_close(ws):
    print("close connection")

def on_message(ws, message): # automated bot function that runs indefinitely
    global closes
    global in_position
    global order_successful
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

        if len(closes) > RSI_PERIOD:
            np_closes=np.array(closes)
            rsi = rsiFunc(np_closes, RSI_PERIOD)
            print("all rsis calc'd so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("overbought, sell!")
                    order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_successful:
                        in_position = False
                        order_successful = False
                    #put binance sell logic here
                else:
                    print("it is overbought but we don't own any so there's nothing to do.")


            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("it is oversold, but you already own it, so there's nothing to do")
                else:
                    print("buy, buy, buy")
                    #put binance buy logic here
                    order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_successful:
                        in_position = True
                        order_successful = False


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