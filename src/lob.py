from collections import defaultdict
import math
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from .active_buy_sell_list import ActiveBuySellList
from .order import Order


class LOB:
    def __init__(self, verbose: bool = False):
        self.active_buys = ActiveBuySellList('buy', verbose)
        self.active_sells = ActiveBuySellList('sell', verbose)
        self.market = float('nan')
        self.data = defaultdict(lambda: [])
        self.fig, self.xmin, self.xmax = None, float('+inf'), float('-inf')
        
    def __repr__(self) -> str:
        return f"ask: {self.ask} bid: {self.bid} market: {self.market}"
    
    @property
    def ask(self) -> int:
        return float('+inf') if self.active_sells.is_empty() else self.active_sells[0].price
    
    @property
    def bid(self) -> int:
        return float('-inf') if self.active_buys.is_empty() else self.active_buys[0].price
    
    def is_empty(self) -> bool:
        return self.active_buys.is_empty() and self.active_sells.is_empty()
    
    @property
    def ymin(self) -> int:
        return min(self.active_buys.ymin, self.active_sells.ymin)
        
    @property
    def ymax(self) -> int:
        return max(self.active_buys.ymax, self.active_sells.ymax)
    
    @property
    def current_range(self) -> Tuple[int, int]:
        l = (self.active_buys.list[::-1] + self.active_sells.list)
        return (l[0].price, l[-1].price) if len(l) > 0 else (float('-inf'), float('+inf'))
        
    def place(self, order: Order) -> None:
        if order.price is None or (order.mode == 'buy' and order.price >= self.ask) or (order.mode == 'sell' and order.price <= self.bid):
            self._execute(order)
        else:
            self._add(order)
        self._update_data()

    def _execute(self, order: Order) -> None:
        assert order.price is None or (order.mode == 'buy' and order.price >= self.ask) or (order.mode == 'sell' and order.price <= self.bid)
        if order.mode == 'buy':
            output = self.active_sells.execute(order)
        else:
            output = self.active_buys.execute(order)
        if output.success:
            self.market = output.last_price
        
    def _add(self, order: Order) -> None:
        assert (order.mode == 'buy' and order.price < self.ask) or (order.mode == 'sell' and order.price > self.bid)
        if order.mode == 'buy':
            self.active_buys.add(order)
        else:
            self.active_sells.add(order)
            
        self.xmin = min(self.xmin, order.price)
        self.xmax = max(self.xmax, order.price)
    
    def _update_data(self) -> None:
        self.data['bid'].append(self.bid)
        self.data['ask'].append(self.ask)
        self.data['mid'].append(0.5 * (self.bid + self.ask))
        self.data['market'].append(self.market)
        
    def render(self, show_price=True) -> None:
        if self.fig is None:
            self.fig, self.axes = plt.subplots(2, 1) if show_price else plt.subplots() #, figsize=(9, 10))

        #
        # Available depth
        #
        
        ax = self.axes[0] if show_price else self.axes
        ax.cla()
        
        ax.set(xlabel='Price', ylabel='Available depth')
        ax.axhline(y=0, color='black')
        
        # Plot bars
        common = {
            'width': 1,
            'edgecolor': 'black'
        }
        self.active_buys.render(ax, color='tab:blue', **common)
        self.active_sells.render(ax, color='tab:red', **common)
          
        # Set limits and ticks
        ax.set(yticks=np.arange(self.ymin, self.ymax + 1, math.ceil((self.ymax - self.ymin) / 10)))
        ax.set(ylim=(self.ymin, self.ymax))
        if not math.isinf(self.xmin):
            current_min, current_max = self.current_range
            xmin = max(self.xmin, current_min - 10)
            xmax = min(self.xmax, current_max + 10)
            
            ax.set(xticks=np.arange(xmin, xmax + 1, math.ceil((xmax + 1 - xmin) / 10)))
            ax.set(xlim=(xmin - 1, xmax + 1))
        
        if not show_price:
            self.fig.canvas.draw()
            return

        #
        # Price curves
        #
        

        ax = self.axes[1]
        ax.cla()
        
        ax.set(xlabel='Time', ylabel='Price')
        ax.grid('on')
        T = len(self.data['bid'])

        for key, ts in self.data.items():
            ts = np.array(ts)
            sections = np.split(np.arange(len(ts)), np.where(np.diff(np.isfinite(ts).astype(int)) != 0)[0] + 1)
            
            if key == 'bid':
                color = 'tab:blue'
            elif key == 'ask':
                color = 'tab:red'
            elif key == 'mid':
                color = 'tab:green'
            elif key == 'market':
                continue
            
            last = None
            label_set = False
            for i, idx in enumerate(sections):
                if len(idx) == 0:
                    continue
                if np.isfinite(ts[idx]).all():
                    line, = ax.plot(idx, ts[idx])
                    line.set(linewidth=1, color=color, linestyle='solid')
                    if not label_set:
                        line.set(label=key)
                        label_set = True
                    
                    if last is not None:
                        last_idx, last_value = last
                        first_idx, first_value = idx[0], ts[idx[0]]
                        ax.plot([last_idx, first_idx], [last_value, first_value])[0].set(linewidth=1, color=color, linestyle='dashed')

                    last = idx[-1], ts[idx[-1]]
                                    
        if not math.isinf(self.xmin):
            ax.set(xlim=(0, T), xticks=np.arange(0, T + 1, max(1, T // 10)), yticks=np.arange(xmin, xmax, math.ceil((xmax + 1 - xmin) / 10)))
            ax.legend()
        
        self.fig.canvas.draw()
        
