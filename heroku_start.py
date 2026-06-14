#!/usr/bin/env python3
"""
Startup script for DolbyMusic on Heroku
This script ensures all necessary directories and permissions are set up
"""

import os
import sys

# FIX: Silence the GitPython executable missing warning/error
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

import tempfile

# Force unbuffered output immediately
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

print("="*50, flush=True)
print("🎵 DOLBYMUSIC BOT STARTING ON HEROKU", flush=True)
print("="*50, flush=True)
print(f"Python: {sys.version}", flush=True)
print(f"Platform: Heroku", flush=True)
print("="*50, flush=True)

def setup_heroku_environment():
    """Set up environment for Heroku deployment"""
    
    print("🚀 Setting up DolbyMusic for Heroku...", flush=True)
    
    # Create necessary directories with absolute paths
    directories = [
        "downloads",
        "logs", 
        "cache",
        "cache/thumbnails",  # Sub-directory for thumbnails
        "temp"  # Additional temp directory
    ]
    
    for directory in directories:
        try:
            # Use absolute path to ensure proper creation
            abs_path = os.path.abspath(directory)
            os.makedirs(abs_path, exist_ok=True)
            
            # Verify directory was created and is writable
            test_file = os.path.join(abs_path, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            
            print(f"✅ Created/verified directory: {directory} -> {abs_path}", flush=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not create directory {directory}: {e}", flush=True)
            # For critical directories, try alternative approaches
            if directory in ["downloads", "cache"]:
                try:
                    # Try using temp directory as fallback
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    fallback_dir = os.path.join(temp_dir, f"dolbymusic_{directory}")
                    os.makedirs(fallback_dir, exist_ok=True)
                    
                    # Create symlink or set environment variable
                    os.environ[f"DOLBYMUSIC_{directory.upper()}_DIR"] = fallback_dir
                    print(f"🔄 Created fallback {directory} directory: {fallback_dir}", flush=True)
                except Exception as e2:
                    print(f"❌ Failed to create fallback for {directory}: {e2}", flush=True)
    
    # Set file operation permissions (if on Unix-like system)
    try:
        if os.name != 'nt':  # Not Windows
            for directory in ["downloads", "cache", "logs"]:
                if os.path.exists(directory):
                    os.chmod(directory, 0o755)
                    print(f"✅ Set permissions for {directory}", flush=True)
    except Exception as e:
        print(f"⚠️ Could not set permissions: {e}", flush=True)
    
    # Check critical files
    critical_files = [
        "Dolbymusic/__init__.py",
        "strings/langs/en.yml",
        "config.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ Critical file found: {file_path}", flush=True)
        else:
            print(f"❌ Critical file missing: {file_path}", flush=True)
            return False
    
    # Check environment variables
    required_env_vars = [
        "API_ID",
        "API_HASH", 
        "BOT_TOKEN",
        "MONGO_DB_URI",
        "OWNER_ID"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}", flush=True)
        return False
    else:
        print("✅ All required environment variables are set", flush=True)
    
    # Ensure Node.js and FFmpeg are in PATH for subprocesses
    for extra_bin in ["/tmp/node-bin", "/tmp/ffmpeg-bin"]:
        if os.path.isdir(extra_bin) and extra_bin not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{extra_bin}:{os.environ['PATH']}"
    
    # Set Python path
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✅ Added {current_dir} to Python path", flush=True)
    
    print("="*50, flush=True)
    print("✅ Heroku setup completed successfully!", flush=True)
    print(f"📂 Working directory: {current_dir}", flush=True)
    print(f"🐍 Python version: {sys.version}", flush=True)
    print("🎵 DolbyMusic setup complete!", flush=True)
    print("="*50, flush=True)
    
    return True

if __name__ == "__main__":
    if setup_heroku_environment():
        # Import and start the bot
        try:
            print("🎵 Starting DolbyMusic bot...", flush=True)
            print("⏳ Initializing bot modules...", flush=True)
            # Import the main module and run it
            import asyncio
            from Dolbymusic.__main__ import init
            
            # Run the bot's main function
            asyncio.get_event_loop().run_until_complete(init())
            
        except Exception as e:
            print(f"❌ Error starting bot: {e}", flush=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("❌ Setup failed. Please check your configuration.", flush=True)
        sys.exit(1)
