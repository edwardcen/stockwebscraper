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
			print("{0} succesfully added to {1} stock investigation".format(
				successful, self.symbol))
		if unsuccessful:
			print("{0} are not data points currently allowed".format(unsuccessful))

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
			print("{0} succesfully removed from {1} stock investigation".format(
				successful, self.symbol))
		if unsuccessful:
			print("{0} were not found".format(unsuccessful))

	def generate_report(self):
		if not self.data_points:
			print("You have not selected any data points")
			return
		s = ""
		for data in self.data_points:
			s += data
		url = "http://finance.yahoo.com/d/quotes.csv?s={0}&f={1}".format(self.symbol, s)
		self.report = pd.read_csv(url, header = None, names = self.data_points)
		print("Report succesfully generated. Use @status to check values")


	def __repr__(self):

		string = """
		Symbol: {0}\n
		Data Points: {1}
		""".format(self.symbol, self.data_points)
		string += "\n"
		string += str(self.report)
		return string

class StockList:
	def __init__(self):
		self.history = {}
		self.current_stock = None

	def add_stock(self, symbol):
		symbol = symbol.upper()
		if self.current_stock and symbol == self.current_stock.symbol:
			print("You are already currently investigating {0}".format(symbol))
		elif symbol in self.history:
			self.current_stock = self.history[symbol]
			print("You already have {0} in history. Stock under investigation is now {0}"
				.format(symbol))
		else:
			new_stock = Stock(symbol)
			self.history[symbol] = new_stock
			self.current_stock = new_stock
			print("Changed stock under investigation to {0}".format(symbol))

####################
# BACKEND ANALYSIS #	
####################

def generate_url():
	url = ""
	return

def generate_csv():
	return


############
# COMMANDS #
############

def status():
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		print(history_of_stocks.current_stock)

def stock():
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		print("Stock under investigation: {0}".format(history_of_stocks.current_stock.symbol))

def data():
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		print("Data Points under investigation: {0}".format(
			history_of_stocks.current_stock.data_points))
def remove(data_points_to_remove):
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		history_of_stocks.current_stock.remove_data_points(data_points_to_remove)

def add(data_points_to_add):
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		history_of_stocks.current_stock.add_data_points(data_points_to_add)

def change(new_stock):
	history_of_stocks.add_stock(new_stock)

def help():
    print('There are {} possible commands:'.format(len(COMMAND_FORMATS)))
    for usage in COMMAND_FORMATS.keys():
        print(usage,'   ', COMMAND_FORMATS[usage])

def history():
	print(list(history_of_stocks.history.keys()))

def generate():
	if history_of_stocks.current_stock == None:
		print("You have not yet selected a stock. Use @change to select a stock")
	else:
		history_of_stocks.current_stock.generate_report()	


#################
# CONFIGURATION #
#################

COMMAND_FORMATS = {
    '@status': '  Shows you current status',
    '@stock': '   Shows stock you are investigating',
    '@data': '    Shows data points you are investigating',
    '@remove': '  Remove data points',
    "@add": "     Add data points",    
    '@change': '  Change stock under investigation',
    '@help': '    Access Help menu',
    "@history": " Access past searches",
    "@exit": "    Exit the web scraper",
    "@generate": "Generate graph will all data",
}

COMMAND_NUM_ARGS = {
    '@status': 0,
    '@stock': 0,
    '@data': 0,
    '@remove': 1,
    "@add": 1,
    '@change': 1,
    '@help': 0,
    "@history": 0,
    "@generate": 0,
}

SPECIAL_FORMS = {
    '@status': status,
    '@stock': stock,
    '@data': data,
    '@remove': remove,
    "@add": add,
    '@change': change,
    '@help': help,
    "@history": history,
    "@generate": generate,
}

DATA_POINTS_AVAILABLE = (
	"a","b","b2","b3","p","o","y","d","r1",
	"q","c1","c","c6","k2","p2","d1","d2",
	"t1","c8","c3","h","k1","l","l1","t8",
	"m5","m6","m7","m8","m3","m4","w1","w4",
	"p1","m","m2","g1","g3","g4","g5","g6",
	"t7","t6","i5","l2","l3","v1","v7","s6",
	"k","j","j5","k4","j6","k5","w","v",
	"j1","j3","f6","n","n4","s","s1","x",
	"j2","v","a5","b6","k3","a2","e","e7",
	"e8","e9","b4","j4","p5","p6","r","r2",
	"r5","r6","r7","s7"
)
#################
# PROGRAM START #
#################
history_of_stocks = StockList()
read_eval_print_loop()