import random
import tkinter as tk

def build_ticker(root, market):
    frame = tk.Frame(root, bg="#000000", height=30)
    frame.pack(fill="x")
    tk.Label(frame, text="Version 1.0", fg="white", bg="#000000",
             font=("Segoe UI", 10, "bold")).place(x=10, y=6)

    label = tk.Label(frame, text="", fg="#00ff88", bg="#000000",
                     font=("Segoe UI", 12))
    label.place(x=1000, y=5)

    stocks = list(market.stocks.values())
    picks = random.sample(stocks, min(5, len(stocks))) if stocks else []

    def update():
        nonlocal picks
        if not stocks:
            label.config(text="No market data available")
            return
        text = "   |   ".join([f"{s.ticker}: ${s.price}" for s in picks])
        label.config(text=text)

        x = label.winfo_x() - 1
        if x < -label.winfo_reqwidth():
            picks = random.sample(stocks, min(5, len(stocks)))
            x = root.winfo_width()

        label.place(x=x, y=5)
        root.after(75, update)

    update()
    return frame
