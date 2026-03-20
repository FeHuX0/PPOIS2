from __future__ import annotations

import random

from crimsoland.events import ENEMY_SPAWN, START_WAVE, WAVE_COMPLETED, post_event


class WaveSystem:
    def __init__(
        self,
        waves_config: list[dict],
        wave_break_ms: int,
        rng: random.Random | None = None,
    ):
        self.waves = waves_config
        self.wave_break_ms = wave_break_ms
        self.rng = rng or random.Random()
        self.current_wave_index = -1
        self.spawn_queue: list[dict] = []
        self.started = False
        self.finished = False
        self.wave_active = False
        self.waiting_for_next_wave = False
        self.next_wave_at = 0

    @property
    def current_wave_number(self) -> int:
        if self.current_wave_index < 0:
            return 0
        return self.waves[self.current_wave_index]["number"]

    def reset(self) -> None:
        self.current_wave_index = -1
        self.spawn_queue.clear()
        self.started = False
        self.finished = False
        self.wave_active = False
        self.waiting_for_next_wave = False
        self.next_wave_at = 0

    def start(self, now_ms: int) -> None:
        self.reset()
        self.started = True
        self.next_wave_at = now_ms

    def update(self, now_ms: int, living_enemy_count: int) -> None:
        if not self.started or self.finished:
            return
        if self.waiting_for_next_wave and now_ms >= self.next_wave_at:
            self.waiting_for_next_wave = False
            self._schedule_next_wave(now_ms)
        elif self.current_wave_index == -1 and now_ms >= self.next_wave_at:
            self._schedule_next_wave(now_ms)
        spawned_any = False
        while self.spawn_queue and self.spawn_queue[0]["spawn_time_ms"] <= now_ms:
            spawn = self.spawn_queue.pop(0)
            post_event(
                ENEMY_SPAWN,
                enemy_type=spawn["enemy_type"],
                wave_number=self.current_wave_number,
            )
            spawned_any = True
        if self.wave_active and not self.spawn_queue and living_enemy_count == 0 and not spawned_any:
            self.wave_active = False
            final_wave = self.current_wave_index == len(self.waves) - 1
            post_event(
                WAVE_COMPLETED,
                wave_number=self.current_wave_number,
                final_wave=final_wave,
            )
            if final_wave:
                self.finished = True
            else:
                self.waiting_for_next_wave = True
                self.next_wave_at = now_ms + self.wave_break_ms

    def _schedule_next_wave(self, now_ms: int) -> None:
        if self.current_wave_index + 1 >= len(self.waves):
            self.finished = True
            return
        self.current_wave_index += 1
        wave = self.waves[self.current_wave_index]
        self.spawn_queue = []
        for entry in wave["entries"]:
            spawn_time = now_ms + entry["start_delay_ms"]
            for index in range(entry["count"]):
                self.spawn_queue.append(
                    {
                        "spawn_time_ms": spawn_time + index * entry["interval_ms"],
                        "enemy_type": entry["enemy"],
                    }
                )
        self.spawn_queue.sort(key=lambda item: item["spawn_time_ms"])
        self.wave_active = True
        post_event(START_WAVE, wave_number=wave["number"])
