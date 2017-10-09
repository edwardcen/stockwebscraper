"""
Basic Stocks Web Scraper based on Yahoo Finance API
designed by Edward Cen. Not for commercial use. 
Elements of the evaluation loop were inspired by 
John DeNero and the CS61A course.
"""

###########################
# PACKAGES FOR WEB SCRAPING
###########################

import requests
import pandas as pd
from prettytable import PrettyTable

################
# LINE PARSING #
################

def adv_parse(line):
    tokens = line.split()
    if not tokens:
        raise SyntaxError('No command given')
    command = tokens.pop(0)
    if "@" + command in COMMAND_NUM_ARGS:
    	raise SyntaxError('Did you mean "{}"?'.format("@" + command))
    elif command == "@exit":
    	raise SystemExit
    else:
    	return (command, ' '.join(tokens))

##############
# EVALUATION #
##############

def adv_eval(exp):
    operator, operand = exp[0], exp[1]
    if operator not in COMMAND_NUM_ARGS:
        raise SyntaxError('Invalid command: {}'.format(operator))
    else:
        function = SPECIAL_FORMS[operator]

    if COMMAND_NUM_ARGS[operator] == 0:
        function()
    else:
        function(operand)

########################
# READ EVAL PRINT LOOP #
########################

def read_eval_print_loop():
	help()
	while True:
		try:
			line = input('> ')
			exp = adv_parse(line)
			adv_eval(exp)
		except (KeyboardInterrupt, EOFError, SystemExit): # If you ctrl-c or ctrl-d
			print('\nExiting Stock Scraper')
			return
        # If the user input was badly formed or if something doesn't exist
		except SyntaxError as e:
			print('ERROR:', e)


################
# DATA STORAGE #
################

class Stock:
	def __init__(self, symbol):
		self.symbol = symbol
		self.data_points = []
		self.report = None

	def add_data_points(self, data_points_string):
		data_points = data_points_string.split()
		successful, unsuccessful = [], []
		for data in data_points:
			if data in DATA_POINTS_AVAILABLE and data not in self.data_points:
				self.data_points += [data]
				successful += [data]
			else:
				unsuccessful += [data]
		if successful:
			print("\033[92m{0} succesfully added to {1} stock investigation\033[0m".format(
				successful, self.symbol))
		if unsuccessful:
			print("\033[91m{0} are not data points currently allowed\033[0m".format(unsuccessful))

	def remove_data_points(self, data_points_string):
		data_points = data_points_string.split()
		successful, unsuccessful = [], []
		for data in data_points:
			if data in self.data_points:
				self.data_points.remove(data)
				successful += [data]
			else:
				unsuccessful += [data]
		if successful:
			print("\033[92m{0} succesfully removed from {1} stock investigation\033[0m".format(
				successful, self.symbol))
		if unsuccessful:
			print("\033[91m{0} were not found\033[0m".format(unsuccessful))

	def generate_report(self):
		if not self.data_points:
			print("\033[93m You have not selected any data points \033[0m")
			return
		s = ""
		for data in self.data_points:
			s += data
		url = "http://finance.yahoo.com/d/quotes.csv?s={0}&f={1}".format(self.symbol, s)
		file = requests.get(url).content.decode("utf-8")
		file_in_list = file.split(",")
		for pos in range(len(file_in_list)):
			if "\n" in file_in_list[pos]:
				file_in_list[pos] = file_in_list[pos][:len(file_in_list[pos]) - 1]
			# file_in_list[pos] = "\033[92m" + file_in_list[pos] + "\033[0m"
		data_table = PrettyTable(["\033[96m" + DATA_POINTS_AVAILABLE[data] + "\033[0m"
			for data in self.data_points])
		# data_table.column_headers = ["\033[92m" + DATA_POINTS_AVAILABLE[data] + "\u001b[37m"
		# for data in self.data_points]
		data_table.add_row(file_in_list)

		self.report = data_table
		

	def __repr__(self):

		string = """
		\033[96mSymbol:\033[0m {0}\n
		\033[96mData Points:\033[0m {1}
		""".format(self.symbol, self.data_points)
		string += "\n"
		self.generate_report()
		string += str(self.report)
		return string

class StockList:
	def __init__(self):
		self.history = {}
		self.current_stock = None

	def add_stock(self, symbol):
		symbol = symbol.upper()
		if self.current_stock and symbol == self.current_stock.symbol:
			print("\033[93mYou are already currently investigating {0}\033[0m".format(symbol))
		elif symbol in self.history:
			self.current_stock = self.history[symbol]
			print("You already have {0} in history.\n\033[92mStock under investigation is now {0}\033[0m"
				.format(symbol))
		else:
			new_stock = Stock(symbol)
			self.history[symbol] = new_stock
			self.current_stock = new_stock
			print("\033[92mChanged stock under investigation to {0}\033[0m".format(symbol))


############
# COMMANDS #
############

def status():
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		print(history_of_stocks.current_stock)

def remove(data_points_to_remove):
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @stock to select a stock")
	else:
		history_of_stocks.current_stock.remove_data_points(data_points_to_remove)

def add(data_points_to_add):
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @stock to select a stock")
	else:
		history_of_stocks.current_stock.add_data_points(data_points_to_add)

def stock(new_stock):
	history_of_stocks.add_stock(new_stock)

def help():
    print('There are {} possible commands:'.format(len(COMMAND_FORMATS)))
    for usage in COMMAND_FORMATS.keys():
        print(usage,'   ', COMMAND_FORMATS[usage])

def history():
	print(list(history_of_stocks.history.keys()))



#################
# CONFIGURATION #
#################

COMMAND_FORMATS = {
    '@status': '  Shows you current status',
    '@remove': '  Remove data points',
    "@add": "     Add data points",    
    '@stock': '  Change stock under investigation',
    '@help': '    Access Help menu',
    "@history": " Access past searches",
    "@exit": "    Exit the web scraper",
}

COMMAND_NUM_ARGS = {
    '@status': 0,
    '@remove': 1,
    "@add": 1,
    '@stock': 1,
    '@help': 0,
    "@history": 0,
}

SPECIAL_FORMS = {
    '@status': status,
    '@remove': remove,
    "@add": add,
    '@stock': stock,
    '@help': help,
    "@history": history,
}

DATA_POINTS_AVAILABLE = {
	"a": "Ask","b": "Bid","b2": "Ask (realtime)","b3": "Bid (realtime)","p": "Previous Close"
	,"o": "Open","y": "Dividend Yield","d": "Dividend per Share"
	,"r1": "Dividend Pay Date",
	"q": "Ex-Divident Date","c1": "Change","c": "Change & Percent Change","c6": "Change (realtime)"
	,"k2": "Change Percent (realtime)","p2": "Change in Percent","d1": "Last Trade Date"
	,"d2": "Trade Date",
	"t1": "Last Trade Time","c8": "After Hours Change (realtime)","c3": "Commission", "g": "Day's Low",
	"h": "Day's High","k1": "Last Trade (realtime) with Time","l": "Last Trade (With Time)",
	"l1": "Last Trade (Price Only)"
	,"t8": "1yr Target Price",
	"m5": "Change From 200 Day Moving Average","m6": "Percent Change From 200 Day Moving Average"
	,"m7": "Change From 50 Day Moving Average","m8": "Percent Change From 50 Day Moving Average"
	,"m3": "50 Day Moving Average","m4": "200 Day Moving Average","w1": "Day’s Value Change"
	,"w4": "Day’s Value Change (realtime)",
	"p1": "Price Paid","m": "Day's Range","m2": "Day's Range (realtime)","g1": "Holdings Gain Percent"
	,"g3": "Annualized Gains","g4": "Holdings Gain","g5": "Holdings Gain Percent (realtime)"
	,"g6": "Holdings Gain (realtime)",
	"t7": "Ticker Trend","t6": "Trade Links","i5": "Order Book (realtime)","l2": "High Limit"
	,"l3": "Low Limit","v1": "Holdings Value","v7": "Holdings Value (realtime)"
	,"s6": "Revenue",
	"k": "52 Week High","j": "52 Week Low","j5": "Change from 52 Week Low","k4": "Change from 52 Week High"
	,"j6": "Percent Change from 52 Week Low","k5": "Percent Change from 52 Week High","w": "52 Week Range"
	,"v": "Volume",
	"j1": "Market Capitalization","j3": "Market Cap (realtime)","f6": "Float Shares","n": "Name"
	,"n4": "Notes","s": "Symbol","s1": "Shares Owned"
	,"x": "Stock Exchange",
	"j2": "Shares Outstanding","v": "Volume","a5": "Ask Size","b6": "Bid Size","k3": "Last Trade Size"
	,"a2": "Average Daily Volume","e": "Earnings Per Share"
	,"e7": "EPS Estimate Current Year",
	"e8": "EPS Estimate Next Year","e9": "EPS Estimate Next Quarter","b4": "Book Value","j4": "EBITDA"
	,"p5": "Price / Sales","p6": "Price / Book","r": "P/E Ratio"
	,"r2": "P/E Ratio (realtime)",
	"r5": "PEG Ratio","r6": "Price / EPS Estimate Current Year","r7": "Price / EPS Estimate Next Year"
	,"s7": "Short Ratio"
}
#################
# PROGRAM START #
#################
history_of_stocks = StockList()
read_eval_print_loop()