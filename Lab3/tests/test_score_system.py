from pathlib import Path

from crimsoland.systems.score_system import ScoreSystem


def test_score_system_loads_and_sorts_entries(temp_game_data):
    system = ScoreSystem(temp_game_data['highscores_file'], limit=10, name_max_length=12)
    scores = system.top_scores()
    assert scores[0].score >= scores[-1].score
    assert system.qualifies(9999)
    assert not system.is_first_place(scores[0].score)


def test_score_system_records_and_truncates_name(tmp_path: Path):
    path = tmp_path / 'scores.json'
    system = ScoreSystem(path, limit=3, name_max_length=5)
    system.record_score('LongPlayer', 25, played_at='2026-03-14')
    system.record_score('Bob', 50, played_at='2026-03-13')
    system.record_score('Ada', 40, played_at='2026-03-12')
    system.record_score('Eve', 10, played_at='2026-03-11')
    scores = system.top_scores()
    assert [entry.score for entry in scores] == [50, 40, 25]
    assert scores[-1].name == 'LongP'


def test_score_system_handles_broken_json(tmp_path: Path):
    path = tmp_path / 'broken.json'
    path.write_text('{broken', encoding='utf-8')
    system = ScoreSystem(path)
    assert system.top_scores() == []
