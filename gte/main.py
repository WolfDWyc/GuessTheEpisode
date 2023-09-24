from pywebio import start_server, config, pin
from pywebio.input import input_group, select, actions
from pywebio.output import use_scope, put_image, put_text, put_markdown

from gte.db import get_all_shows, get_frames
from gte.gte_game import GTEGame
from gte.images import get_image_url


def create_game() -> GTEGame:
    all_shows = get_all_shows()
    form_result = input_group(
        "New Game",
        [
            select(
                "Select shows",
                options=[
                    {
                        "label": show,
                        "value": show,
                    }
                    for show in all_shows
                ],
                multiple=True,
                required=True,
                name="select_shows"
            ),
            actions(
                buttons=[
                    {"label": "Start", "value": "Start"}
                ], name="start"
            )
        ]
    )
    return GTEGame(get_frames(form_result["select_shows"]))


@config(
    title="GuessTheEpisode",
    description="Guess the episode from a random frame",
    css_style=".pywebio {min-height:calc(100vh - 50px);}"
)
def main():
    game = create_game()
    while True:
        with use_scope(name="image-scope", clear=True):
            frame = game.get_current_frame()
            put_markdown(f"<u>Round {game.get_round()}</u>\n**Current show:** {frame.episode.show_name}")
            put_image(get_image_url(frame), width="100%", height="100%")

            options = {
                f"{index + 1:03} {episode.name}": episode
                for index, episode in enumerate(game.get_show_episodes(frame.episode.show_name))
            }
            pin.put_input(
                "Episode",
                datalist=list(options.keys()),
            )

            with use_scope("form-scope", clear=True):
                pin.put_actions(
                    "Actions",
                    buttons=[
                        {"label": "Guess", "value": "Guess"},
                        {"label": "Skip (-50 Points)", "value": "Skip", "color": "secondary"}
                    ])

                change = pin.pin_wait_change("Actions")
                if change["value"] == "Guess":
                    guess_text = pin.pin["Episode"]
                    if guess_text not in options:
                        raise ValueError("Something went wrong")
                    guess = options[guess_text]
                elif change["value"] == "Skip":
                    guess = None
                else:
                    raise ValueError("Something went wrong")

            guess_result = game.guess(guess)
            with use_scope("form-scope", clear=True):
                if guess_result.guessed_episode == guess_result.actual_episode:
                    put_text(f"Good job! The episode was {guess_result.actual_episode.name}")
                else:
                    put_text(f"The episode was {guess_result.actual_episode.name}")
                put_text(f"Score: {guess_result.new_score} ({guess_result.new_score - guess_result.old_score:+})")

                pin.put_actions("Continue", buttons=[{"label": "Continue", "value": "Continue"}])
                pin.pin_wait_change("Continue")


if __name__ == '__main__':
    start_server(main, port=452, remote_access=True)


