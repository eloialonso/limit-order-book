from collections import defaultdict
from dataclasses import dataclass
import math

from .order import Order


@dataclass 
class ExecutionOutput:
    success: bool
    last_price: int

        
class ActiveBuySellList:
    def __init__(self, mode: str, verbose: bool):
        assert mode in ('buy', 'sell')
        self.log = print if verbose else lambda x: None
        self.mode = mode
        self.list = []
        self.ymin, self.ymax = -5, 5
        
    def __repr__(self) -> str:
        return f'Active {self.mode}s: {repr(self.list)}'
        
    def __getitem__(self, key: int) -> Order:
        return self.list[key]
    
    def is_empty(self) -> bool:
        return len(self.list) == 0
    
    def add(self, order: Order) -> None:
        assert order.mode == self.mode
        
        if self.list == []:
            self.list.append(order)
            return
        
        for i, o in enumerate(self.list):
            assert o.time < order.time
            if (self.mode == 'buy' and o.price < order.price):
                break
            if (self.mode == 'sell' and o.price > order.price):
                break
        else:
            i += 1
        self.list = self.list[:i] + [order] + self.list[i:]
    
    def execute(self, order: Order) -> ExecutionOutput:
        assert order.mode != self.mode
        q = 0
        target_q = abs(order.quantity)
        for i, o in enumerate(self.list):
            if self.mode == 'buy' and order.price is not None and o.price < order.price:
                break
            if self.mode == 'sell' and order.price is not None and o.price > order.price:
                break
            q += abs(o.quantity)
            if q >= target_q:
                break
        
        if q < target_q:
            self.log(f'Could not execute order {order}, canceling it.')
            return ExecutionOutput(success=False, last_price=None)
            
        remaining_q = q - target_q
        if remaining_q > 0:
            self.list[i].quantity = remaining_q * (1 if self.mode == 'buy' else -1)
            i -= 1

        self.list = self.list[i + 1:]
        return ExecutionOutput(success=True, last_price=o.price)
    
    def render(self, ax, color: str, **properties) -> None:
        total = defaultdict(lambda: 0)
        for order in self.list:
            p, q = order.price, -order.quantity
            bar, = ax.bar(p, q, bottom=total[p], align='center')
            bar.set(color=color, **properties)
            total[p] += q
        
        if self.list:
            self.ymin = min(self.ymin, min(total.values()) - 1)
            self.ymax = max(self.ymax, max(total.values()) + 1)
            extreme_price = self.list[0].price
            if not math.isinf(extreme_price):
                posy = +2 if self.mode == 'buy' else -2
                s = 'bid' if self.mode == 'buy' else 'ask'
                ax.text(extreme_price, posy, s, horizontalalignment='center', color=color)
        
