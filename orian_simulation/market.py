from dataclasses import dataclass
from typing import Union, Generator

from pandas import DataFrame, Timestamp


from dataclasses import dataclass

@dataclass
class Asset:
    """
    A class representing a financial asset.

    Attributes:
        name (str): The name of the asset (e.g., "Bitcoin", "AAPL").
        allow_float_amount (bool): Indicates whether fractional amounts of the asset are allowed.
                                   - True: The asset allows fractional amounts (e.g., Bitcoin can have 0.3).
                                   - False: The asset only allows whole amounts (e.g., stocks like AAPL must be an integer).

    Methods:
        __eq__(other: Asset) -> bool:
            Compares two Asset instances for equality based on the asset's name.
        
        __hash__() -> int:
            Returns the hash value of the asset, which is based on the asset's name.
    """
    
    name: str
    allow_float_amount: bool  # True if the asset allows float amounts, False if only integers are allowed

    def __eq__(self, other: "Asset") -> bool:
        """
        Compares this Asset instance to another Asset instance.

        Args:
            other (Asset): The other asset to compare with.

        Returns:
            bool: True if both assets have the same name, False otherwise.
        """
        return self.name == other.name

    def __hash__(self) -> int:
        """
        Returns the hash value for this Asset instance, based on its name.

        Returns:
            int: The hash value of the asset.
        """
        return hash(self.name)


@dataclass
class Currency:
    """
    A class representing a currency.

    Attributes:
        name (str): The name of the currency (e.g., "USD", "EUR").

    Methods:
        __eq__(other: Currency) -> bool:
            Compares two Currency instances for equality based on the currency's name.
        
        __hash__() -> int:
            Returns the hash value of the currency, which is based on the currency's name.
    """
    name: str

    def __eq__(self, other: "Currency") -> bool:
        """
        Compares this Currency instance to another Currency instance.

        Args:
            other (Currency): The other currency to compare with.

        Returns:
            bool: True if both currencies have the same name, False otherwise.
        """
        return self.name == other.name

    def __hash__(self) -> int:
        """
        Returns the hash value for this Currency instance, based on its name.

        Returns:
            int: The hash value of the currency.
        """
        return hash(self.name)


class StockMarketHandler:
    """
    A class that handles stock market data for multiple assets.

    This class provides functionality to manage, retrieve, and iterate over stock market data for various assets. 
    It stores a dictionary that maps each asset to its respective stock data, and offers methods to generate data over time 
    and retrieve asset prices for specific dates.

    Attributes:
        stock_market_dict (dict[Asset, DataFrame]): A dictionary mapping each asset to its corresponding DataFrame 
            containing stock market data. The DataFrame is expected to have a 'Close' column representing closing prices 
            and a DateTime index for dates.
        _dates (list[Timestamp]): A sorted list of unique dates from all the asset data in stock_market_dict.
    """

    def __init__(self, stock_market_dict: dict[Asset, DataFrame]):
        """
        Initializes the StockMarketHandler with a dictionary of stock market data.

        Args:
            stock_market_dict (dict[Asset, DataFrame]): A dictionary where each key is an Asset and the value is 
                a DataFrame containing stock market data for that asset. The DataFrame must have a 'Close' column 
                and a DateTime index representing the trading dates.
        """
        self.stock_market_dict = stock_market_dict
        self._dates = self._get_unique_dates()

    def _get_unique_dates(self) -> list[Timestamp]:
        """
        Returns a list of unique dates across all assets in the stock market data.

        The method iterates through each asset's DataFrame to collect all unique dates and sorts them chronologically.

        Returns:
            list[Timestamp]: A sorted list of unique dates found in the stock market data.
        """
        dates = set()
        for stock in self.stock_market_dict:
            dates = dates.union(set(self.stock_market_dict[stock].index))
        return sorted(list(dates))

    def stock_market_generator(self) -> Generator[dict[Asset, DataFrame], None, None]:
        """
        A generator that yields stock market data up to each unique date.

        For each unique date, it returns the stock market data of all assets, including all data available up to that date.

        Yields:
            tuple[Timestamp, dict[Asset, DataFrame]]: A tuple containing the date and a dictionary where the keys are 
            the assets and the values are their corresponding DataFrames with data up to the given date.
        """
        for date in self._dates:
            stock_market_dict = {
                asset: self.stock_market_dict[asset].loc[:date]
                for asset in self.stock_market_dict.keys()
            }
            yield date, stock_market_dict

    def get_asset_price(self, asset: Asset, date: Timestamp) -> Union[float, None]:
        """
        Returns the closing price of a given asset on a specified date.

        The method checks whether the asset exists and whether the date is within the range of available data. If so, 
        it returns the closing price for that date. If the asset or date is not found, it returns None.

        Args:
            asset (Asset): The asset for which to retrieve the price.
            date (Timestamp): The date on which to retrieve the closing price.

        Returns:
            Union[float, None]: The closing price of the asset on the given date, or None if the asset is not found 
            or the date is outside the range of available data.
        """
        if (
            date < self.stock_market_dict[asset].index[0]
            or asset not in self.stock_market_dict
        ):
            return None

        return self.stock_market_dict[asset].loc[:date, "Close"].iloc[-1]