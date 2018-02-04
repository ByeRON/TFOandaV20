import pandas as pd
import numpy as np

"""
<Alias>    <Description>
W          weekly frequency
M          month end frequency
H          hourly frequency
T,min      minutely frequency
S          secondly frequency

Refference from pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
"""

class FXData:
	def __init__(self, rate):
		self.recv = None
		self.tickdata = pd.Series([])
		self.ohlc = None
		self.rate = rate
		self.freq = None
#		self.recv = None

	def set_num_drop(self, rate):
		t_index = pd.date_range("2017-1-1 00:00", periods=2, freq=rate)
		ts = pd.Series(np.random.randn(len(t_index)), index=t_index)
		self.freq = len(ts.asfreq(self.rate)) - 1

	def append_tickdata(self, recv):
		tick =  pd.Series(float(recv["bids"][0]["price"]),index=[pd.to_datetime(recv["time"])])
		self.tickdata = self.tickdata.append(tick)

	def to_ohlc(self, rate):
		return self.tickdata.resample(rate).ohlc()

	def clear_tickdata(self):
		self.tickdata = pd.Series([])

	def concat_ohlc(self, df):
		self.ohlc = pd.concat([self.ohlc, df])

#	def drop_ohlc(self):
#		if (self.rate == self.crit_rate):
#			self.ohlc = self.ohlc.drop([self.ohlc.index[0]])
#		else:
#			drop_index = np.array([])
#			for i in range(self.freq):
#				drop_index = np.append(drop_index,self.ohlc.index[i])
#			self.ohlc = self.ohlc.drop(drop_index)
			
	def drop_ohlc(self):
		tmp_index = np.array([])
		for i in range(self.freq):
			tmp_index = np.append(tmp_index,self.ohlc.index[i])
		self.ohlc = self.ohlc.drop(tmp_index)


	def update_ohlc(self):
		self.concat_ohlc(self.to_ohlc(self.rate))
		self.drop_ohlc()
		self.clear_tickdata()

#	def can_update_ohlc(self, rate, size=0):
#		dummy_tick = pd.Series(float(self.recv["tick"]["bid"]),index=[pd.to_datetime(self.recv["tick"]["time"])])
#		dummy_tickdata = self.tickdata.append(dummy_tick)
#		dummy_ohlc = dummy_tickdata.resample(rate).ohlc()
#		if((size + 2) <= len(dummy_ohlc)):
#			return True
#		else:
#			return False

def main():
	print("This class is FXData")


if __name__ == "__main__":
	main()
