from pathlib import Path

from src.ingest.xml_dom_writer import AthleteXmlDomWriter
from src.models.athlete import Athlete


RANKS = [
    "1-й юношеский",
    "2-й разряд",
    "3й-разряд",
    "кмс",
    "мастер спорта",
]

SQUADS = ["основной", "запасной", "n/a"]

SPORTS_AND_POSITIONS = {
    "Футбол": ["вратарь", "защитник", "полузащитник", "нападающий"],
    "Баскетбол": ["разыгрывающий", "атакующий защитник", "лёгкий форвард", "центровой"],
    "Волейбол": ["связующий", "доигровщик", "либеро", "диагональный"],
    "Хоккей": ["вратарь", "защитник", "центральный нападающий", "крайний нападающий"],
    "Плавание": ["спринтер", "стайер", "баттерфляй", "брасс"],
    "Лёгкая атлетика": ["спринтер", "барьерист", "прыгун", "марафонец"],
    "Теннис": ["одиночный разряд", "парный разряд", "универсал"],
    "Бокс": ["лёгкий вес", "средний вес", "тяжёлый вес"],
}

FIRST_NAMES = [
    "Алексей", "Дмитрий", "Максим", "Илья", "Егор", "Никита", "Сергей", "Павел",
    "Андрей", "Роман", "Олег", "Владимир", "Иван", "Матвей", "Тимофей", "Арсений",
    "Кирилл", "Глеб", "Виктор", "Фёдор", "Константин", "Василий", "Руслан", "Георгий",
]

LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Кузнецов", "Орлов", "Савельев", "Жуков", "Емельянов",
    "Федоров", "Баранов", "Титов", "Новиков", "Громов", "Макаров", "Лазарев", "Сорокин",
    "Тарасов", "Волков", "Николаев", "Богданов", "Ковалёв", "Михайлов", "Зайцев", "Комаров",
]

PATRONYMICS = [
    "Алексеевич", "Дмитриевич", "Игоревич", "Павлович", "Сергеевич", "Олегович",
    "Владимирович", "Романович", "Никитич", "Максимович", "Егорович", "Ильич",
]


def build_demo_athletes(amount: int, offset: int = 0) -> list[Athlete]:
    athletes: list[Athlete] = []
    sports = list(SPORTS_AND_POSITIONS.items())

    for index in range(amount):
        serial = index + offset
        first_name = FIRST_NAMES[serial % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(serial // len(FIRST_NAMES)) % len(LAST_NAMES)]
        patronymic = PATRONYMICS[(serial // 3) % len(PATRONYMICS)]
        sport, positions = sports[serial % len(sports)]
        position = positions[serial % len(positions)]
        squad = SQUADS[serial % len(SQUADS)]
        rank = RANKS[(serial // 2) % len(RANKS)]
        titles = (serial * 3) % 18

        athletes.append(
            Athlete(
                full_name=f"{last_name} {first_name} {patronymic}",
                squad=squad,
                position=position,
                titles=titles,
                sport=sport,
                rank=rank,
            )
        )

    return athletes


def generate_sample_xml_files(
    target_directory: str | Path,
    files_count: int = 3,
    items_per_file: int = 60,
) -> list[Path]:
    writer = AthleteXmlDomWriter()
    target_path = Path(target_directory)
    target_path.mkdir(parents=True, exist_ok=True)
    output_files: list[Path] = []

    for file_index in range(files_count):
        athletes = build_demo_athletes(items_per_file, offset=file_index * items_per_file)
        file_path = target_path / f"athletes_demo_{file_index + 1}.xml"
        writer.write(athletes, file_path)
        output_files.append(file_path)

    return output_files


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    generate_sample_xml_files(project_root / "sample_data")
