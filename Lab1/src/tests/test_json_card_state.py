from decimal import Decimal
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from src.core.enum import CardStatus, TransactionType
from src.domain.bank import Bank
from src.domain.bank_card import BankCard
from src.domain.card_limits import CardLimits
from src.domain.card_owner import CardOwner
from src.services.card_service import CardService
from src.storage.json_card_state import JsonCardStateRepository


class JsonCardStateRepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_directory = Path("tests") / ".tmp" / uuid4().hex
        self._temp_directory.mkdir(parents=True, exist_ok=True)
        self.state_path = self._temp_directory / "card_state.json"
        self.repository = JsonCardStateRepository(path=self.state_path)

    def tearDown(self) -> None:
        shutil.rmtree(self._temp_directory, ignore_errors=True)

    @staticmethod
    def _build_card() -> BankCard:
        return BankCard(
            card_number="1234567812345678",
            pin_code="1234",
            bank=Bank(name="Test Bank", bic="TESTBIC1"),
            owner=CardOwner(full_name="Test User", owner_id="U-1"),
            limits=CardLimits(
                withdrawal_limit=Decimal("500.00"),
                payment_limit=Decimal("700.00"),
            ),
            balance=Decimal("1000.00"),
        )

    def test_load_or_default_saves_initial_state_when_file_missing(self) -> None:
        card = self._build_card()

        loaded_card = self.repository.load_or_default(card)

        self.assertEqual(loaded_card.balance, Decimal("1000.00"))
        self.assertTrue(self.state_path.exists())

    def test_save_and_load_preserves_state(self) -> None:
        card = self._build_card()
        service = CardService(card=card, on_state_change=self.repository.save)

        service.deposit(amount=Decimal("150.00"), pin_code="1234")
        service.change_limits(
            withdrawal_limit=Decimal("300.00"),
            payment_limit=Decimal("600.00"),
            pin_code="1234",
        )
        service.block_card(pin_code="1234")

        restored_card = self.repository.load()

        self.assertEqual(restored_card.balance, Decimal("1150.00"))
        self.assertEqual(restored_card.limits.withdrawal_limit, Decimal("300.00"))
        self.assertEqual(restored_card.limits.payment_limit, Decimal("600.00"))
        self.assertEqual(restored_card.status, CardStatus.BLOCKED)
        self.assertEqual(len(restored_card.transactions), 3)
        self.assertEqual(
            [transaction.transaction_type for transaction in restored_card.transactions],
            [
                TransactionType.DEPOSIT,
                TransactionType.LIMIT_CHANGE,
                TransactionType.BLOCK,
            ],
        )


if __name__ == "__main__":
    unittest.main()
