from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class ScoreEntry:
    name: str
    score: int
    date: str


class ScoreSystem:
    def __init__(self, file_path: str | Path, limit: int = 10, name_max_length: int = 12):
        self.file_path = Path(file_path)
        self.limit = limit
        self.name_max_length = name_max_length
        self._entries: list[ScoreEntry] = []
        self.load()

    def load(self) -> list[ScoreEntry]:
        if not self.file_path.exists():
            self._entries = []
            return []
        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._entries = []
            return []
        entries: list[ScoreEntry] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            score = item.get("score")
            date = item.get("date")
            if isinstance(name, str) and isinstance(score, int) and isinstance(date, str):
                entries.append(ScoreEntry(name=name, score=score, date=date))
        self._entries = self._sort_entries(entries)[: self.limit]
        return self.top_scores()

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(entry) for entry in self._entries[: self.limit]]
        self.file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def top_scores(self) -> list[ScoreEntry]:
        return list(self._entries[: self.limit])

    def is_first_place(self, score: int) -> bool:
        if not self._entries:
            return True
        return score > self._entries[0].score

    def qualifies(self, score: int) -> bool:
        if len(self._entries) < self.limit:
            return True
        return score >= self._entries[self.limit - 1].score

    def record_score(
        self,
        name: str,
        score: int,
        played_at: str | None = None,
    ) -> list[ScoreEntry]:
        safe_name = (name.strip() or "PLAYER")[: self.name_max_length]
        entry = ScoreEntry(
            name=safe_name,
            score=int(score),
            date=played_at or datetime.now().strftime("%Y-%m-%d"),
        )
        self._entries.append(entry)
        self._entries = self._sort_entries(self._entries)[: self.limit]
        self.save()
        return self.top_scores()

    @staticmethod
    def _sort_entries(entries: list[ScoreEntry]) -> list[ScoreEntry]:
        return sorted(entries, key=lambda item: (-item.score, item.date, item.name.lower()))
