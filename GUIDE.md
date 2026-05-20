# The Ultimate Guide to Building a YouTube Video Downloader with Python

## Introduction
Welcome to this comprehensive tutorial! We have built a professional-grade YouTube Video Downloader that rivals commercial software. This tool supports **High Resolutions (1080p, 4K)**, **Dark Mode UI**, and **Smart Merging** technology.

## 1. Key Features
*   **Universal Download**: Supports standard (720p) and High Quality (1080p, 1440p, 4K) videos.
*   **Smart Merging**: YouTube separates audio and video for high qualities. Our app automatically downloads both and "glues" them together (merges) locally using FFmpeg.
*   **Robust Playability**:
    *   **Auto-Conversion**: If a video is in WebM format, the app can automatically allow it or convert text to ensure it plays on your PC.
    *   **Sanitization**: Handles complex filenames (Emoji, Kanji, Special Chars) safely so downloads never crash.
*   **Modern UI**: Built with `CustomTkinter` for a sleek look.

---

## 2. Installation & Setup

### Step A: Install Python
Ensure Python 3.10+ is installed from [python.org](https://www.python.org/downloads/) with **"Add to PATH"** checked.

### Step B: Install Libraries
We use `pytubefix` for downloading and `imageio-ffmpeg` for the merging engine.

```bash
pip install pytubefix customtkinter imageio-ffmpeg
```

*   **pytubefix**: Fixes broken YouTube downloads.
*   **customtkinter**: Making the UI look good.
*   **imageio-ffmpeg**: Provides the `ffmpeg` tool automatically, so you don't need to manually install it on Windows.

---

## 3. How It Works (The "Magic")

1.  **Analysis**: The app scans the URL. It finds "Progressive" streams (Audio+Video in one file, usually max 720p) and "Adaptive" streams (Video Only, up to 4K).
2.  **Selection**: You choose your quality.
    *   **Ready to Play**: Simple download, instant.
    *   **HQ (1080p+)**: Triggers the advanced flow.
3.  **The Advanced Flow (High Res)**:
    *   Downloads Video track to a hidden Temp folder.
    *   Downloads Audio track to a hidden Temp folder.
    *   **Merge**: Uses FFmpeg to copy the two tracks into a single MP4 file.
    *   **Fallback**: If strict copying fails (due to weird codecs), it automatically re-encodes the video to H.264 standard format to ensure it works.

---

## 4. Troubleshooting

### "Merge Failed" Error
*   This used to happen with complex filenames. We fixed it by using "Safe Filenames" internally.
*   If it persists, it might be your **Antivirus** blocking the `ffmpeg.exe` process from creating files. Allow python to write to disk.

### "No Streams Found"
*   The video might be Age Restricted (requires login) or Region Locked. This app does not currently support logging in with cookies.

### Slow Merging?
*   Merging usually takes 5-10 seconds. If it takes longer (minutes), the app has likely switched to "Re-encode Mode" because the original video format was incompatible. This ensures you get a working file, but takes more CPU power.

---

## 5. Running the App
1.  Open Terminal/Command Prompt.
2.  Navigate to the folder.
3.  Run:
    ```bash
    python main.py
    ```

Enjoy your 4K Downloads!
