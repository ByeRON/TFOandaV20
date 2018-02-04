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

	def append_tickdata(self, recv):
		tick =  pd.Series(float(recv["tick"]["bid"]),index=[pd.to_datetime(recv["tick"]["time"])])
		self.tickdata = self.tickdata.append(tick)

	def to_ohlc(self, rate):
		return self.tickdata.resample(rate).ohlc()


	def clear_tickdata(self):
		self.tickdata = pd.Series([])


	def concat_ohlc(self, df):
		self.ohlc = pd.concat([self.ohlc, df])


	def drop_ohlc(self):
		self.ohlc = self.ohlc.drop([self.ohlc.index[0]])


	def update_ohlc(self):
		self.concat_ohlc(self.to_ohlc(self.rate))
		self.drop_ohlc()
		self.clear_tickdata()


def main():
	print("This class is FXData")


if __name__ == "__main__":
	main()
