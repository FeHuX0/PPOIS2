from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from src.core.enum import CardStatus, TransactionType
from src.domain.bank import Bank
from src.domain.bank_card import BankCard
from src.domain.card_limits import CardLimits
from src.domain.card_owner import CardOwner
from src.domain.transaction import Transaction


class JsonCardStateRepository:
    """Save and load card state in JSON format."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, card: BankCard) -> None:
        payload = {
            "version": 1,
            "card": {
                "card_number": card.card_number,
                "pin_code": card.pin_code,
                "bank": {
                    "name": card.bank.name,
                    "bic": card.bank.bic,
                },
                "owner": {
                    "full_name": card.owner.full_name,
                    "owner_id": card.owner.owner_id,
                },
                "limits": {
                    "withdrawal_limit": str(card.limits.withdrawal_limit),
                    "payment_limit": str(card.limits.payment_limit),
                },
                "balance": str(card.balance),
                "status": card.status.value,
                "transactions": [
                    {
                        "transaction_id": transaction.transaction_id,
                        "timestamp": transaction.timestamp.isoformat(),
                        "transaction_type": transaction.transaction_type.value,
                        "amount": str(transaction.amount),
                        "balance_after": str(transaction.balance_after),
                        "description": transaction.description,
                    }
                    for transaction in card.transactions
                ],
            },
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> BankCard:
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        card_data = payload["card"]
        limits_data = card_data["limits"]
        card = BankCard(
            card_number=card_data["card_number"],
            pin_code=card_data["pin_code"],
            bank=Bank(
                name=card_data["bank"]["name"],
                bic=card_data["bank"]["bic"],
            ),
            owner=CardOwner(
                full_name=card_data["owner"]["full_name"],
                owner_id=card_data["owner"]["owner_id"],
            ),
            limits=CardLimits(
                withdrawal_limit=Decimal(limits_data["withdrawal_limit"]),
                payment_limit=Decimal(limits_data["payment_limit"]),
            ),
            balance=Decimal(card_data["balance"]),
            status=CardStatus(card_data["status"]),
        )
        for transaction_data in card_data.get("transactions", []):
            card.add_transaction(
                Transaction(
                    transaction_type=TransactionType(
                        transaction_data["transaction_type"]
                    ),
                    amount=Decimal(transaction_data["amount"]),
                    balance_after=Decimal(transaction_data["balance_after"]),
                    description=transaction_data["description"],
                    timestamp=datetime.fromisoformat(transaction_data["timestamp"]),
                    transaction_id=transaction_data["transaction_id"],
                )
            )
        return card

    def load_or_default(self, default_card: BankCard) -> BankCard:
        if self._path.exists():
            return self.load()
        self.save(default_card)
        return default_card
