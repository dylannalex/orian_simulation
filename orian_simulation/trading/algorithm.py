from abc import ABC, abstractmethod

import pandas as pd

from orian_simulation.trading.prediction import PredictionEnum


class TradingAlgorithm(ABC):
    def __init__(self):
        self.window_sizeame = "TradingAlgorithm"

    @abstractmethod
    def make_prediction(self, stock_market_data: pd.DataFrame) -> PredictionEnum:
        pass


class TrendAlgorithm(TradingAlgorithm):
    """
    A trading algorithm that predicts the trend of a stock based on the recent closing prices.

    The algorithm analyzes the closing prices over a specified window size. It predicts:
    - INCREASE: if all prices within the window have increased consecutively.
    - DECREASE: if all prices within the window have decreased consecutively.
    - STABLE: if the prices within the window do not show a consistent increase or decrease.
    - UNKNOWN: if there are not enough prices to fill the window size.

    Args:
        window_size (int): The number of recent closing prices to consider for prediction.
    Methods:
        make_prediction(stock_market_data: pd.DataFrame) -> PredictionEnum:
            Makes a prediction on the trend of a stock based on the given stock market data.
    """

    def __init__(self, window_size: int):
        self.window_size = window_size
        self.name = f"TrendAlgorithm({window_size})"

    def make_prediction(self, stock_market_data: pd.DataFrame) -> PredictionEnum:
        """
        Makes a prediction on the trend of a stock based on the given stock market data.
        Args:
            stock_market_data (pd.DataFrame): The stock market data containing the closing prices.
        Returns:
            PredictionEnum: The predicted trend of the stock (INCREASE, DECREASE, or STABLE).
        """
        if len(stock_market_data) < self.window_size:
            return PredictionEnum.UNKNOWN

        prices = stock_market_data["Close"].iloc[-self.window_size :]

        if all(prices.iloc[i] < prices.iloc[i + 1] for i in range(self.window_size - 1)):
            return PredictionEnum.INCREASE
        elif all(prices.iloc[i] > prices.iloc[i + 1] for i in range(self.window_size - 1)):
            return PredictionEnum.DECREASE
        else:
            return PredictionEnum.STABLE
        