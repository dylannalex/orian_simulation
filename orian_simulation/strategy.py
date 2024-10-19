from pandas import DataFrame

from orian_simulation.market import Asset
from orian_simulation.trading.algorithm import TradingAlgorithm
from orian_simulation.trading.prediction import PredictionEnum
from orian_simulation.transaction import (
    TransactionQuantityManager,
    TransactionTrigger,
    TransactionDTO,
    Wallet,
    TransactionEnum,
)


class AutomatedStrategy:
    """
    Class representing an automated trading strategy.

    Attributes:
    - trading_algorithm (TradingAlgorithm): The trading algorithm used by the strategy.
    - trading_asset (Asset): The asset being traded by the strategy.
    - priority (int): The priority of the strategy (lower values are executed first).
    - transaction_trigger (TransactionTrigger): The trigger for executing transactions.
    - buy_transaction_quantity_manager (TransactionQuantityManager): The quantity manager for buy transactions.
    - sell_transaction_quantity_manager (TransactionQuantityManager): The quantity manager for sell transactions.
    - predictions (list[PredictionEnum]): A list of predictions made by the trading algorithm.
    - name (str): The name of the strategy (optional).

    Methods:
    - make_transaction(stock_market_data: DataFrame, wallet: Wallet) -> TransactionDTO:
        Makes a transaction based on the current stock market data and wallet state
        using the strategy's trading algorithm and transaction trigger.
    """

    def __init__(
        self,
        trading_algorithm: TradingAlgorithm,
        trading_asset: Asset,
        priority: int,
        transaction_trigger: TransactionTrigger,
        buy_transaction_quantity_manager: TransactionQuantityManager,
        sell_transaction_quantity_manager: TransactionQuantityManager,
        name: str = None,
    ):
        self.trading_algorithm = trading_algorithm
        default_name = f"{trading_algorithm.name}({trading_asset.name})"
        self.name = name or default_name
        self.trading_asset = trading_asset
        self.priority = priority
        self.transaction_trigger = transaction_trigger
        self.buy_transaction_quantity_manager = buy_transaction_quantity_manager
        self.sell_transaction_quantity_manager = sell_transaction_quantity_manager
        self.predictions: list[PredictionEnum] = []

    def make_transaction(
        self, stock_market_data: DataFrame, wallet: Wallet
    ) -> TransactionDTO:
        """
        Makes a transaction based on the given stock market data and wallet.
        Args:
            stock_market_data (DataFrame): The stock market data used for making the transaction.
            wallet (Wallet): The wallet containing the funds for the transaction.
        Returns:
            TransactionDTO: The transaction data transfer object representing the transaction.
        """
        # Get prediction from trading algorithm
        prediction = self.trading_algorithm.make_prediction(stock_market_data)
        self.predictions.append(prediction)

        # Evaluate predictions and trigger transaction
        transaction_type = self.transaction_trigger.evaluate_predictions(
            self.predictions
        )

        if transaction_type is TransactionEnum.HOLD:
            return None

        transaction_dto = TransactionDTO(
            transaction_type=transaction_type,
            currency=wallet.base_currency,
            asset=self.trading_asset,
            asset_price=stock_market_data["Close"].iloc[-1],
            transaction_date=stock_market_data.index[-1],
            asset_amount=None,
            strategy_name=self.name,
        )

        # Compute asset amount for transaction
        if transaction_type is TransactionEnum.BUY:
            transaction_dto = (
                self.buy_transaction_quantity_manager.compute_asset_amount(
                    transaction_dto
                )
            )
        elif transaction_type is TransactionEnum.SELL:
            transaction_dto = (
                self.sell_transaction_quantity_manager.compute_asset_amount(
                    transaction_dto
                )
            )

        return transaction_dto
