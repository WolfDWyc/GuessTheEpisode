import random
from collections import defaultdict

from gte.models import Frame, Episode, ShowName, GuessResult

GUESS_WEIGHT = 100
ZERO_DISTANCE = 3


class GTEGame:
    def __init__(self, frames: list[Frame]):
        self._shows_episodes: dict[ShowName, list[Episode]] = defaultdict(list)
        for frame in frames:
            if frame.episode not in self._shows_episodes[frame.episode.show_name]:
                self._shows_episodes[frame.episode.show_name].append(frame.episode)
        self._frames = frames
        self._score = 0
        self._round = 1
        self._current_frame = None
        self._choose_frame()

    def _choose_frame(self):
        if self._current_frame is None:
            self._current_frame = random.choice(self._frames)
            return

        new_frame = self._current_frame
        while new_frame == self._current_frame or new_frame.episode == self._current_frame.episode:
            new_frame = random.choice(self._frames)
        self._current_frame = new_frame

    def _calculate_guess_score(self, episode: Episode | None) -> int:
        frame_episode = self._current_frame.episode
        if episode is None:
            return -1 * GUESS_WEIGHT // 2
        if episode.show_name != frame_episode.show_name:
            return -1 * GUESS_WEIGHT

        show_episodes = self._shows_episodes[frame_episode.show_name]
        episode_distance = min(abs(show_episodes.index(frame_episode) - show_episodes.index(episode)), ZERO_DISTANCE * 2)

        return int(GUESS_WEIGHT/ZERO_DISTANCE * (ZERO_DISTANCE * 2 - episode_distance) - GUESS_WEIGHT)

    def get_all_shows(self) -> list[ShowName]:
        return list(self._shows_episodes.keys())

    def get_show_episodes(self, show_name: ShowName) -> list[Episode]:
        return self._shows_episodes[show_name]

    def get_current_frame(self) -> Frame:
        return self._current_frame

    def guess(self, episode: Episode | None) -> GuessResult:
        previous_score = self._score
        previous_episode = self._current_frame.episode
        self._score += self._calculate_guess_score(episode)
        self._round += 1
        self._choose_frame()
        return GuessResult(
            round=self._round,
            old_score=previous_score,
            new_score=self._score,
            guessed_episode=episode,
            actual_episode=previous_episode,
        )

    def get_score(self) -> int:
        return self._score

    def get_round(self) -> int:
        return self._round

