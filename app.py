"""
@author: Prakhar Mishra
"""

from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pandas
import numpy as np
from datetime import date
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_data(stock_name, start_date, end_date, default_column='Close'):
	stock = yf.Ticker(stock_name)
	hist = stock.history(period='1d', start=start_date, end=end_date)
	default_col_history = hist[default_column].tolist()

	if len(default_col_history) == 0: return 0
	else: return default_col_history

def calculate_sharpe(history):
	expected_return = np.mean(history)
	risk_free = 10.0
	sharpe = (expected_return - risk_free) / np.std(history)
	return round(sharpe, 2)

def calculate_sortino(history):
	expected_return = np.mean(history)
	print (expected_return)
	below_avg = [i for i in history if i < expected_return]
	risk_free = 10.0
	print (np.std(below_avg))
	sortino = (expected_return - risk_free) / np.std(below_avg)
	return round(sortino, 2)

@app.route('/getmetrics', methods=['POST'])
def metrics():
	history, sharpe_ratios, sortino_ratio = [], [], []
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	# if start_date < end_date:
	# 	return "Start date can't be less than end date"

	for s in ['AAPL', 'GOOG', 'AMZN']:
		history.append(get_data(s, start_date, end_date))

	assert len(history)==3
	
	response = {}
	sortino_max = -1
	s = None
	for data, stock in zip(history, ['AAPL', 'GOOG', 'AMZN']):
		print (stock)
		sortino = calculate_sortino(data)
		if sortino > sortino_max:
			sortino_max = sortino
			s = stock
		response[stock] = {'data': data[::5], 'metrics': [calculate_sharpe(data), sortino]}

	response['best']=s
	return jsonify(response)

if __name__=='__main__':
	app.run(host='0.0.0.0', port=5555, debug=True, threaded=True)