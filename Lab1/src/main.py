from pathlib import Path

from src.cli.app_cli import CardCLI
from src.factories.card_factory import CardFactory
from src.storage.json_card_state import JsonCardStateRepository


def main() -> None:
    state_repository = JsonCardStateRepository(path=Path("card_state.json"))
    card = state_repository.load_or_default(CardFactory.create_default_card())
    cli = CardCLI(
        service=CardFactory.create_service(
            card=card,
            on_state_change=state_repository.save,
        )
    )
    cli.run()


if __name__ == "__main__":
    main()
