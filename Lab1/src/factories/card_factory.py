from collections.abc import Callable
from decimal import Decimal

from src.domain.bank import Bank
from src.domain.bank_card import BankCard
from src.domain.card_limits import CardLimits
from src.domain.card_owner import CardOwner
from src.services.card_service import CardService


class CardFactory:
    """Factory for building card aggregates and related services."""

    @staticmethod
    def create_default_card() -> BankCard:
        return BankCard(
            card_number="1234567812345678",
            pin_code="1234",
            bank=Bank(name="POIS Bank", bic="POISRU01"),
            owner=CardOwner(full_name="Ivan Ivanov", owner_id="USR-001"),
            limits=CardLimits(
                withdrawal_limit=Decimal("1000.00"),
                payment_limit=Decimal("1500.00"),
            ),
            balance=Decimal("10000.00"),
        )

    @staticmethod
    def create_service(
        card: BankCard,
        on_state_change: Callable[[BankCard], None] | None = None,
    ) -> CardService:
        return CardService(card=card, on_state_change=on_state_change)

    @classmethod
    def create_default_service(
        cls,
        on_state_change: Callable[[BankCard], None] | None = None,
    ) -> CardService:
        return cls.create_service(
            card=cls.create_default_card(),
            on_state_change=on_state_change,
        )
