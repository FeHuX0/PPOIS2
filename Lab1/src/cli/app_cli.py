from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import TypeAlias

from src.core.enum import CliCommand, CliState
from src.core.exceptions import CardError
from src.services.interfaces import CardServiceInterface

Handler: TypeAlias = Callable[[], None]


class CardCLI:
    """Command-line interface for card operations."""

    def __init__(self, service: CardServiceInterface) -> None:
        self._service = service
        self._state: CliState = CliState.RUNNING
        self._handlers: dict[CliCommand, Handler] = {
            CliCommand.BALANCE_CHECK: self._handle_balance_check,
            CliCommand.WITHDRAW: self._handle_withdraw,
            CliCommand.DEPOSIT: self._handle_deposit,
            CliCommand.PAYMENT: self._handle_payment,
            CliCommand.BLOCK: self._handle_block,
            CliCommand.UNBLOCK: self._handle_unblock,
            CliCommand.CHANGE_LIMITS: self._handle_limit_change,
            CliCommand.HISTORY: self._handle_history,
        }

    def run(self) -> None:
        card = self._service.card
        print("Система обслуживания банковской карты")
        print(f"Карта: {card.masked_number}, владелец: {card.owner.full_name}")
        while self._state == CliState.RUNNING:
            self._print_menu()
            command = self._parse_command(input("Выберите пункт меню: ").strip())
            if command is None:
                print("Неизвестная команда.")
                continue
            if command == CliCommand.EXIT:
                self._state = CliState.STOPPED
                print("Завершение работы.")
                break
            handler = self._handlers.get(command)
            if handler is None:
                print("Неизвестная команда.")
                continue
            try:
                handler()
            except (CardError, ValueError) as error:
                print(f"Ошибка: {error}")

    @staticmethod
    def _print_menu() -> None:
        print("\nДоступные операции:")
        print(f"{CliCommand.BALANCE_CHECK.value} - Проверка баланса")
        print(f"{CliCommand.WITHDRAW.value} - Снятие денег")
        print(f"{CliCommand.DEPOSIT.value} - Внесение денег")
        print(f"{CliCommand.PAYMENT.value} - Оплата товаров и услуг")
        print(f"{CliCommand.BLOCK.value} - Блокировка карты")
        print(f"{CliCommand.UNBLOCK.value} - Разблокировка карты")
        print(f"{CliCommand.CHANGE_LIMITS.value} - Изменение лимитов")
        print(f"{CliCommand.HISTORY.value} - Просмотр журнала транзакций")
        print(f"{CliCommand.EXIT.value} - Выход")

    @staticmethod
    def _parse_command(raw_command: str) -> CliCommand | None:
        try:
            return CliCommand(raw_command)
        except ValueError:
            return None

    def _handle_balance_check(self) -> None:
        pin_code = self._read_pin()
        balance = self._service.get_balance(pin_code=pin_code)
        print(f"Текущий баланс: {balance}")

    def _handle_withdraw(self) -> None:
        amount = self._read_amount("Введите сумму снятия: ")
        pin_code = self._read_pin()
        balance = self._service.withdraw(amount=amount, pin_code=pin_code)
        print(f"Операция выполнена. Новый баланс: {balance}")

    def _handle_deposit(self) -> None:
        amount = self._read_amount("Введите сумму внесения: ")
        pin_code = self._read_pin()
        balance = self._service.deposit(amount=amount, pin_code=pin_code)
        print(f"Операция выполнена. Новый баланс: {balance}")

    def _handle_payment(self) -> None:
        amount = self._read_amount("Введите сумму оплаты: ")
        pin_code = self._read_pin()
        balance = self._service.pay(amount=amount, pin_code=pin_code)
        print(f"Операция выполнена. Новый баланс: {balance}")

    def _handle_block(self) -> None:
        pin_code = self._read_pin()
        self._service.block_card(pin_code=pin_code)
        print("Карта заблокирована.")

    def _handle_unblock(self) -> None:
        pin_code = self._read_pin()
        self._service.unblock_card(pin_code=pin_code)
        print("Карта разблокирована.")

    def _handle_limit_change(self) -> None:
        withdrawal_limit = self._read_amount("Новый лимит снятия: ")
        payment_limit = self._read_amount("Новый лимит оплаты: ")
        pin_code = self._read_pin()
        limits = self._service.change_limits(
            withdrawal_limit=withdrawal_limit,
            payment_limit=payment_limit,
            pin_code=pin_code,
        )
        print(
            "Лимиты изменены: "
            f"снятие={limits.withdrawal_limit}, "
            f"оплата={limits.payment_limit}"
        )

    def _handle_history(self) -> None:
        pin_code = self._read_pin()
        transactions = self._service.get_transactions(pin_code=pin_code)
        if not transactions:
            print("Журнал транзакций пуст.")
            return
        print("\nЖурнал транзакций:")
        for index, transaction in enumerate(transactions, start=1):
            print(
                f"{index}. {transaction.timestamp:%Y-%m-%d %H:%M:%S} | "
                f"{transaction.transaction_type.value} | "
                f"amount={transaction.amount} | "
                f"balance={transaction.balance_after} | "
                f"{transaction.description}"
            )

    @staticmethod
    def _read_pin() -> str:
        pin_code = input("Введите PIN: ").strip()
        if not pin_code:
            raise ValueError("PIN не может быть пустым.")
        return pin_code

    @staticmethod
    def _read_amount(prompt: str) -> Decimal:
        raw_value = input(prompt).strip().replace(",", ".")
        try:
            amount = Decimal(raw_value)
        except InvalidOperation as error:
            raise ValueError("Некорректный формат суммы.") from error
        return amount
