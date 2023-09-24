# GuessTheEpisode

GuessTheEpisode is a game where you have to guess the episode of a TV show based on a random frame of it.

# Installation

Simply clone the repo and run `poetry install`.

# Usage

## Adding the first show

1. Download a TV Show.
2. Configure the consts in `scripts/add_show.py` and run it.
3. Configure the same DB path in `gte/db.py`.
4. Host the frames folder statically either using `scripts/host_images.py` or any other method.
5. Configure the address of the hosting server in `gte/images.py`.

## Adding a new show

Follow steps 1 and 2 from the previous section.

## Running the game

Run `gte/main.py` 

# Planned features

Not in any specific order:

- [ ] Host a public version of the game on fly.io.
- [ ] Add a better config system.
- [ ] Add a script that fetches frames.
- [ ] Add a script that fetches show information.
- [ ] Make a Rest API that adds shows for you instead of requiring you to run a script.
- [ ] Add an AI helper that lets you describe the episode plot and will give you the episode name.