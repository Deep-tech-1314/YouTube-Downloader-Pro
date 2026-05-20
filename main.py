import customtkinter as ctk
from tkinter import filedialog, messagebox
from pytubefix import YouTube
from pytubefix.cli import on_progress
import threading
import os
import sys
import tempfile
import subprocess
import shutil
# Use imageio_ffmpeg to get the binary path reliably without user having it in PATH
import imageio_ffmpeg

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("YouTube Downloader Pro")
        self.geometry("800x600")
        self.resizable(True, True)

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables
        self.url_var = ctk.StringVar()
        self.folder_path = ctk.StringVar(value=os.getcwd())
        self.video_streams = {}

        self.create_widgets()

    def create_widgets(self):
        # Main Container - Use PACK for the main frame to avoid conflict with root
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="YouTube Downloader", 
            font=("Roboto Medium", 28),
            text_color="#3B8ED0"
        )
        self.header_label.grid(row=0, column=0, pady=(10, 30))

        # URL Input Section
        self.url_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.url_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.url_frame.grid_columnconfigure(1, weight=1)
        
        self.link_icon = ctk.CTkLabel(self.url_frame, text="🔗", font=("Arial", 20))
        self.link_icon.grid(row=0, column=0, padx=15, pady=10)

        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            textvariable=self.url_var,
            placeholder_text="Paste YouTube Link Here...",
            height=40,
            font=("Roboto", 14),
            border_width=0
        )
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, sticky="ew", pady=5)
        self.btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.check_btn = ctk.CTkButton(
            self.btn_frame,
            text="Analyze Video",
            command=self.start_fetch_info,
            height=40,
            font=("Roboto Medium", 14),
            fg_color="#2CC985",
            hover_color="#229D68"
        )
        self.check_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Settings Section
        self.settings_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.settings_frame.grid(row=3, column=0, sticky="ew", pady=20)
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # Title Display
        self.video_title_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Waiting for link...", 
            font=("Roboto", 16), 
            text_color="gray"
        )
        self.video_title_label.grid(row=0, column=0, columnspan=3, pady=(15, 10), sticky="w", padx=15)

        # Resolution Dropdown
        ctk.CTkLabel(self.settings_frame, text="Resolution:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.res_option_menu = ctk.CTkOptionMenu(
            self.settings_frame, 
            values=["Fetch info first"],
            state="disabled"
        )
        self.res_option_menu.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Save Path
        ctk.CTkLabel(self.settings_frame, text="Save to:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        self.path_entry = ctk.CTkEntry(self.settings_frame, textvariable=self.folder_path, state="disabled")
        self.path_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=10)
        
        self.browse_btn = ctk.CTkButton(
            self.settings_frame, 
            text="Browse", 
            width=80, 
            command=self.select_directory
        )
        self.browse_btn.grid(row=2, column=2, padx=(0, 15), pady=10)

        # Progress Section
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=15)
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=(20, 10))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, sticky="w")
        
        self.percentage_label = ctk.CTkLabel(self.main_frame, text="0%", text_color="gray")
        self.percentage_label.grid(row=5, column=0, sticky="e")

        # Big Download Button
        self.download_btn = ctk.CTkButton(
            self.main_frame,
            text="DOWNLOAD VIDEO", 
            command=self.start_download,
            height=50,
            font=("Roboto Medium", 16),
            state="disabled",
            fg_color="#3B8ED0",
            hover_color="#2D6E9E"
        )
        self.download_btn.grid(row=6, column=0, sticky="ew", pady=20)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.folder_path.set(directory)

    def start_fetch_info(self):
        url = self.url_var.get().strip()
        if not url:
            self.flash_status("Please enter a valid URL", "red")
            return

        self.check_btn.configure(state="disabled", text="Analyzing...")
        self.status_label.configure(text="Connecting to YouTube...", text_color="#3B8ED0")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        threading.Thread(target=self.fetch_info_thread, args=(url,), daemon=True).start()

    def fetch_info_thread(self, url):
        try:
            self.yt = YouTube(url, on_progress_callback=self.on_progress)
            
            # 1. Get Progressive Streams (Audio+Video, max 720p)
            prog_streams = self.yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
            
            # 2. Get Adaptive Streams (Video Only, 1080p, 4K etc)
            # REMOVE EXTENSION FILTER to find all
            adapt_streams = self.yt.streams.filter(adaptive=True, only_video=True).order_by('resolution').desc()
            
            self.video_streams = {}
            options = []
            
            # Add Progressive Options
            for s in prog_streams:
                size_mb = s.filesize / 1024 / 1024
                # Note: codec info is nice but let's keep it simple "Ready to Play"
                label = f"{s.resolution} (Ready to Play) - {size_mb:.1f} MB"
                self.video_streams[label] = {"type": "progressive", "stream": s}
                options.append(label)

            # Add High Res Options
            seen_res = set() 
            # Sort: prioritize MP4 (avc1) first, then high res
            # Tuple sort: (Resolution Int, Is MP4?)
            sorted_adapt = sorted(adapt_streams, key=lambda s: (int(s.resolution[:-1]) if s.resolution else 0, s.mime_type == "video/mp4"), reverse=True)
            
            for s in sorted_adapt:
                if s.resolution and s.resolution not in seen_res:
                    try:
                        res_int = int(s.resolution.replace("p", ""))
                        if res_int > 720: # Only show high res that needs merging
                            size_mb = s.filesize / 1024 / 1024
                            ext = s.mime_type.split("/")[-1].upper() # MP4 or WEBM
                            label = f"{s.resolution} (HQ {ext}) - ~{size_mb:.1f} MB+"
                            self.video_streams[label] = {"type": "adaptive", "stream": s}
                            options.append(label)
                            seen_res.add(s.resolution)
                    except: pass

            if not options:
                raise Exception("No playable streams found.")

            self.after(0, lambda: self.update_ui_after_fetch(self.yt.title, options))

        except Exception as e:
            self.after(0, lambda: self.handle_error(str(e)))

    def update_ui_after_fetch(self, title, options):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        
        self.check_btn.configure(state="normal", text="Analyze Video")
        self.video_title_label.configure(text=f"Found: {title[:50]}..." if len(title) > 50 else f"Found: {title}", text_color="white")
        
        self.res_option_menu.configure(values=options, state="normal")
        self.res_option_menu.set(options[0])
        
        self.download_btn.configure(state="normal")
        self.status_label.configure(text="Select resolution and download.", text_color="white")

    def handle_error(self, msg):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        self.check_btn.configure(state="normal", text="Analyze Video")
        self.status_label.configure(text="Error occurred", text_color="#E53935")
        messagebox.showerror("Error", msg)

    def start_download(self):
        selected_label = self.res_option_menu.get()
        if not selected_label or selected_label not in self.video_streams:
            return

        data = self.video_streams[selected_label]
        target_dir = self.folder_path.get()
        
        self.download_btn.configure(state="disabled", text="DOWNLOADING...")
        self.status_label.configure(text="Initializing...", text_color="#3B8ED0")
        
        threading.Thread(target=self.download_thread, args=(data, target_dir), daemon=True).start()

    def sanitize_filename(self, name):
        # Remove invalid characters for Windows
        # < > : " / \ | ? *
        import re
        # Explicitly remove potentially dangerous full-width chars that look like operators
        # And strict ASCII conversion isn't needed, but deleting system chars is.
        # Simple regex for invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Also clean control characters
        name = "".join(c for c in name if c.isprintable())
        return name[:150] # Truncate to avoid MAX_PATH limits

    def download_thread(self, data, target_dir):
        # Create a temp directory that is invisible to user
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                download_type = data["type"]
                stream = data["stream"]
                
                # Sanitize the filename MANUALLY to ensure FFmpeg/Windows logic is happy
                # pytubefix does some, but we need to be stricter for FFmpeg output
                safe_title = self.sanitize_filename(stream.default_filename)
                
                # If original was webm, we still want final to be mp4 if possible for compatibility
                if safe_title.endswith(".webm"):
                    final_filename = safe_title.replace(".webm", ".mp4")
                else:
                    final_filename = safe_title
                
                final_path = os.path.join(target_dir, final_filename)

                if download_type == "progressive":
                    self.after(0, lambda: self.flash_status("Downloading Video...", "#3B8ED0"))
                    stream.download(output_path=target_dir)
                
                else: # Adaptive - needs merge
                    self.after(0, lambda: self.flash_status("Downloading High Res Video Track...", "#3B8ED0"))
                    
                    # 1. Download Video to System Temp (Use SAFE simple filename)
                    # We don't need the real title here, it causes encoding issues with FFmpeg on Windows
                    safe_video_name = "temp_video_track.mp4" 
                    if stream.mime_type == "video/webm":
                        safe_video_name = "temp_video_track.webm"
                        
                    stream.download(output_path=temp_dir, filename=safe_video_name)
                    video_path = os.path.join(temp_dir, safe_video_name)
                    
                    # 2. Download Audio to System Temp
                    self.after(0, lambda: self.flash_status("Downloading Audio Track...", "#3B8ED0"))
                    self.progress_bar.set(0.5)
                    
                    audio_stream = self.yt.streams.get_audio_only()
                    if not audio_stream:
                        raise Exception("No audio stream found for this video")
                        
                    safe_audio_name = "temp_audio_track.mp4"
                    audio_stream.download(output_path=temp_dir, filename=safe_audio_name) 
                    audio_path = os.path.join(temp_dir, safe_audio_name)

                    # 3. Merge with FFmpeg
                    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                    
                    # Strategy 1: Fast Copy (Preferred)
                    self.after(0, lambda: self.flash_status("Merging (Fast Copy)...", "#FFA500"))
                    
                    cmd_copy = [
                        ffmpeg_exe,
                        '-i', video_path,
                        '-i', audio_path,
                        '-c:v', 'copy', 
                        '-c:a', 'aac', 
                        final_path,
                        '-y', 
                        '-loglevel', 'error' 
                    ]
                    
                    creationflags = 0
                    if os.name == 'nt':
                        creationflags = subprocess.CREATE_NO_WINDOW
                        
                    result = subprocess.run(cmd_copy, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
                    
                    if result.returncode != 0:
                        # Strategy 2: Re-encode (Fallback for compatibility/errors)
                        print(f"Copy failed: {result.stderr.decode(errors='ignore')}. Retrying with re-encode...")
                        self.after(0, lambda: self.flash_status("Merging (Re-encoding to Fix)... this may take a while", "#FF5722"))
                        
                        cmd_encode = [
                            ffmpeg_exe,
                            '-i', video_path,
                            '-i', audio_path,
                            '-c:v', 'libx264', # Force standard H.264
                            '-c:a', 'aac', 
                            '-preset', 'fast', # Balance speed/size
                            final_path,
                            '-y', 
                            '-loglevel', 'error'
                        ]
                        
                        result2 = subprocess.run(cmd_encode, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
                        
                        if result2.returncode != 0:
                             raise Exception(f"Final Merge Failed: {result2.stderr.decode(errors='ignore')}")

                self.after(0, lambda: self.download_complete(final_path))

            except Exception as e:
                self.after(0, lambda: self.handle_error(str(e)))
                self.after(0, lambda: self.download_btn.configure(state="normal", text="DOWNLOAD VIDEO"))

    def download_complete(self, filepath):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1)
        self.percentage_label.configure(text="100%")
        
        self.status_label.configure(text="Download Complete!", text_color="#2CC985")
        self.download_btn.configure(state="normal", text="DOWNLOAD VIDEO")
        
        msg = f"Saved to:\n{filepath}\n\nDo you want to open the folder?"
        if messagebox.askyesno("Success", msg):
            folder = os.path.dirname(filepath)
            os.startfile(folder)

    def on_progress(self, stream, chunk, bytes_remaining):
        # Only meaningful for the main video stream download
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size
        self.after(0, lambda: self.update_progress_ui(percentage))

    def update_progress_ui(self, percentage):
        if "Merging" not in self.status_label.cget("text"):
             self.progress_bar.set(percentage)
             self.percentage_label.configure(text=f"{int(percentage * 100)}%")

    def flash_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
