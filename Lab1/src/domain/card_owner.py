from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CardOwner:
    """Card owner metadata."""

    full_name: str
    owner_id: str

    def __post_init__(self) -> None:
        self._validate_full_name(self.full_name)
        self._validate_owner_id(self.owner_id)

    @staticmethod
    def _validate_full_name(full_name: str) -> None:
        if not full_name.strip():
            raise ValueError("Owner full name cannot be empty.")

    @staticmethod
    def _validate_owner_id(owner_id: str) -> None:
        if not owner_id.strip():
            raise ValueError("Owner ID cannot be empty.")
