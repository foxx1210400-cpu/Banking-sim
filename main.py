from Startup import game_loop
from player_class import Player


if __name__ == "__main__":
    try:
        game_loop(Player())
    except EOFError:
        pass

