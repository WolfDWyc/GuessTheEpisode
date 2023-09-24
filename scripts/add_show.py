import os
import random
import sqlite3
from itertools import chain
from typing import Iterable

import cv2
import decord
from PIL import Image
from tqdm import tqdm

BACKEND = "decord"  # "opencv" | "decord"

DB = sqlite3.connect(r"..\frames-prod.db")
DB.cursor().execute("CREATE TABLE IF NOT EXISTS frames(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "show_name TEXT, episode_name TEXT)")
DB.commit()
FRAMES_PATH = r"..\frames-prod"
os.makedirs(FRAMES_PATH, exist_ok=True)

SHOW_NAME = "Gravity Falls"
SHOW_PATHS = [r"C:\Users\Yoav\Downloads\Gravity Falls S01-S02 (2012-)\Gravity Falls S01 (360p re-blurip)",
              r"C:\Users\Yoav\Downloads\Gravity Falls S01-S02 (2012-)\Gravity Falls S02 (360p re-blurip)"]
FRAME_COUNT = 50  # Number of frames to take from each episode
START_FRAME_OFFSET = 24 * 150  # Used for skipping intros
END_FRAME_OFFSET = 24 * 45  # Used for skipping credits

# You can get this data from IMDb or any other way you want
EPISODE_NAMES = ["Tourist Trapped", "The Legend of the Gobblewonker", "Headhunters", "The Hand That Rocks the Mabel",
                 "The Inconveniencing", "Dipper vs. Manliness", "Double Dipper", "Irrational Treasure",
                 "The Time Traveler's Pig", "Fight Fighters", "Little Dipper", "Summerween", "Boss Mabel",
                 "Bottomless Pit!", "The Deep End", "Carpet Diem", "Boyz Crazy", "Land Before Swine", "Dreamscaperers",
                 "Gideon Rises", "Scary-oke", "Into the Bunker", "The Golf War", "Sock Opera", "Soos and the Real Girl",
                 "Little Gift Shop of Horrors", "Society of the Blind Eye", "Blendin's Game", "The Love God",
                 "Northwest Mansion Mystery", "Not What He Seems", "A Tale of Two Stans",
                 "Dungeons, Dungeons, and More Dungeons", "The Stanchurian Candidate", "The Last Mabelcorn",
                 "Roadside Attraction", "Dipper and Mabel vs. the Future", "Weirdmageddon: Part 1",
                 "Weirdmageddon 2: Escape from Reality", "Weirdmageddon 3: Take Back the Falls",
                 "Weirdmageddon 4: Somewhere in the Woods"]


def get_random_frames_decord(video_path: str) -> Iterable[Image.Image]:
    video = decord.VideoReader(video_path)
    frame_count = len(video)
    frame_indexes = []
    for _ in range(FRAME_COUNT):
        frame_indexes.append(random.randint(START_FRAME_OFFSET, frame_count - END_FRAME_OFFSET))
    frames = video.get_batch(frame_indexes).asnumpy()
    for frame in tqdm(frames):
        yield Image.fromarray(frame)


def get_random_frames_cv2(video_path: str) -> Iterable[Image.Image]:
    vidcap = cv2.VideoCapture(video_path)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    for _ in tqdm(range(FRAME_COUNT)):
        frame_number = random.randint(START_FRAME_OFFSET, frame_count - END_FRAME_OFFSET)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        _, image = vidcap.read()
        yield Image.fromarray(image)


def get_random_frames(video_path: str) -> Iterable[Image.Image]:
    if BACKEND == "decord":
        return get_random_frames_decord(video_path)
    elif BACKEND == "opencv":
        return get_random_frames_cv2(video_path)
    else:
        raise ValueError(f"Unknown backend {BACKEND}")


def add_frame(frame: Image.Image, episode_index):
    episode_name = EPISODE_NAMES[episode_index]
    cursor = DB.cursor()
    cursor.execute("INSERT INTO frames VALUES (NULL, ?, ?)", (SHOW_NAME, episode_name))
    DB.commit()
    frame.save(os.path.join(FRAMES_PATH, f"frame_{cursor.lastrowid}.jpeg"), format="JPEG")


if __name__ == '__main__':
    if DB.cursor().execute("SELECT * FROM frames WHERE show_name = ?", (SHOW_NAME,)).fetchone():
        override = input(f"Show {SHOW_NAME} already exists in DB, delete? (y/n)")
        if override.lower() != "y":
            print("Aborting")
            exit()
        else:
            frame_files = [os.path.join(FRAMES_PATH, f"frame_{row[0]}.jpeg")
                           for row in DB.cursor().execute("SELECT id FROM frames WHERE show_name = ?", (SHOW_NAME,))]
            for frame_file in frame_files:
                os.remove(frame_file)
            DB.cursor().execute("DELETE FROM frames WHERE show_name = ?", (SHOW_NAME,))
            DB.commit()

    video_list = list(chain(*[[os.path.join(path, name) for name in os.listdir(path)] for path in SHOW_PATHS]))
    if len(video_list) > len(EPISODE_NAMES):
        raise ValueError(f"Found {len(video_list)} videos for {len(EPISODE_NAMES)} episodes")
    confirm = input(f"""
Previewing episode order, {len(video_list)} episodes -
{', '.join(video_list[:3])}...
Confirm order? (y/n)
    """)
    if confirm.lower() != "y":
        print("Aborting")
        exit()

    for episode_index, video_path in enumerate(tqdm(video_list)):
        for frame in get_random_frames(video_path):
            add_frame(frame, episode_index)
