try:
    from ui.gui_components import write_to_textbox
except ImportError:
    from banking_sim.ui.gui_components import write_to_textbox


def show_all_stocks(market, header, textbox, refresh_header):
    refresh_header()
    out = ""

    for s in market.stocks.values():
        out += f"{s.ticker}: ${s.price} | {s.name}\n"

    write_to_textbox(textbox, out if out else "No stocks available.")
