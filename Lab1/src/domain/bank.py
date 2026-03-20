from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Bank:
    """Bank metadata used by the card."""

    name: str
    bic: str

    def __post_init__(self) -> None:
        self._validate_name(self.name)
        self._validate_bic(self.bic)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name.strip():
            raise ValueError("Bank name cannot be empty.")

    @staticmethod
    def _validate_bic(bic: str) -> None:
        if not bic.strip():
            raise ValueError("BIC cannot be empty.")
