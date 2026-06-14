import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID","34708578"))
API_HASH = getenv("API_HASH","d532e5b947d462f858077d614f31f22b")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN","7507436870:AAG7EKuiRZ35blNJXzC_3odtaf_ZjDF_wYA")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI","mongodb+srv://Jani_Sanatani_Power:RamRP@jani.elxnxrd.mongodb.net/?appName=Jani")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 1000))

# Chat id of a group for logging bot's activities
LOG_ID = int(getenv("LOGGER_ID"))
LOGGER_ID = int(getenv("LOGGER_ID","-1002654645615"))

# Get this value on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID","5099526956"))

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Jani-Ka-Repo/Pravet",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/+K3ZEGFDX56hhZTU1")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+jDGf1SvsfDpiZWI9")

API_URL = getenv("API_URL", "https://teaminflex.xyz") #youtube song url
API_KEY = getenv("API_KEY", "INFLEX12532228D") # youtube song api ke

# Set it in True if you want to leave your assistant after a certain amount of time. [Set time via AUTO_LEAVE_ASSISTANT_TIME]
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", False)

# Time after which you're assistant account will leave chats automatically.
AUTO_LEAVE_ASSISTANT_TIME = int(
    getenv("ASSISTANT_LEAVE_TIME", "9000")
)  # Remember to give value in Seconds

# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")

# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", 900))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", 900))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes

# Get your pyrogram v2 session from @KavyaStringGeneratorBot on Telegram
STRING1 = getenv("STRING_SESSION","BQIRnGIAiZQX5VB614d9OcODDHRecZcmr3s0JoMCfKXAfZe6yWzFPvgrZFIcwFaPHGbfY7uuGpBO2pUNnPfROhxoJMNFLwobUV2MKqxH2MvDGpTDApVoRDvraVBRX9SL_kNx9jx5S0uETddqqrBdZ3sy3y00UUSeYTKHmYmdN98B8NXF1AHts261M3BkbYNTRpaA7HvKm6Yc7Akgon58HDBOi0NmDbsbq5XhNj7OHt-XDIn4jX9BEDcqQ2_goej77TcKdtdlDn3XjYqebhdyZULrCs6ElYS0ZsK73EiwGOYIh4xC7N0Ez2X4PD-9JUbpoBvV6tS3rCZDKxDBDhU7759jbhoPWAAAAAG4kG6oAA")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")
STRING6 = getenv("STRING_SESSION6")
STRING7 = getenv("STRING_SESSION7")


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Thumbnail URLs

START_IMG_URL = getenv(
    "START_IMG_URL", "https://ibb.co/4RkjhyZ5"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://ibb.co/9k9F4wXz"
)
PLAYLIST_IMG_URL = "https://ibb.co/N2Z5dkLR"
STATS_IMG_URL = "https://ibb.co/N2Z5dkLR"
TELEGRAM_AUDIO_URL = "https://ibb.co/N2Z5dkLR"
TELEGRAM_VIDEO_URL = "https://ibb.co/N2Z5dkLR"
STREAM_IMG_URL = "https://ibb.co/N2Z5dkLR"
SOUNCLOUD_IMG_URL = "https://ibb.co/4RkjhyZ5"
YOUTUBE_IMG_URL = "https://ibb.co/N2Z5dkLR"
SPOTIFY_ARTIST_IMG_URL = "https://ibb.co/N2Z5dkLR"
SPOTIFY_ALBUM_IMG_URL = "https://ibb.co/N2Z5dkLR"
SPOTIFY_PLAYLIST_IMG_URL = "https://ibb.co/N2Z5dkLR"
CACHE_CHANNEL_ID = -1002846625394

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
