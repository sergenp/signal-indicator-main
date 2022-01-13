### Installation

You need to install [TA-lib](https://mrjbq7.github.io/ta-lib/install.html) before installing the requirements then simply:
`pip install -r requirements.txt` 


#### What is this Program?

This program tracks the binance futures, gets the information from it and passes it through the technical analysis stuff provided by TA-lib.
It indicates oversold-overbought conditions given a coin in Binance futures, indicated by a green or red background where the TA numbers are.

#### How to use it?

You can give gui.py a parameter, or parameters, like so:

`python gui.py -s BTCUSDT`

and it will create a tkinter window with related information for you to use.

You can give more than one symbol to it, seperated by a space

`python gui.py -s BTCUSDT SANDUSDT`
