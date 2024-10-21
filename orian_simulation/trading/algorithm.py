from random import choice
from abc import ABC, abstractmethod

import pandas as pd

from orian_simulation.trading.prediction import PredictionEnum


class TradingAlgorithm(ABC):
    def __init__(self):
        self.window_sizeame = "TradingAlgorithm"

    @abstractmethod
    def make_prediction(self, stock_market_data: pd.DataFrame) -> PredictionEnum:
        pass


class SteadyTrendAlgorithm(TradingAlgorithm):
    """
    A trading algorithm that predicts a steady trend in stock prices based on recent closing prices.

    This algorithm analyzes the closing prices within a specified window size and predicts the overall trend based on the consistency of consecutive price movements. It predicts:

    - INCREASE: If all prices within the window increase consecutively.
    - DECREASE: If all prices within the window decrease consecutively.
    - STABLE: If the prices within the window fluctuate without showing a consistent increase or decrease.
    - UNKNOWN: If there are not enough data points to fill the specified window size.

    The algorithm is ideal for identifying consistent price trends over short periods, focusing on detecting continuous, unbroken upward or downward movements in stock prices.

    Args:
        window_size (int): The number of recent closing prices to analyze for trend prediction.

    Attributes:
        window_size (int): Defines the number of closing prices used to evaluate the trend.
        name (str): A name for the algorithm, indicating the window size being used.

    Methods:
        make_prediction(stock_market_data: pd.DataFrame) -> PredictionEnum:
            Analyzes the recent stock market data and predicts the trend based on the closing prices within the window.
    """

    def __init__(self, window_size: int):
        self.window_size = window_size
        self.name = f"SteadyTrendAlgorithm({window_size})"

    def make_prediction(self, stock_market_data: pd.DataFrame) -> PredictionEnum:
        """
        Analyzes the stock market data and predicts the trend based on consecutive price movements.

        Args:
            stock_market_data (pd.DataFrame): The stock market data containing the 'Close' column with closing prices.

        Returns:
            PredictionEnum: The predicted trend of the stock, which can be one of the following:
                - INCREASE: If all prices have increased consecutively within the window.
                - DECREASE: If all prices have decreased consecutively within the window.
                - STABLE: If the prices do not show a consistent trend.
                - UNKNOWN: If there are insufficient data points to fill the window size.
        """
        if len(stock_market_data) < self.window_size:
            return PredictionEnum.UNKNOWN

        prices = stock_market_data["Close"].iloc[-self.window_size :]

        if all(
            prices.iloc[i] < prices.iloc[i + 1] for i in range(self.window_size - 1)
        ):
            return PredictionEnum.INCREASE
        elif all(
            prices.iloc[i] > prices.iloc[i + 1] for i in range(self.window_size - 1)
        ):
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
        prices = stock_market_data["Close"].iloc[-self.window_size :]

        # Count the number of price increases and decreases
        increases = sum(
            prices.iloc[i] < prices.iloc[i + 1] for i in range(self.window_size - 1)
        )
        decreases = sum(
            prices.iloc[i] > prices.iloc[i + 1] for i in range(self.window_size - 1)
        )

        # Make a prediction based on the majority of movements
        if increases > decreases:
            return PredictionEnum.INCREASE
        elif decreases > increases:
            return PredictionEnum.DECREASE
        else:
            return PredictionEnum.STABLE


class RandomAlgorithm(TradingAlgorithm):
    """
    A trading algorithm that makes random predictions based on stock market data.

    This algorithm randomly predicts whether the stock price will increase, decrease, or remain stable. It is used as a baseline for comparison with other trading algorithms.

    Methods:
        make_prediction(stock_market_data: pd.DataFrame) -> PredictionEnum:
            Makes a random prediction of the stock price trend.
    """

    def __init__(self):
        self.name = "RandomAlgorithm"

    def make_prediction(self, stock_market_data: pd.DataFrame) -> PredictionEnum:
        """
        Makes a random prediction of the stock price trend.

        Args:
            stock_market_data (pd.DataFrame): The stock market data used for prediction.

        Returns:
            PredictionEnum: A random prediction of the stock price trend.
        """
        return choice(
            [PredictionEnum.INCREASE, PredictionEnum.DECREASE, PredictionEnum.STABLE]
        )
