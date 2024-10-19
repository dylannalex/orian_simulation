from dataclasses import dataclass
from typing import Union, Generator

from pandas import DataFrame, Timestamp


@dataclass
class Asset:
    name: str

    def __eq__(self, other: "Asset") -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Currency:
    name: str

    def __eq__(self, other: "Currency") -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class StockMarketHandler:
    def __init__(self, stock_market_dict: dict[Asset, DataFrame]):
        self.stock_market_dict = stock_market_dict
        self._dates = self._get_unique_dates()

    def _get_unique_dates(self) -> list[Timestamp]:
        """Return a list of unique dates in the stock market data.

        Returns:
            list[Timestamp]: A list of unique dates in the stock market data.
        """
        dates = set()
        for stock in self.stock_market_dict:
            dates = dates.union(set(self.stock_market_dict[stock].index))
        return sorted(list(dates))

    def stock_market_generator(self) -> Generator[dict[Asset, DataFrame], None, None]:
        for date in self._dates:
            stock_market_dict = {
                asset: self.stock_market_dict[asset].loc[:date]
                for asset in self.stock_market_dict.keys()
            }
            yield date, stock_market_dict

    def get_asset_price(self, asset: Asset, date: Timestamp) -> Union[float, None]:
        """Return the price of the given asset on the given date.

        Args:
            asset (Asset): The asset for which to get the price.
            date (Timestamp): The date for which to get the price.

        Returns:
            Union[float, None]: The price of the asset on the given date, or \
            None if the asset is not found or the date is before the first date \
            in the data.
        """
        if (
            date < self.stock_market_dict[asset].index[0]
            or asset not in self.stock_market_dict
        ):
            return None

        return self.stock_market_dict[asset].loc[:date, "Close"].iloc[-1]
