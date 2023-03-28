import math
import random

from .lob import LOB
from .order import display_order_menu, Order


def maslov(price0, T, p_limit, p_sell, max_quantity, max_delta_price, interactive=False):
    assert 0 <= p_limit <= 1
    assert 0 <= p_sell <= 1
    assert max_quantity >= 1
    assert max_delta_price >= 1
    
    lob = LOB()
    
    if interactive:
        lob.render()
    
    market, ask, bid = [], [], []
    
    for t in range(T):
        trade = 'buy' if random.random() > p_sell else 'sell'
        mode = 'market' if random.random() > p_limit else 'limit'
        
        quantity = random.randint(1, max_quantity) * (-1 if trade == 'sell' else +1)
        
        if mode == 'market':
            price = None
        else:
            market_price = price0 if math.isnan(lob.market) else lob.market 
            price = market_price + random.randint(1, max_delta_price) * (1 if trade == 'sell' else -1)
        
        lob.place(Order(price, quantity, t))

        if interactive:
            order = display_order_menu(default_trade=trade, default_mode=mode, default_quantity=abs(quantity), default_price='' if mode == 'market' else price)
            if order is None:
                break
            lob.render()
        
    return lob
