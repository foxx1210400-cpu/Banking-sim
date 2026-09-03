from Startup import game_loop
from core.player_class import Player
from core.logger import logger


if __name__ == "__main__":
    try:
        game_loop(Player())
    except EOFError:
        logger.info("CLI game ended by input stream")
    except Exception:
        logger.exception("Unexpected CLI game failure")
        raise

