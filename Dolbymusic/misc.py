import socket
import time

import heroku3
from pyrogram import filters

import config
from Dolbymusic.core.mongo import mongodb

from .logging import LOGGER

SUDOERS = filters.user()

HAPP = None
_boot_ = time.time()


def is_heroku():
    return "heroku" in socket.getfqdn()


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(config.HEROKU_API_KEY),
    "https",
    str(config.HEROKU_APP_NAME),
    "HEAD",
    "master",
]


def dbb():
    global db
    db = {}
    LOGGER(__name__).info(f"Local Database Initialized.")


async def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
    LOGGER(__name__).info(f"Sudoers Loaded.")


def heroku():
    global HAPP
    if is_heroku:
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = Heroku.app(config.HEROKU_APP_NAME)
                LOGGER(__name__).info(f"Heroku App Configured")
            except BaseException:
                LOGGER(__name__).warning(
                    f"Please make sure your Heroku API Key and Your App name are configured correctly in the heroku."
                )


# ============ YOUTUBE CACHE FUNCTIONS ============
# Cache YouTube audio files in Telegram channel to avoid repeated downloads

async def get_cached_audio(video_id: str):
    """Get cached audio message_id from MongoDB"""
    try:
        ytcache = mongodb.ytcache
        cached = await ytcache.find_one({"video_id": video_id})
        return cached.get("message_id") if cached else None
    except Exception as e:
        LOGGER(__name__).error(f"Cache get error: {e}")
        return None


async def save_cached_audio(video_id: str, message_id: int):
    """Save audio message_id to MongoDB cache"""
    try:
        ytcache = mongodb.ytcache
        await ytcache.update_one(
            {"video_id": video_id},
            {"$set": {"message_id": message_id, "cached_at": time.time()}},
            upsert=True
        )
        LOGGER(__name__).info(f"Cached audio for {video_id}: msg {message_id}")
    except Exception as e:
        LOGGER(__name__).error(f"Cache save error: {e}")
