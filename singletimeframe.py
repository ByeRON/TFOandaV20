import requests
import json
import pandas as pd
from OldOandaAccount import OandaAccount
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
	account = OandaAccount()
#	environment = "demo"
	domain = domainDict[environment]
	access_token = account.get_token()
	account_id = account.get_id()
#	instruments = "GBP_JPY"

	try:
		s = requests.Session()
		url = "https://" + domain + "/v1/prices"
		headers = {'Authorization':'Bearer ' + access_token, 
					#'X-Accept-Datetime-Format':'unix'
					}
		params = {'instruments':instruments, 'accountId':account_id}
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

def strategy():
	pass

def can_update(recv, data, num_stick=0):
	dummy_tick = pd.Series(float(recv["tick"]["bid"]),index=[pd.to_datetime(recv["tick"]["time"])])
	dummy_tickdata = data.tickdata.append(dummy_tick)
	dummy_ohlc = dummy_tickdata.resample(data.rate).ohlc()
	
	if((num_stick + 2) <= len(dummy_ohlc)):
		return True
	else:
		return False

def preprocess(response, data, size):
	for line in response.iter_lines(1):
		if has_tick_in_byte(line):
			recv = convert_byte_into_dict(line)
			if can_update(recv,data,num_stick=size) == True:
				data.update_ohlc()
				print("complete initialize function")
				print(data.ohlc)
				break
			data.append_tickdata(recv)
			print(data.tickdata)
		else:
			continue

def mainroutine(response, data):
	plot = FXVisual()
	for line in response.iter_lines(1):
		if has_tick_in_byte(line):
			recv = convert_byte_into_dict(line)
			if can_update(recv,data) == True:
				print(data.ohlc)
				plot.visualize(data.ohlc, data.rate)
				strategy()
				data.update_ohlc()
			data.append_tickdata(recv)
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
	
	data = FXData("1min")
	size = 7

	preprocess(response, data, size)
	mainroutine(response, data)


if __name__ == "__main__":
	main()
