from binance.client import Client
from binance.client import Client
from binance.enums import *
import time

api_key = "f2606K2O8H4g2amhSTKiGG1XCLdVjyurVgEPxZSnK59opAvAsgYnSEg8xfFcFsd7"
api_secret = "bWJe4WEv2DsPkPiAcQGYwhWLgHXOgw6fAoxAPsAqKr8kQPjlFdH4FNydcCeyXwWX"


client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    
    return True


order(SIDE_BUY, 0.001, "BTCUSDT", order_type=ORDER_TYPE_MARKET)
print(order)
time.sleep(3)
order(SIDE_SELL, 0.001, "BTCUSDT", order_type=ORDER_TYPE_MARKET)
print(order)
time.sleep(3)
print(client.get_account())


