import argparse
import json
import threading
import time
import webbrowser
from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    Listbox,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    Variable,
    ttk,
)
from tkinter.constants import RIGHT

import requests
from google_speech import Speech

from get_data import get_current_price, get_data

TTS_PLAYED_UP = 0
TTS_PLAYED_DOWN = 0

def configure_entry_background(entry, value, limit_down, limit_up, background_down="red", background_up="green", background_neutral="white", tts=""):
    global TTS_PLAYED_UP, TTS_PLAYED_DOWN
    if value > limit_up:
        entry.configure(bg=background_down)
        if tts:
            if TTS_PLAYED_UP == 0:
                speech = Speech(tts.format("above", limit_up), "en")
                speech.play()
                TTS_PLAYED_DOWN = 0
                TTS_PLAYED_UP = 1

    elif value < limit_down:
        entry.configure(bg=background_up)
        if tts:
            if TTS_PLAYED_DOWN == 0:
                TTS_PLAYED_DOWN = 1
                TTS_PLAYED_UP = 0
                speech = Speech(tts.format("below", limit_down), "en")
                speech.play()
    else:
        entry.configure(bg=background_neutral)
        if tts:
            TTS_PLAYED_DOWN = 0
            TTS_PLAYED_UP = 0

def entry_maker(tab_root, name, col, row, **options):
    vr_string_var = StringVar()
    lbl_entry = Label(tab_root, text=name)
    ent_entry = Entry(tab_root, textvariable=vr_string_var, **options)

    lbl_entry.grid(row=row, column=col)
    ent_entry.grid(row=row+1, column=col)
    return ent_entry, vr_string_var

def get_current_price_work(label, symbol="OMGUSDT"):
    while True:
        label.config(text=f"{symbol} CURRENT PRICE: " + get_current_price(symbol))
        time.sleep(2)

def update_func(entries, vars, update_data_minutes_invertal, sleep_time=30, symbol="OMGUSDT"):
    while True:
        try:
            macdhist, cci, money_flow, rsi, slowd, bool_bands = get_data(minutes_interval=update_data_minutes_invertal, symbol=symbol)
            
            vars[0].set("TBD")
            vars[1].set(cci[-1])
            vars[2].set(money_flow[-1])
            vars[3].set(rsi[-1])
            vars[4].set(slowd[-1])

            # bollinger bands
            vars[5].set(bool_bands[0][-1])
            vars[6].set(bool_bands[1][-1])
            vars[7].set(bool_bands[2][-1])


            # configure_entry_background(entries[0], macdhist[-1], -0.008, 0.008)
            configure_entry_background(entries[1], cci[-1], -150, 150)
            # if update_data_minutes_invertal == "5m":
            #     configure_entry_background(entries[2], money_flow[-1], 20, 80, tts="Money flow {} {} in five minutes graph yeet")
            # else:
            configure_entry_background(entries[2], money_flow[-1], 20, 80)          
            configure_entry_background(entries[3], rsi[-1], 30, 70)
            configure_entry_background(entries[4], slowd[-1], 20, 80)
            time.sleep(sleep_time)

        except requests.exceptions.ConnectionError:
            for var in vars:
                var.set("Connection Error")
            time.sleep(5)


def tab_maker(notebook, update_interval, thread_sleep_time=30, lbl_title="", tab_title="", symbol="OMGUSDT"):
    frame = ttk.Frame(notebook)
    thread = threading.Thread(target=update_func, args=[*tab_populator(tab=frame, title=lbl_title, symbol=symbol), update_interval], kwargs={"symbol" : symbol, "sleep_time" : thread_sleep_time})
    thread.setDaemon(True)
    thread.start()
    notebook.add(frame, text=tab_title)

def tab_populator(tab, title="", symbol="OMGUSDT"):
    if title:
        lbl_title = Label(tab, text = title)
        lbl_title.grid(column=0, row=0)

    ent_macd, vr_macd = entry_maker(tab, "MACD", row=1, col=0)
    ent_cci, vr_cci = entry_maker(tab, "CCI", row=3, col=0)
    ent_money, vr_money = entry_maker(tab, "MONEY FLOW", row=5, col=0)
    ent_rsi, vr_rsi = entry_maker(tab, "RSI(12)", row=7, col=0)
    ent_sto, vr_sto = entry_maker(tab, "STOCHASTIC", row=9, col=0)

    ent_boll_lower, vr_boll_l = entry_maker(tab, "LOWER BOLLINGER BAND", row=2, col=1)
    ent_boll_middle, vr_boll_m = entry_maker(tab, "MIDDLE BOLLINGER BAND", row=4, col=1)
    ent_boll_upper, vr_boll_u = entry_maker(tab, "UPPER BOLLINGER BAND", row=6, col=1)

    open_in_web_button = Button(tab, text=f"Open {symbol} in Binance", command=lambda: webbrowser.open(f'https://www.binance.com/en/futuresng/{symbol}', new=2))
    open_in_web_button.grid(row=5, column=3)
    entries = [ent_macd, ent_cci, ent_money, ent_rsi, ent_sto, ent_boll_upper, ent_boll_middle, ent_boll_lower]
    varslist = [vr_macd, vr_cci, vr_money, vr_rsi, vr_sto, vr_boll_u, vr_boll_m, vr_boll_l]

    return entries, varslist

def main(root, symbol):
    tabControl = ttk.Notebook(root)
    price_title = Label(root, text ="",font='Helvetica 11 bold')
    price_title.pack()
    
    with open("tabs.json", "r") as f:
        tabs = json.load(f)
        for tab in tabs:
            tab_maker(tabControl, tab["interval"], thread_sleep_time=tab["thread_sleep_time"], lbl_title=tab["lbl_title"].format(symbol), tab_title=tab["tab_title"], symbol=symbol)

    current_price_thread = threading.Thread(target=get_current_price_work, args=[price_title, symbol])
    current_price_thread.setDaemon(True)
    current_price_thread.start() 
    tabControl.pack(expand=1, fill="both")

if __name__ == '__main__':
    root = Tk()
    root.title("Technical Analysis for Crypto Currencies")
    
    parser = argparse.ArgumentParser(description='Technical Analysis Indicator Calculator')
    parser.add_argument('-symbols', '-s', '--names-list', type=str, help='Symbol of the exchange that program should use, defaults to OMGUSDT', default=["OMGUSDT"], nargs="+")
    args = parser.parse_args()
    
    for symbol in args.names_list:
        main(root, symbol=symbol)

    root.mainloop()
