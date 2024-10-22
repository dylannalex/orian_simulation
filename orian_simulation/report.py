from orian_simulation.simulation import WalletUpdate
from orian_simulation.transaction import TransactionEnum


class Report:
    """
    A class that generates a financial report based on wallet updates from trading simulations.

    The report evaluates key performance metrics such as return on investment (ROI), 
    net profit, maximum profit, maximum loss, and transaction statistics. 

    Args:
        wallet_updates (list[WalletUpdate]): A list of WalletUpdate objects that represent 
        the changes in the wallet's balance over time.
    
    Attributes:
        balance_history (list[float]): A list storing the balance after each wallet update.
        transaction_history (list[TransactionEnum]): A list storing the types of transactions 
        (BUY/SELL) after each wallet update.

    Methods:
        generate_report() -> dict:
            Generates and returns a financial report with the following metrics:
            - ROI
            - Net profit
            - Maximum profit
            - Maximum loss
            - Total transactions
            - Total buy transactions
            - Total sell transactions
    """

    def __init__(self, wallet_updates: list[WalletUpdate]):
        """
        Initializes the Report class with the provided wallet updates, extracting balance and transaction histories.

        Args:
            wallet_updates (list[WalletUpdate]): A list of WalletUpdate objects containing 
            balance and transaction data from the simulation.
        """
        self.balance_history = [update.balance for update in wallet_updates]
        self.transaction_history = [
            update.transaction_dto.transaction_type for update in wallet_updates
        ]

    def generate_report(self) -> dict:
        """
        Generates a report based on the wallet's balance and transaction history.

        The report includes metrics such as ROI, net profit, maximum profit, maximum loss, 
        and transaction statistics (total transactions, buy/sell breakdown).

        Returns:
            dict: A dictionary containing the following metrics:
            - roi (float): Return on Investment calculated as (final_balance - initial_balance) / initial_balance.
            - net_profit (float): The net profit from the simulation (final_balance - initial_balance).
            - max_profit (float): The maximum profit achieved during the simulation.
            - max_loss (float): The maximum loss during the simulation.
            - total_transactions (int): The total number of transactions made.
            - total_buy_transactions (int): The total number of buy transactions made.
            - total_sell_transactions (int): The total number of sell transactions made.
        """
        initial_balance = self.balance_history[0]
        final_balance = self.balance_history[-1]
        roi = (final_balance - initial_balance) / initial_balance
        net_profit = final_balance - initial_balance
        max_profit = max(self.balance_history) - initial_balance
        max_loss = min(self.balance_history) - initial_balance
        total_transactions = len(self.transaction_history)
        total_buy_transactions = sum(
            [t == TransactionEnum.BUY for t in self.transaction_history]
        )
        total_sell_transactions = sum(
            [t == TransactionEnum.SELL for t in self.transaction_history]
        )
        return {
            "roi": roi,
            "net_profit": net_profit,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "total_transactions": total_transactions,
            "total_buy_transactions": total_buy_transactions,
            "total_sell_transactions": total_sell_transactions,
        }
