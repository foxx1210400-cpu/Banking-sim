from ui.gui_components import make_button, write_to_textbox


def build_sector_menu(sidebar, sectors, callback):
    import tkinter as tk

    tk.Label(sidebar, text="Stock Categories", fg="white", bg="#1a1a1a",
             font=("Segoe UI", 12, "bold")).pack(pady=(20,5))

    for sec in sectors:
        make_button(sidebar, sec, lambda s=sec: callback(s)).pack(fill="x")


def show_sector(sector, market, header, textbox, refresh_header):
    refresh_header()
    out = ""

    for s in market.stocks.values():
        if s.sector == sector:
            out += f"{s.ticker}: ${s.price} | {s.name}\n"

    write_to_textbox(textbox, out if out else "No stocks found.")
