# import os
# import re
# import textwrap

# import aiofiles
# import aiohttp
# import numpy as np

# from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont
# from youtubesearchpython import VideosSearch

# from config import YOUTUBE_IMG_URL
# from Dolbymusic import app


# def changeImageSize(maxWidth, maxHeight, image):
#     # Preserve aspect ratio and fit the image into the target canvas
#     # using a 'contain' strategy (scale-to-fit) so content is not cropped.
#     src_w, src_h = image.size
#     if src_w == 0 or src_h == 0:
#         return Image.new("RGBA", (maxWidth, maxHeight), (0, 0, 0, 0))

#     ratio = min(maxWidth / src_w, maxHeight / src_h)
#     new_w = max(1, int(src_w * ratio))
#     new_h = max(1, int(src_h * ratio))

#     resized = image.resize((new_w, new_h), Image.LANCZOS)

#     # Create target canvas. Use transparent background for RGBA-like images,
#     # otherwise use a dark background to match existing behavior.
#     if image.mode in ("RGBA", "LA"):
#         canvas = Image.new("RGBA", (maxWidth, maxHeight), (0, 0, 0, 0))
#     else:
#         canvas = Image.new("RGBA", (maxWidth, maxHeight), (0, 0, 0, 180))

#     # Center the resized image on the canvas
#     left = (maxWidth - new_w) // 2
#     top = (maxHeight - new_h) // 2
#     if resized.mode == "RGBA":
#         canvas.paste(resized, (left, top), mask=resized)
#     else:
#         canvas.paste(resized, (left, top))

#     return canvas


# def add_corners(im):
#     bigsize = (im.size[0] * 3, im.size[1] * 3)
#     mask = Image.new("L", bigsize, 0)
#     ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
#     mask = mask.resize(im.size, Image.LANCZOS)
#     mask = ImageChops.darker(mask, im.split()[-1])
#     im.putalpha(mask)


# async def gen_thumb(videoid, user_id):
#     # Ensure cache directory exists with safe path handling
#     try:
#         from Dolbymusic.utils.heroku_utils import get_safe_cache_path, safe_file_path
#         cache_dir = get_safe_cache_path()
#     except Exception:
#         cache_dir = "cache"

#     # Ensure cache directory exists
#     os.makedirs(cache_dir, exist_ok=True)

#     cache_file = os.path.join(cache_dir, f"{videoid}_{user_id}.png")
#     if os.path.isfile(cache_file):
#         return cache_file

#     url = f"https://www.youtube.com/watch?v={videoid}"
#     try:
#         results = VideosSearch(url, limit=1)
#         search_results = results.result()

#         for result in search_results["result"]:
#             try:
#                 title = result["title"]
#                 title = re.sub("\W+", " ", title)
#                 title = title.title()
#             except Exception:
#                 title = "Unsupported Title"
#             try:
#                 duration = result["duration"]
#             except Exception:
#                 duration = "Unknown"
#             try:
#                 thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#             except Exception:
#                 thumbnail = None

#         async with aiohttp.ClientSession() as session:
#             async with session.get(thumbnail) as resp:
#                 if resp.status == 200:
#                     thumb_path = os.path.join(cache_dir, f"thumb{videoid}.png")
#                     f = await aiofiles.open(thumb_path, mode="wb")
#                     await f.write(await resp.read())
#                     await f.close()

#         # Try to get user profile photo - comprehensive debugging approach
#         wxy = None
#         debug_info = []

#         debug_info.append(f"Starting profile photo fetch for user {user_id}")

#         # Method 1: Try get_profile_photos (for users)
#         try:
#             debug_info.append("Attempting get_profile_photos...")
#             user_photos = await app.get_profile_photos(user_id)
#             debug_info.append(f"get_profile_photos returned: {type(user_photos)}")

#             if user_photos and hasattr(user_photos, 'total_count'):
#                 debug_info.append(f"Profile photos total_count: {user_photos.total_count}")
#                 if user_photos.total_count > 0 and hasattr(user_photos, 'photos') and user_photos.photos:
#                     sizes = user_photos.photos[0]
#                     debug_info.append(f"Sizes type: {type(sizes)}; len: {len(sizes) if hasattr(sizes, '__len__') else 'n/a'}")

#                     largest_photo = None
#                     if isinstance(sizes, (list, tuple)) and len(sizes) > 0:
#                         try:
#                             largest_photo = max(
#                                 sizes,
#                                 key=lambda s: getattr(s, 'file_size', getattr(s, 'width', 0) or 0)
#                             )
#                         except Exception:
#                             largest_photo = sizes[-1]
#                     else:
#                         largest_photo = sizes

#                     debug_info.append(f"Selected largest photo type: {type(largest_photo)}")
#                     try:
#                         user_photo_path = os.path.join(cache_dir, f"user_{user_id}.jpg")
#                         photo_file = await app.download_media(
#                             largest_photo,
#                             file_name=user_photo_path,
#                         )
#                         if photo_file and os.path.exists(photo_file):
#                             wxy = photo_file
#                             debug_info.append(f"SUCCESS: Downloaded user photo to {photo_file}")
#                         else:
#                             debug_info.append("Download returned None or file doesn't exist")
#                             raise Exception("Download failed")
#                     except Exception as download_err:
#                         debug_info.append(f"Download error: {download_err}")
#                         raise
#                 else:
#                     raise Exception(f"No photos available (count: {getattr(user_photos, 'total_count', 'unknown')})")
#             else:
#                 raise Exception("Invalid user_photos response")
#         except Exception as e1:
#             debug_info.append(f"Method 1 failed: {e1}")

#             # Method 2: Try a different approach - get user info first
#             try:
#                 debug_info.append("Attempting to get user info...")
#                 user_info = await app.get_users(user_id)
#                 debug_info.append(f"User info: {type(user_info)}")

#                 if user_info and hasattr(user_info, 'photo') and user_info.photo:
#                     debug_info.append(f"User has photo: {type(user_info.photo)}")
#                     try:
#                         photo_file = await app.download_media(
#                             user_info.photo.big_file_id if hasattr(user_info.photo, 'big_file_id') else user_info.photo,
#                             file_name=os.path.join(cache_dir, f"user_{user_id}.jpg")
#                         )
#                         if photo_file and os.path.exists(photo_file):
#                             wxy = photo_file
#                             debug_info.append(f"SUCCESS: Downloaded user photo via user info to {photo_file}")
#                         else:
#                             raise Exception("User info photo download failed")
#                     except Exception as download_err:
#                         debug_info.append(f"User info photo download error: {download_err}")
#                         raise Exception("User info method failed")
#                 else:
#                     raise Exception("User has no photo in user info")
#             except Exception as e2:
#                 debug_info.append(f"Method 2 failed: {e2}")

#         # Fallback to bot's profile photo if all user methods failed
#         if not wxy:
#             try:
#                 debug_info.append("Attempting bot profile photo fallback...")
#                 bot_photos = await app.get_profile_photos(app.id)
#                 if bot_photos and hasattr(bot_photos, 'total_count') and bot_photos.total_count > 0:
#                     first_photo = bot_photos.photos[0]
#                     bot_photo_path = os.path.join(cache_dir, f"bot_{app.id}.jpg")
#                     photo_file = await app.download_media(
#                         first_photo,
#                         file_name=bot_photo_path,
#                     )
#                     if photo_file and os.path.exists(photo_file):
#                         wxy = photo_file
#                         debug_info.append(f"SUCCESS: Using bot profile photo {photo_file}")
#                     else:
#                         raise Exception("Bot photo download failed")
#                 else:
#                     raise Exception("Bot has no profile photos")
#             except Exception as e2:
#                 debug_info.append(f"Bot fallback failed: {e2}")

#                 # Final fallback: create default image
#                 default_img = Image.new("RGB", (640, 640), color="#2C3E50")
#                 draw = ImageDraw.Draw(default_img)

#                 draw.ellipse([(50, 50), (590, 590)], fill="#3498DB", outline="#2980B9", width=10)
#                 draw.ellipse([(220, 180), (420, 380)], fill="#ECF0F1")   # head
#                 draw.ellipse([(120, 350), (520, 750)], fill="#ECF0F1")   # body

#                 wxy = os.path.join(cache_dir, f"default_{user_id}.jpg")
#                 default_img.save(wxy)
#                 debug_info.append(f"Created default profile image at {wxy}")

#         # Print all debug info
#         for info in debug_info:
#             print(f"PFP DEBUG: {info}")

#         # Process the profile image to make it circular - robust approach
#         try:
#             if not wxy or not os.path.exists(wxy):
#                 raise Exception("Profile image file not found or invalid path")

#             file_size = os.path.getsize(wxy)
#             if file_size < 100:
#                 raise Exception(f"Profile image file too small ({file_size} bytes), likely corrupted")

#             xy = Image.open(wxy)
#             if not xy or xy.size[0] < 10 or xy.size[1] < 10:
#                 raise Exception("Profile image too small or corrupted")

#             if xy.mode in ("RGBA", "LA", "P"):
#                 xy = xy.convert("RGB")
#             elif xy.mode not in ("RGB", "RGBA"):
#                 xy = xy.convert("RGB")

#             xy = xy.resize((640, 640), Image.LANCZOS)

#             mask = Image.new('L', (640, 640), 0)
#             draw_mask = ImageDraw.Draw(mask)
#             draw_mask.ellipse([(0, 0), (640, 640)], fill=255)

#             circular_img = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
#             circular_img.paste(xy, (0, 0))
#             circular_img.putalpha(mask)

#             x = circular_img.resize((107, 107), Image.LANCZOS)
#             print(f"Successfully processed profile image to circular format")
#         except Exception as e:
#             print(f"Failed to process profile image: {e}")
#             x = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
#             draw = ImageDraw.Draw(x)
#             draw.ellipse([(2, 2), (105, 105)], fill="#3498DB", outline="#2980B9", width=2)
#             draw.ellipse([(35, 25), (72, 62)], fill="white")
#             draw.ellipse([(20, 65), (87, 132)], fill="white")
#             print("Created robust fallback circular profile image")

#         try:
#             youtube = Image.open(os.path.join(cache_dir, f"thumb{videoid}.png"))
#             dolby_asset = "Dolbymusic/assets/dolby_thumb.png"
#             if os.path.exists(dolby_asset):
#                 bg = Image.open(dolby_asset)
#             else:
#                 bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))
#         except Exception:
#             youtube = Image.new("RGB", (480, 360), color="gray")
#             bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))

#         try:
#             image1 = changeImageSize(1280, 720, youtube)
#             image2 = image1.convert("RGBA")
#             background = image2.filter(filter=ImageFilter.BoxBlur(30))
#             enhancer = ImageEnhance.Brightness(background)
#             background = enhancer.enhance(0.6)

#             image3 = changeImageSize(1280, 720, bg)
#             image5 = image3.convert("RGBA")
#             composite = Image.alpha_composite(background, image5)
#             composite.save(os.path.join(cache_dir, f"temp{videoid}.png"))
#         except Exception:
#             fallback = Image.new("RGBA", (1280, 720), color=(50, 50, 50, 255))
#             fallback.save(os.path.join(cache_dir, f"temp{videoid}.png"))

#         try:
#             Xcenter = youtube.width / 2
#             Ycenter = youtube.height / 2
#             x1 = Xcenter - 250
#             y1 = Ycenter - 250
#             x2 = Xcenter + 250
#             y2 = Ycenter + 250
#             logo = youtube.crop((x1, y1, x2, y2))
#             logo.thumbnail((520, 520), Image.LANCZOS)
#             logo.save(os.path.join(cache_dir, f"chop{videoid}.png"))
#             if not os.path.isfile(os.path.join(cache_dir, f"cropped{videoid}.png")):
#                 im = Image.open(os.path.join(cache_dir, f"chop{videoid}.png")).convert("RGBA")
#                 add_corners(im)
#                 im.save(os.path.join(cache_dir, f"cropped{videoid}.png"))
#         except Exception:
#             fallback_crop = Image.new("RGBA", (365, 365), color=(100, 100, 100, 255))
#             fallback_crop.save(os.path.join(cache_dir, f"cropped{videoid}.png"))

#         try:
#             crop_img = Image.open(os.path.join(cache_dir, f"cropped{videoid}.png"))
#             logo = crop_img.convert("RGBA")
#             logo.thumbnail((365, 365), Image.LANCZOS)
#             width = int((1280 - 365) / 2)
#             background = Image.open(os.path.join(cache_dir, f"temp{videoid}.png"))
#             background.paste(logo, (width + 2, 160), mask=logo)

#             if x.mode != "RGBA":
#                 x = x.convert("RGBA")
#             background.paste(x, (700, 440), mask=x)
#             background.paste(image3, (0, 0), mask=image3)
#             print(f"Successfully composed final thumbnail with profile image")
#         except Exception as e:
#             print(f"Failed to compose final thumbnail: {e}")
#             background = Image.new("RGBA", (1280, 720), color=(80, 80, 80, 255))

#         try:
#             draw = ImageDraw.Draw(background)
#             font_path = "Dolbymusic/assets/font2.ttf"
#             if os.path.exists(font_path):
#                 font = ImageFont.truetype(font_path, 45)
#                 arial = ImageFont.truetype(font_path, 30)
#             else:
#                 font = ImageFont.load_default()
#                 arial = ImageFont.load_default()
#         except Exception:
#             font = ImageFont.load_default()
#             arial = ImageFont.load_default()

#         try:
#             para = textwrap.wrap(title, width=32)
#         except Exception:
#             para = ["Unknown Title"]

#         try:
#             draw.text(
#                 (455, 25),
#                 "ADDED TO QUEUE",
#                 fill="white",
#                 stroke_width=5,
#                 stroke_fill="black",
#                 font=font,
#             )
#             if len(para) > 0 and para[0]:
#                 bbox = draw.textbbox((0, 0), f"{para[0]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 560),
#                     f"{para[0]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#             if len(para) > 1 and para[1]:
#                 bbox = draw.textbbox((0, 0), f"{para[1]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 610),
#                     f"{para[1]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#         except Exception:
#             pass

#         try:
#             bbox = draw.textbbox((0, 0), f"Duration: {duration} Mins", font=arial)
#             text_w = bbox[2] - bbox[0]
#             draw.text(
#                 ((1280 - text_w) / 2, 660),
#                 f"Duration: {duration} Mins",
#                 fill="white",
#                 font=arial,
#             )
#         except Exception:
#             pass

#         # ============================================================
#         #  CRITICAL FIX: save the final composite to the cache file
#         # ============================================================
#         try:
#             background.save(cache_file)
#             print(f"Thumbnail saved to {cache_file}")
#         except Exception as save_err:
#             print(f"Failed to save final thumbnail: {save_err}")
#             return YOUTUBE_IMG_URL

#         # Clean up temporary files
#         if 'thumb_path' in locals() and os.path.exists(thumb_path):
#             os.remove(thumb_path)
#         if 'wxy' in locals() and wxy and os.path.exists(wxy):
#             os.remove(wxy)

#         return cache_file
#     except Exception as e:
#         print(f"Thumbnail generation failed: {e}")
#         return YOUTUBE_IMG_URL


# async def gen_qthumb(videoid, user_id):
#     # Ensure cache directory exists with safe path handling
#     try:
#         from Dolbymusic.utils.heroku_utils import get_safe_cache_path
#         cache_dir = get_safe_cache_path()
#     except Exception:
#         cache_dir = "cache"
#     os.makedirs(cache_dir, exist_ok=True)

#     cache_file = os.path.join(cache_dir, f"que{videoid}_{user_id}.png")
#     if os.path.isfile(cache_file):
#         return cache_file

#     url = f"https://www.youtube.com/watch?v={videoid}"
#     try:
#         results = VideosSearch(url, limit=1)
#         for result in (await results.next())["result"]:
#             try:
#                 title = result["title"]
#                 title = re.sub("\W+", " ", title)
#                 title = title.title()
#             except Exception:
#                 title = "Unsupported Title"
#             try:
#                 duration = result["duration"]
#             except Exception:
#                 duration = "Unknown"
#             try:
#                 thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#             except Exception:
#                 thumbnail = None

#         async with aiohttp.ClientSession() as session:
#             async with session.get(thumbnail) as resp:
#                 if resp.status == 200:
#                     thumb_path = os.path.join(cache_dir, f"thumb{videoid}.png")
#                     f = await aiofiles.open(thumb_path, mode="wb")
#                     await f.write(await resp.read())
#                     await f.close()

#         # Try to get user profile photo - comprehensive debugging approach (same as gen_thumb)
#         wxy = None
#         debug_info = []

#         debug_info.append(f"Starting profile photo fetch for user {user_id} (queue)")

#         # Method 1: Try get_profile_photos
#         try:
#             debug_info.append("Attempting get_profile_photos for queue...")
#             user_photos = await app.get_profile_photos(user_id)
#             debug_info.append(f"get_profile_photos returned: {type(user_photos)}")

#             if user_photos and hasattr(user_photos, 'total_count'):
#                 debug_info.append(f"Profile photos total_count: {user_photos.total_count}")
#                 if user_photos.total_count > 0 and hasattr(user_photos, 'photos') and user_photos.photos:
#                     sizes = user_photos.photos[0]
#                     debug_info.append(f"Sizes type: {type(sizes)}; len: {len(sizes) if hasattr(sizes, '__len__') else 'n/a'}")

#                     largest_photo = None
#                     if isinstance(sizes, (list, tuple)) and len(sizes) > 0:
#                         try:
#                             largest_photo = max(
#                                 sizes,
#                                 key=lambda s: getattr(s, 'file_size', getattr(s, 'width', 0) or 0)
#                             )
#                         except Exception:
#                             largest_photo = sizes[-1]
#                     else:
#                         largest_photo = sizes

#                     debug_info.append(f"Selected largest photo type: {type(largest_photo)}")
#                     try:
#                         user_photo_path = os.path.join(cache_dir, f"user_{user_id}_queue.jpg")
#                         photo_file = await app.download_media(
#                             largest_photo,
#                             file_name=user_photo_path,
#                         )
#                         if photo_file and os.path.exists(photo_file):
#                             wxy = photo_file
#                             debug_info.append(f"SUCCESS: Downloaded user photo to {photo_file}")
#                         else:
#                             debug_info.append("Download returned None or file doesn't exist")
#                             raise Exception("Download failed")
#                     except Exception as download_err:
#                         debug_info.append(f"Download error: {download_err}")
#                         raise
#                 else:
#                     raise Exception(f"No photos available (count: {getattr(user_photos, 'total_count', 'unknown')})")
#             else:
#                 raise Exception("Invalid user_photos response")
#         except Exception as e1:
#             debug_info.append(f"Method 1 failed: {e1}")

#             # Method 2: get user info first
#             try:
#                 debug_info.append("Attempting to get user info for queue...")
#                 user_info = await app.get_users(user_id)
#                 debug_info.append(f"User info: {type(user_info)}")

#                 if user_info and hasattr(user_info, 'photo') and user_info.photo:
#                     debug_info.append(f"User has photo: {type(user_info.photo)}")
#                     try:
#                         photo_file = await app.download_media(
#                             user_info.photo.big_file_id if hasattr(user_info.photo, 'big_file_id') else user_info.photo,
#                             file_name=os.path.join(cache_dir, f"user_{user_id}_queue.jpg")
#                         )
#                         if photo_file and os.path.exists(photo_file):
#                             wxy = photo_file
#                             debug_info.append(f"SUCCESS: Downloaded user photo via user info to {photo_file}")
#                         else:
#                             raise Exception("User info photo download failed")
#                     except Exception as download_err:
#                         debug_info.append(f"User info photo download error: {download_err}")
#                         raise Exception("User info method failed")
#                 else:
#                     raise Exception("User has no photo in user info")
#             except Exception as e2:
#                 debug_info.append(f"Method 2 failed: {e2}")

#         # Fallback to bot's profile photo
#         if not wxy:
#             try:
#                 debug_info.append("Attempting bot profile photo fallback for queue...")
#                 bot_photos = await app.get_profile_photos(app.id)
#                 if bot_photos and hasattr(bot_photos, 'total_count') and bot_photos.total_count > 0:
#                     first_photo = bot_photos.photos[0]
#                     bot_photo_path = os.path.join(cache_dir, f"bot_{app.id}_queue.jpg")
#                     photo_file = await app.download_media(
#                         first_photo,
#                         file_name=bot_photo_path,
#                     )
#                     if photo_file and os.path.exists(photo_file):
#                         wxy = photo_file
#                         debug_info.append(f"SUCCESS: Using bot profile photo {photo_file}")
#                     else:
#                         raise Exception("Bot photo download failed")
#                 else:
#                     raise Exception("Bot has no profile photos")
#             except Exception as e2:
#                 debug_info.append(f"Bot fallback failed: {e2}")

#                 # Final fallback: create default image
#                 default_img = Image.new("RGB", (640, 640), color="#2C3E50")
#                 draw = ImageDraw.Draw(default_img)
#                 draw.ellipse([(50, 50), (590, 590)], fill="#3498DB", outline="#2980B9", width=10)
#                 draw.ellipse([(220, 180), (420, 380)], fill="#ECF0F1")
#                 draw.ellipse([(120, 350), (520, 750)], fill="#ECF0F1")
#                 wxy = os.path.join(cache_dir, f"default_{user_id}_queue.jpg")
#                 default_img.save(wxy)
#                 debug_info.append(f"Created default profile image at {wxy}")

#         for info in debug_info:
#             print(f"PFP DEBUG QUEUE: {info}")

#         # Process the profile image to make it circular
#         try:
#             if not wxy or not os.path.exists(wxy):
#                 raise Exception("Profile image file not found or invalid path")

#             file_size = os.path.getsize(wxy)
#             if file_size < 100:
#                 raise Exception(f"Profile image file too small ({file_size} bytes), likely corrupted")

#             xy = Image.open(wxy)
#             if not xy or xy.size[0] < 10 or xy.size[1] < 10:
#                 raise Exception("Profile image too small or corrupted")

#             if xy.mode in ("RGBA", "LA", "P"):
#                 xy = xy.convert("RGB")
#             elif xy.mode not in ("RGB", "RGBA"):
#                 xy = xy.convert("RGB")

#             xy = xy.resize((640, 640), Image.LANCZOS)

#             mask = Image.new('L', (640, 640), 0)
#             draw_mask = ImageDraw.Draw(mask)
#             draw_mask.ellipse([(0, 0), (640, 640)], fill=255)

#             circular_img = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
#             circular_img.paste(xy, (0, 0))
#             circular_img.putalpha(mask)

#             x = circular_img.resize((107, 107), Image.LANCZOS)
#             print(f"Successfully processed profile image to circular format for queue")
#         except Exception as e:
#             print(f"Failed to process profile image for queue: {e}")
#             x = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
#             draw = ImageDraw.Draw(x)
#             draw.ellipse([(2, 2), (105, 105)], fill="#3498DB", outline="#2980B9", width=2)
#             draw.ellipse([(35, 25), (72, 62)], fill="white")
#             draw.ellipse([(20, 65), (87, 132)], fill="white")
#             print("Created robust fallback circular profile image for queue")

#         try:
#             youtube = Image.open(os.path.join(cache_dir, f"thumb{videoid}.png"))
#             bg_path = "Dolbymusic/assets/morningx.png"
#             dolby_asset = "Dolbymusic/assets/dolby_thumb.png"
#             if os.path.exists(dolby_asset):
#                 bg = Image.open(dolby_asset)
#             elif os.path.exists(bg_path):
#                 bg = Image.open(bg_path)
#             else:
#                 bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))
#         except Exception:
#             youtube = Image.new("RGB", (480, 360), color="gray")
#             bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))

#         try:
#             image1 = changeImageSize(1280, 720, youtube)
#             image2 = image1.convert("RGBA")
#             background = image2.filter(filter=ImageFilter.BoxBlur(30))
#             enhancer = ImageEnhance.Brightness(background)
#             background = enhancer.enhance(0.6)

#             image3 = changeImageSize(1280, 720, bg)
#             image5 = image3.convert("RGBA")
#             Image.alpha_composite(background, image5).save(os.path.join(cache_dir, f"temp{videoid}.png"))
#         except Exception:
#             fallback = Image.new("RGBA", (1280, 720), color=(50, 50, 50, 255))
#             fallback.save(os.path.join(cache_dir, f"temp{videoid}.png"))

#         try:
#             Xcenter = youtube.width / 2
#             Ycenter = youtube.height / 2
#             x1 = Xcenter - 250
#             y1 = Ycenter - 250
#             x2 = Xcenter + 250
#             y2 = Ycenter + 250
#             logo = youtube.crop((x1, y1, x2, y2))
#             logo.thumbnail((520, 520), Image.LANCZOS)
#             logo.save(os.path.join(cache_dir, f"chop{videoid}.png"))
#             if not os.path.isfile(os.path.join(cache_dir, f"cropped{videoid}.png")):
#                 im = Image.open(os.path.join(cache_dir, f"chop{videoid}.png")).convert("RGBA")
#                 add_corners(im)
#                 im.save(os.path.join(cache_dir, f"cropped{videoid}.png"))
#         except Exception:
#             fallback_crop = Image.new("RGBA", (365, 365), color=(100, 100, 100, 255))
#             fallback_crop.save(os.path.join(cache_dir, f"cropped{videoid}.png"))

#         try:
#             crop_img = Image.open(os.path.join(cache_dir, f"cropped{videoid}.png"))
#             logo = crop_img.convert("RGBA")
#             logo.thumbnail((365, 365), Image.LANCZOS)
#             width = int((1280 - 365) / 2)
#             background = Image.open(os.path.join(cache_dir, f"temp{videoid}.png"))
#             background.paste(logo, (width + 2, 160), mask=logo)

#             if x.mode != "RGBA":
#                 x = x.convert("RGBA")
#             background.paste(x, (700, 440), mask=x)
#             background.paste(image3, (0, 0), mask=image3)
#             print(f"Successfully composed final queue thumbnail with profile image")
#         except Exception as e:
#             print(f"Failed to compose final queue thumbnail: {e}")
#             background = Image.new("RGBA", (1280, 720), color=(80, 80, 80, 255))

#         try:
#             draw = ImageDraw.Draw(background)
#             font_path = "Dolbymusic/assets/font2.ttf"
#             if os.path.exists(font_path):
#                 font = ImageFont.truetype(font_path, 45)
#                 arial = ImageFont.truetype(font_path, 30)
#             else:
#                 font = ImageFont.load_default()
#                 arial = ImageFont.load_default()
#         except Exception:
#             font = ImageFont.load_default()
#             arial = ImageFont.load_default()

#         try:
#             para = textwrap.wrap(title, width=32)
#         except Exception:
#             para = ["Unknown Title"]

#         try:
#             draw.text(
#                 (455, 25),
#                 "ADDED TO QUEUE",
#                 fill="white",
#                 stroke_width=5,
#                 stroke_fill="black",
#                 font=font,
#             )
#             if len(para) > 0 and para[0]:
#                 bbox = draw.textbbox((0, 0), f"{para[0]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 560),
#                     f"{para[0]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#             if len(para) > 1 and para[1]:
#                 bbox = draw.textbbox((0, 0), f"{para[1]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 610),
#                     f"{para[1]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#         except Exception:
#             pass

#         try:
#             bbox = draw.textbbox((0, 0), f"Duration: {duration} Mins", font=arial)
#             text_w = bbox[2] - bbox[0]
#             draw.text(
#                 ((1280 - text_w) / 2, 660),
#                 f"Duration: {duration} Mins",
#                 fill="white",
#                 font=arial,
#             )
#         except Exception:
#             pass

#         # ============================================================
#         #  CRITICAL FIX: save the final composite to the cache file
#         # ============================================================
#         try:
#             background.save(cache_file)
#             print(f"Queue thumbnail saved to {cache_file}")
#         except Exception as save_err:
#             print(f"Failed to save final queue thumbnail: {save_err}")
#             return YOUTUBE_IMG_URL

#         # Clean up temporary files
#         if 'thumb_path' in locals() and os.path.exists(thumb_path):
#             os.remove(thumb_path)
#         if 'wxy' in locals() and wxy and os.path.exists(wxy):
#             os.remove(wxy)

#         return cache_file
#     except Exception as e:
#         print(f"Queue thumbnail generation failed: {e}")
#         return YOUTUBE_IMG_URL


# async def get_thumb(videoid, user_id):
#     """
#     Main thumbnail function that returns either cached or newly generated thumbnail
#     This is the function that other modules import and use
#     """
#     return await gen_thumb(videoid, user_id)


import random
import os
import re
import aiofiles
import aiohttp
import traceback
import logging
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

# ---------- Helper functions (unchanged) ----------
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i
    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1, text2]

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generate_gradient(width, height, start_color, end_color):
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(60 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def crop_center_circle(img, output_size, border, border_color, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    img = img.resize((output_size - 2*border, output_size - 2*border))
    final_img = Image.new("RGBA", (output_size, output_size), border_color)
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    final_img.paste(img, (border, border), mask_main)
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    return result

def draw_text_with_shadow(background, draw, position, text, font, fill, shadow_offset=(3, 3), shadow_blur=5):
    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text(position, text, font=font, fill="black")
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    background.paste(shadow, shadow_offset, shadow)
    draw.text(position, text, font=font, fill=fill)

# ---------- Fallback default thumbnail ----------
def create_default_thumbnail():
    img = Image.new('RGBA', (1280, 720), (30, 30, 30, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Dolbymusic/assets/font2.ttf", 50)
    except:
        font = ImageFont.load_default()
    d.text((400, 300), "No Thumbnail", fill="white", font=font)
    return img

# ---------- Main thumbnail generator ----------
async def gen_thumb(videoid: str):
    try:
        # Ensure cache directory exists
        os.makedirs("cache", exist_ok=True)

        cached_path = f"cache/{videoid}_v4.png"
        if os.path.isfile(cached_path):
            return cached_path

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        search_data = await results.next()
        if not search_data or "result" not in search_data or not search_data["result"]:
            raise Exception("No search results")

        result = search_data["result"][0]
        title = result.get("title")
        title = re.sub("\W+", " ", title).title() if title else "Unsupported Title"
        duration = result.get("duration") or "Live"
        thumbnail = result.get("thumbnails")
        if thumbnail:
            thumbnail = thumbnail[0]["url"].split("?")[0]
        else:
            thumbnail = None
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        if not thumbnail:
            raise Exception("No thumbnail URL")

        # Download thumbnail image
        filepath = f"cache/thumb{videoid}.png"
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status != 200:
                    raise Exception(f"Thumbnail HTTP {resp.status}")
                # Read the body only once and write directly
                f = await aiofiles.open(filepath, mode="wb")
                await f.write(await resp.read())
                await f.close()

        # Open downloaded thumbnail
        youtube = Image.open(filepath)
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(20))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        start_gradient_color = random_color()
        end_gradient_color = random_color()
        gradient_image = generate_gradient(1280, 720, start_gradient_color, end_gradient_color)
        background = Image.blend(background, gradient_image, alpha=0.2)

        draw = ImageDraw.Draw(background)
        # Use fonts stored in Dolbymusic/assets/
        arial = ImageFont.truetype("Dolbymusic/assets/font2.ttf", 30)
        font = ImageFont.truetype("Dolbymusic/assets/font.ttf", 30)
        title_font = ImageFont.truetype("Dolbymusic/assets/font3.ttf", 45)

        circle_thumbnail = crop_center_circle(youtube, 400, 20, start_gradient_color)
        circle_thumbnail = circle_thumbnail.resize((400, 400))
        background.paste(circle_thumbnail, (120, 160), circle_thumbnail)

        text_x = 565
        title1 = truncate(title)
        draw_text_with_shadow(background, draw, (text_x, 180), title1[0], title_font, (255, 255, 255))
        draw_text_with_shadow(background, draw, (text_x, 230), title1[1], title_font, (255, 255, 255))
        draw_text_with_shadow(background, draw, (text_x, 320), f"{channel}  |  {views[:23]}", arial, (255, 255, 255))

        line_length = 580
        line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        if duration != "Live":
            pct = random.uniform(0.15, 0.85)
            color_len = int(line_length * pct)
            draw.line([(text_x, 380), (text_x + color_len, 380)], fill=line_color, width=9)
            draw.line([(text_x + color_len, 380), (text_x + line_length, 380)], fill="white", width=8)
            draw.ellipse([text_x + color_len - 10, 370, text_x + color_len + 10, 390], fill=line_color)
        else:
            line_color = (255, 0, 0)
            draw.line([(text_x, 380), (text_x + line_length, 380)], fill=line_color, width=9)
            draw.ellipse([text_x + line_length - 10, 370, text_x + line_length + 10, 390], fill=line_color)

        draw_text_with_shadow(background, draw, (text_x, 400), "00:00", arial, (255, 255, 255))
        draw_text_with_shadow(background, draw, (1080, 400), duration, arial, (255, 255, 255))

        play_icons = Image.open("Dolbymusic/assets/play_icons.png")
        play_icons = play_icons.resize((580, 62))
        background.paste(play_icons, (text_x, 450), play_icons)

        # Delete temp download
        os.remove(filepath)

        background.save(cached_path)
        return cached_path

    except Exception as e:
        logging.error(f"Thumbnail generation failed for {videoid}: {e}")
        traceback.print_exc()
        # Return a default thumbnail so the bot never gets None
        default_path = f"cache/default_thumb.png"
        if not os.path.isfile(default_path):
            img = create_default_thumbnail()
            img.save(default_path)
        return default_path

# ---------- Compatibility wrapper ----------
async def get_thumb(videoid, user_id=None):
    """Wrapper so other modules can call get_thumb(videoid, user_id)"""
    return await gen_thumb(videoid)
