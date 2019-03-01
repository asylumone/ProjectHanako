import core.core as core
from core.config import tg_token

if __name__ == '__main__':
    Hanako = core.Core(tg_token)
    Hanako.start()

# TODO: Add logging levels
# TODO: Calendar, file downloader, calculator
