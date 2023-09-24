from pydantic import BaseModel

ShowName = str


class Episode(BaseModel):
    name: str
    show_name: ShowName

    def __str__(self):
        return f"{self.show_name}  - {self.name}"


class Frame(BaseModel):
    frame_id: int
    episode: Episode


class GuessResult(BaseModel):
    round: int
    old_score: int
    new_score: int
    actual_episode: Episode
    guessed_episode: Episode | None
