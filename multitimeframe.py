import requests
import json
import pandas as pd
#from OldOandaAccount import OandaAccount
from OandaAccount import AccountClass
from OandaFXData import FXData
from OandaVisual import FXVisual


def connect_to_stream(instruments, environment="demo"):

	"""
	Environment            Description
	fxTrade(Live)          The live(real money) environment
	fxTrade Practice(Demo) The Demo (simulated money) environment
	"""

	domainDict = {'live':'stream-fxtrade.oanda.com','demo':'stream-fxpractice.oanda.com'}
	#Replace the following variables with your personal values
#	account = OandaAccount()
	account = AccountClass()
#	environment = "demo"
	domain = domainDict[environment]
	access_token = account.get_token()
	account_id = account.get_id()
#	instruments = "GBP_JPY"

	try:
		s = requests.Session()
		#url = "https://" + domain + "/v1/prices"
		#url = "https://" + domain + "/v3/accounts/" + account_id +"/pricing"
		url = "https://" + domain + "/v3/accounts/" + account_id +"/pricing/stream"
		headers = {'Authorization':'Bearer ' + access_token, 
					#'X-Accept-Datetime-Format':'unix'
					}
		params = {'instruments':instruments}
		#params = {'instruments':instruments, 'accountId':account_id}
		#params = {'instruments':instruments, 'since':"2018-02-01T00:00:00.000000000Z"}
		req = requests.Request('GET', url, headers = headers, params = params)
		pre = req.prepare()
		resp = s.send(pre, stream = True, verify = True)
		return resp
	except Exception as e:
		s.close()
		print("Caught exception when connecting to stream : {}".format(str(e)))

def convert_byte_into_dict(byte_line):
	try:
		return json.loads(byte_line.decode("UTF-8"))
	except Exception as e:
		print("Caught exception when converting message into json : {}" .format(str(e)))
		return None

def has_heartbeat_in_string(msg):
	if "heartbeat" in msg or msg is None:
		return True
	else:
		return False

def has_heartbeat_in_byte(msg):
	msg = convert_byte_into_dict(msg)
	if "heartbeat" in msg or msg is None:
		return True
	else:
		return False

def invalid_status_code(res):
	if res.status_code != 200:
		return True
	else:
		return False

def is_nullstr(msg):
	if msg:
		return False
	else:
		return True

def has_tick_in_byte(msg):
	if is_nullstr(msg) == False and has_heartbeat_in_byte(msg) == False:
		return True
	else:
		return False

def has_price(msg):
	msg = convert_byte_into_dict(msg)
	if msg["type"] == "PRICE":
		return True
	else:
		return False

def strategy():
	pass

def can_update(recv, data, num_stick=0):
	dummy_tick = pd.Series(float(recv["bids"][0]["price"]),index=[pd.to_datetime(recv["time"])])
	dummy_tickdata = data.tickdata.append(dummy_tick)
	dummy_ohlc = dummy_tickdata.resample(data.rate).ohlc()
	
	if((num_stick + 2) <= len(dummy_ohlc)):
		return True
	else:
		return False

def preprocess(response, data, crit_rate, size):
	for line in response.iter_lines(1):
		print(line)
#		if has_tick_in_byte(line):
		if has_price(line):
			recv = convert_byte_into_dict(line)
			if can_update(recv,data[crit_rate],num_stick=size) == True:
				for v in data.values():
					v.update_ohlc()
					print(v.ohlc)
				print("complete initialize function")
				break
			for v in data.values():
				v.append_tickdata(recv)
				print(v.tickdata)
		else:
			continue

def mainroutine(response, data, crit_rate):
	plot = FXVisual()
	for line in response.iter_lines(1):
#		if has_tick_in_byte(line):
		if has_price(line):
			recv = convert_byte_into_dict(line)
			if can_update(recv,data[crit_rate]) == True:
				for v in data.values():
					print(v.ohlc)
					plot.visualize(v.ohlc, v.rate)
					strategy()
					v.update_ohlc()
			for v in data.values():
				v.append_tickdata(recv)
#			print(data.tickdata)
		else:
			continue

def can_not_connect(res):
	if res.status_code != 200:
		return True
	else:
		return False

def main():
	response = connect_to_stream("GBP_JPY")
	if can_not_connect(response) == True:
		print(response.text)
		return

	time_scale = {"1min","5min"}
	data = {k : FXData(k) for k in time_scale}
	criterion = "5min"
	size = 2

	for v in data.values():
		v.set_num_drop(criterion)
#		print(v.rate)
#		print(v.freq)

	preprocess(response, data, criterion, size)
	mainroutine(response, data, criterion)

if __name__ == "__main__":
	main()
