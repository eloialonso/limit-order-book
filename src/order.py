from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk


@dataclass
class Order:
    price: int
    quantity: int
    time: int
    
    @property
    def mode(self):
        assert self.quantity != 0
        return 'buy' if self.quantity > 0 else 'sell'


@dataclass
class UserInput:
    ok: bool
    should_quit: bool = False
    order: Order = None


def display_order_menu(prompt='', default_trade='', default_mode='', default_quantity='', default_price=''):

    def disable_textbox():
        textbox['state'] = 'disabled'

    def enable_textbox():
        textbox['state'] = 'normal'

    def process_input():
        if trade.get() == '' and mode.get() == '' and price.get() == '' and quantity.get() == '':
            return UserInput(ok=False, should_quit=True)

        quit = bool(should_quit.get())

        # Wrong input
        if trade.get() not in ['buy', 'sell'] or mode.get() not in ['market', 'limit']:
            return UserInput(ok=False, should_quit=quit)
        if not quantity.get().isdigit() or (mode.get() == 'limit' and not price.get().isdigit()):
            return UserInput(ok=False, should_quit=quit)

        # Correct input
        p = int(price.get()) if mode.get() == 'limit' else None
        q = int(quantity.get()) * (-1 if trade.get() == 'sell' else 1)
        order = Order(p, q, time=None)
        return UserInput(ok=True, order=order, should_quit=quit)

    #######################################

    root = tk.Tk()
    root.title(prompt)
    root.geometry('200x300+100+300')
    root.resizable(False, False)

    label_trade = ttk.Label(root, text='Trade:')
    label_trade.pack(fill='x')
    trade = tk.StringVar()
    r_b = ttk.Radiobutton(root, text='buy', value='buy', variable=trade)
    r_s = ttk.Radiobutton(root, text='sell', value='sell', variable=trade)
    trade.set(default_trade)
    r_b.pack(fill='x')
    r_s.pack(fill='x')

    label_mode = ttk.Label(root, text='Mode:')
    label_mode.pack(fill='x')
    mode = tk.StringVar()
    r_m = ttk.Radiobutton(root, text='market', value='market', variable=mode, command=disable_textbox)
    r_l = ttk.Radiobutton(root, text='limit', value='limit', variable=mode, command=enable_textbox)
    mode.set(default_mode)
    r_m.pack(fill='x')
    r_l.pack(fill='x')

    label_quantity = ttk.Label(root, text='Quantity:')
    label_quantity.pack(fill='x')
    quantity = tk.StringVar()
    textbox = ttk.Entry(root, textvariable=quantity)
    quantity.set(str(default_quantity))
    textbox.pack(fill='x')

    label_price = ttk.Label(root, text='Price:')
    label_price.pack(fill='x')
    price = tk.StringVar()
    textbox = ttk.Entry(root, textvariable=price)
    price.set(str(default_price))
    textbox.pack(fill='x')

    should_quit = tk.IntVar()
    checkbox = ttk.Checkbutton(root, text='Quit', variable=should_quit, onvalue=1, offvalue=0)
    checkbox.pack(fill='x')

    ok_button = ttk.Button(
        root,
        text='Ok',
        command=lambda: root.destroy()
    )
    ok_button.pack()

    root.bind('<Return>', lambda event: root.destroy())

    root.mainloop()
    
    #######################################

    user_input = process_input()
    if user_input.should_quit:
        return None
    if user_input.ok:
        return user_input.order
    
    return display_order_menu()

