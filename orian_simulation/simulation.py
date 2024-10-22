from pandas import Timestamp
from dataclasses import dataclass
from typing import Union

import pandas as pd

from orian_simulation.transaction import Wallet, TransactionDTO
from orian_simulation.strategy import AutomatedStrategy
from orian_simulation.market import StockMarketHandler, Asset, Currency


@dataclass
class WalletUpdate:
    """
    Data Transfer Object representing a wallet update.

    Attributes:
        time (Timestamp): The time of the wallet update.
        wallet (Wallet): The wallet object representing the user's funds at that time.
        transaction_dto (TransactionDTO): The transaction that triggered the wallet update.
    """

    time: Timestamp
    wallet_amounts: dict[Union[Asset, Currency], float]
    transaction_dto: TransactionDTO
    balance: float


class OnlineSimulation:
    """
    Class representing an online simulation.
    Args:
        stock_market_handler (StockMarketHandler): The stock market handler object containing the stock market data.
        strategies (list[AutomatedStrategy]): The list of automated strategies to be used.
        wallet (Wallet): The wallet object representing the user's funds.
    Attributes:
        strategies (list[AutomatedStrategy]): The list of automated strategies used in the simulation.
        stock_market_data (pd.DataFrame): The stock market data used for the simulation.
        wallet (Wallet): The wallet object representing the user's funds.
        transaction_history (list): The list of transactions made during the simulation.
    Methods:
        run_simulation(): Runs the simulation by iterating over the stock market data and executing strategies.
    """

    def __init__(
        self,
        stock_market_handler: StockMarketHandler,
        strategies: list[AutomatedStrategy],
        wallet: Wallet,
        max_transaction_date_difference: int = 2,
    ):
        self.strategies = strategies
        self.stock_market_handler = stock_market_handler
        self.wallet = wallet
        self.history: list[WalletUpdate] = []
        self.max_transaction_date_difference = max_transaction_date_difference

    def run_simulation(self) -> None:
        """
        Runs the simulation by iterating over the stock market data and executing strategies.
        """
        stock_market_dict_generator = self.stock_market_handler.stock_market_generator()
        for current_date, stock_market_dict in stock_market_dict_generator:
            for strategy in sorted(self.strategies, key=lambda s: s.priority):
                stock_market_data = stock_market_dict[strategy.trading_asset]

                if len(stock_market_data) == 0:
                    continue

                stock_market_date = stock_market_data.index[-1]
                date_difference = (current_date - stock_market_date).days

                if date_difference > self.max_transaction_date_difference:
                    continue

                transaction = strategy.make_transaction(
                    stock_market_data,
                    wallet=self.wallet,
                )

                if transaction is None:
                    continue

                self.wallet.update_wallet(transaction)
                self.history.append(
                    WalletUpdate(
                        time=current_date,
                        wallet_amounts=self.wallet.amounts.copy(),
                        transaction_dto=transaction,
                        balance=self._get_wallet_balance(date=current_date),
                    )
                )

    def _get_wallet_balance(self, date) -> float:
        """
        Returns the net value of the wallet based on the asset prices in the stock market data.
        """
        balance = 0.0
        for asset, amount in self.wallet.amounts.items():
            if isinstance(asset, Currency):
                continue

            asset_price = self.stock_market_handler.get_asset_price(asset, date)
            if asset_price is not None:
                balance += asset_price * amount

        balance += self.wallet.amounts[self.wallet.base_currency]
        return balance

    @property
    def simulation_history_dataframe(self) -> pd.DataFrame:
        """
        Returns the simulation history as a pandas DataFrame.
        """
        history_df = pd.DataFrame(
            [
                {
                    "strategy": update.transaction_dto.strategy_name,
                    "amount": update.transaction_dto.asset_amount,
                    "transaction_type": update.transaction_dto.transaction_type,
                    "total_balance": update.balance,
                    **update.wallet_amounts,
                }
                for update in self.history
            ],
            index=[update.time for update in self.history],
        )
        return history_df
