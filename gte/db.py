import sqlite3
from io import BytesIO
from typing import List

from PIL import Image

from gte.models import ShowName, Frame, Episode

DB = sqlite3.connect(r"../frames-prod.db", check_same_thread=False)


def get_all_shows() -> List[ShowName]:
    return [row[0] for row in DB.execute("SELECT DISTINCT show_name FROM frames")]


def get_frames(shows: List[ShowName]) -> List[Frame]:
    return [
        Frame(frame_id=row[0], episode=Episode(name=row[1], show_name=row[2]))
        for row in DB.execute(
            "SELECT id, episode_name, show_name FROM frames WHERE show_name IN ({}) ORDER BY show_name, id".format(
                ", ".join(["?"] * len(shows))
            ),
            shows,
        ).fetchall()
    ]


def get_frame_image(frame: Frame) -> Image:
    return Image.open(BytesIO(DB.execute("SELECT image FROM frames WHERE id = ?", (frame.frame_id,)).fetchone()[0]))


if __name__ == '__main__':
    all_shows = get_all_shows()
    print(all_shows)
    print(len(get_frames(all_shows[:1])))
