from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Union

from orian_simulation.trading.prediction import PredictionEnum
from orian_simulation.market import Asset, Currency


class TransactionEnum(Enum):
    """
    Enumeration of possible transaction types.
    """

    SELL = 0
    BUY = 1
    HOLD = 2


@dataclass
class TransactionDTO:
    """
    Data Transfer Object representing a financial transaction.

    Attributes:
    - transaction_type (TransactionEnum): The type of transaction (BUY, SELL, HOLD).
    - asset (Asset): The asset involved in the transaction.
    - currency (Currency): The currency involved in the transaction.
    - asset_price (float): The price of the asset at the time of the transaction.
    - asset_amount (float): The amount of the asset being transacted.
    - transaction_date (datetime): The date and time of the transaction.
    - strategy_name (str): The name of the strategy that triggered the transaction.
    """

    transaction_type: TransactionEnum
    asset: Asset
    currency: Currency
    asset_price: float
    asset_amount: float
    transaction_date: datetime
    strategy_name: str


@dataclass
class Wallet:
    """
    Represents a wallet containing various assets and a base currency.

    Attributes:
    - amounts (dict[Asset or Currency, float]): A dictionary holding the amount of each asset and currency \
        in the wallet.
    - base_currency (Currency): The base currency for the wallet.

    Methods:
    - update_wallet(transaction_dto: TransactionDTO) -> None:
        Updates the wallet based on a transaction.
    """

    amounts: dict[Union[Asset, Currency], float]
    base_currency: Currency

    def __post_init__(self):
        # Initialize the base currency amount to 0 if not present
        if not self.base_currency in self.amounts.keys():
            self.amounts[self.base_currency] = 0

        # Initialize the assets list
        self.assets = [
            asset for asset in self.amounts.keys() if isinstance(asset, Asset)
        ]

    def update_wallet(self, transaction_dto: TransactionDTO) -> None:
        """
        Updates the wallet based on a transaction.

        Parameters:
        - transaction_dto (TransactionDTO): The transaction details.

        Raises:
        - ValueError: If the asset involved in the transaction is not available in the wallet.
        """
        if not transaction_dto.asset in self.amounts.keys():
            raise ValueError(
                f"Asset '{transaction_dto.asset}' is not available in wallet"
            )

        currency_amount = transaction_dto.asset_amount * transaction_dto.asset_price

        if transaction_dto.transaction_type == TransactionEnum.SELL:
            self.amounts[transaction_dto.asset] -= transaction_dto.asset_amount
            self.amounts[self.base_currency] += currency_amount

        elif transaction_dto.transaction_type == TransactionEnum.BUY:
            self.amounts[transaction_dto.asset] += transaction_dto.asset_amount
            self.amounts[self.base_currency] -= currency_amount


class TransactionTrigger(ABC):
    """
    Abstract base class for evaluating transaction triggers based on prediction history.
    """

    @abstractmethod
    def evaluate_predictions(
        self, prediction_dto_history: list[PredictionEnum]
    ) -> TransactionEnum:
        """
        Evaluates the prediction history and determines the type of transaction to be made.

        Parameters:
        - prediction_dto_history (list[PredictionEnum]): A list of prediction data transfer objects.

        Returns:
        - TransactionEnum: The type of transaction determined based on the predictions.
        """
        pass


class TransactionQuantityManager(ABC):
    """
    Abstract base class for managing the quantity of assets to be transacted.
    """

    @abstractmethod
    def __init__(self, wallet: Wallet):
        pass

    @abstractmethod
    def compute_asset_amount(self, transaction_dto: TransactionDTO) -> TransactionDTO:
        """
        Computes the amount of the asset to be transacted.

        Parameters:
        - transaction_dto (TransactionDTO): The transaction details.

        Returns:
        - TransactionDTO: The transaction DTO with updated asset amount.
        """
        pass


class TransactionTriggerByRepeatedPredictions(TransactionTrigger):
    """
    Implements a transaction trigger based on repeated predictions.

    Attributes:
    - repetitions (int): The number of repeated predictions to consider for triggering a transaction.

    Methods:
    - evaluate_predictions(prediction_dto_history: list[PredictionEnum]) -> TransactionEnum:
        Evaluates the prediction history and triggers a transaction if conditions are met.
    """

    def __init__(self, repetitions: int):
        self.repetitions = repetitions

    def evaluate_predictions(
        self, prediction_dto_history: list[PredictionEnum]
    ) -> TransactionEnum:
        """
        Evaluates the prediction history and determines the transaction type based on repeated predictions.

        Parameters:
        - prediction_dto_history (list[PredictionEnum]): A list of prediction data transfer objects.

        Returns:
        - TransactionEnum: The type of transaction determined based on the repeated predictions.
        """
        last_predictions = prediction_dto_history[-self.repetitions :]

        if all([p == PredictionEnum.INCREASE for p in last_predictions]):
            return TransactionEnum.BUY

        elif all([p == PredictionEnum.DECREASE for p in last_predictions]):
            return TransactionEnum.SELL

        return TransactionEnum.HOLD


class TransactionQuantityManagerByWalletPercentage(TransactionQuantityManager):
    """
    Manages the transaction quantity based on a percentage of the wallet's holdings.

    Attributes:
    - wallet (Wallet): The wallet containing the assets.
    - percentage (float): The percentage of the wallet's holdings to transact.

    Methods:
    - compute_asset_amount(transaction_dto: TransactionDTO) -> TransactionDTO:
        Computes the amount of the asset to be transacted based on the wallet's holdings and the specified percentage.
    """

    def __init__(self, wallet: Wallet, percentage: float):
        self.wallet = wallet
        self.percentage = percentage

    def compute_asset_amount(self, transaction_dto: TransactionDTO) -> TransactionDTO:
        """
        Computes the amount of the asset to be transacted based on the wallet's holdings and the specified percentage.

        Parameters:
        - transaction_dto (TransactionDTO): The transaction details.

        Returns:
        - TransactionDTO: The transaction DTO with updated asset amount.
        """
        # Compute asset amount based on transaction type
        if transaction_dto.transaction_type == TransactionEnum.BUY:
            currency_amount = self.wallet.amounts[self.wallet.base_currency]
            currency_amount *= self.percentage
            asset_amount = currency_amount / transaction_dto.asset_price

        elif transaction_dto.transaction_type == TransactionEnum.SELL:
            wallet_asset_amount = self.wallet.amounts[transaction_dto.asset]
            asset_amount = wallet_asset_amount * self.percentage

        else:
            asset_amount = 0

        # Convert to integer if asset does not allow float amounts
        if not transaction_dto.asset.allow_float_amount:
            asset_amount = int(asset_amount)

        transaction_dto.asset_amount = asset_amount
        return transaction_dto


class TransactionQuantityManagerByFixedAmount(TransactionQuantityManager):
    """
    Manages the transaction quantity based on fixed amounts for buying and selling.

    Attributes:
    - wallet (Wallet): The wallet containing the assets.
    - currency_amount_to_buy (float): The fixed amount of base currency to use for buying assets.
    - asset_amount_to_sell (float): The fixed amount of assets to sell.

    Methods:
    - compute_asset_amount(transaction_dto: TransactionDTO) -> TransactionDTO:
        Computes the amount of the asset to be transacted based on the fixed amounts for buying and selling.
    """

    def __init__(
        self, wallet: Wallet, fixed_amount: float
    ):
        self.wallet = wallet
        self.fixed_amount = fixed_amount

    def compute_asset_amount(self, transaction_dto: TransactionDTO) -> TransactionDTO:
        """
        Computes the amount of the asset to be transacted based on the fixed amounts for buying and selling.

        Parameters:
        - transaction_dto (TransactionDTO): The transaction details.

        Returns:
        - TransactionDTO: The transaction DTO with updated asset amount.
        """
        # Convert to integer if asset does not allow float amounts
        if not transaction_dto.asset.allow_float_amount:
            fixed_amount = int(self.fixed_amount)
        else:
            fixed_amount = self.fixed_amount

        # Compute asset amount based on transaction type
        if transaction_dto.transaction_type == TransactionEnum.BUY:
            wallet_currency_amount = self.wallet.amounts[self.wallet.base_currency]
            currency_amount = min(wallet_currency_amount, fixed_amount)
            asset_amount = currency_amount / transaction_dto.asset_price

        elif transaction_dto.transaction_type == TransactionEnum.SELL:
            wallet_asset_amount = self.wallet.amounts[transaction_dto.asset]
            asset_amount = min(wallet_asset_amount, fixed_amount)

        else:
            asset_amount = 0

        transaction_dto.asset_amount = asset_amount
        return transaction_dto
