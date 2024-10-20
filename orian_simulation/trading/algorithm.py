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
        
class MajorityTrendAlgorithm(TradingAlgorithm):
    """
    A trading algorithm that predicts the dominant trend in stock prices based on recent closing prices.

    The algorithm analyzes closing prices over a specified window size and determines the majority trend (whether prices
    are increasing, decreasing, or stable) during that period. It predicts:
    
    - INCREASE: if the majority of consecutive price movements within the window show an increase.
    - DECREASE: if the majority of consecutive price movements within the window show a decrease.
    - STABLE: if there is no clear majority of increasing or decreasing movements.
    - UNKNOWN: if there is insufficient data to fill the specified window size.

    Args:
        window_size (int): The number of recent closing prices to consider when making a prediction.

    Methods:
        make_prediction(stock_market_data: pd.DataFrame) -> PredictionEnum:
            Analyzes the stock market data and predicts the dominant trend based on the given window of prices.
    """

    def __init__(self, window_size: int):
        """
        Initializes the MajorityTrendAlgorithm with a specified window size for analyzing price trends.
        
        Args:
            window_size (int): The number of recent price data points to consider for trend analysis.
        """
        self.window_size = window_size
        self.name = f"MajorityTrendAlgorithm({window_size})"

    def make_prediction(self, stock_market_data: pd.DataFrame) -> PredictionEnum:
        """
        Analyzes the stock market data and predicts the dominant trend of a stock based on recent closing prices.
        
        Args:
            stock_market_data (pd.DataFrame): The stock market data containing at least the 'Close' prices.
        
        Returns:
            PredictionEnum: 
                - INCREASE: if the majority of price movements show an upward trend.
                - DECREASE: if the majority of price movements show a downward trend.
                - STABLE: if the price movements are balanced or unclear.
                - UNKNOWN: if there is insufficient data to analyze.
        """
        # Check if there is enough data for the specified window size
        if len(stock_market_data) < self.window_size:
            return PredictionEnum.UNKNOWN

        # Extract the closing prices for the analysis window
        prices = stock_market_data["Close"].iloc[-self.window_size:]

        # Count the number of price increases and decreases
        increases = sum(prices.iloc[i] < prices.iloc[i + 1] for i in range(self.window_size - 1))
        decreases = sum(prices.iloc[i] > prices.iloc[i + 1] for i in range(self.window_size - 1))

        # Make a prediction based on the majority of movements
        if increases > decreases:
            return PredictionEnum.INCREASE
        elif decreases > increases:
            return PredictionEnum.DECREASE
        else:
            return PredictionEnum.STABLE
