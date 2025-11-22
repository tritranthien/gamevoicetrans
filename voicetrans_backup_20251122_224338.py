import pyaudiowpatch as pyaudio
import numpy as np
import threading
import queue
import time
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import pyttsx3
from gtts import gTTS
import edge_tts
import asyncio
import pygame
import tempfile
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
import torch

class AudioTranslatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Real-time Audio Translator - Chinese to Vietnamese")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Biến trạng thái
        self.is_running = False
        self.translator_engine = None
        
        # Khởi tạo audio
        self.audio = pyaudio.PyAudio()
        
        # Tạo UI
        self.create_ui()
        
        # Load devices
        self.load_audio_devices()
        
        # Kiểm tra GPU
        self.check_gpu()
        
    def create_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#2b2b2b', foreground='white', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TCombobox', font=('Arial', 9))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#2b2b2b', foreground='#4CAF50')
        
        # === HEADER ===
        header = tk.Frame(self.root, bg='#1e1e1e', height=60)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        title = tk.Label(header, text="🎙️ Real-time Audio Translator", 
                        font=('Arial', 16, 'bold'), bg='#1e1e1e', fg='#4CAF50')
        title.pack(pady=10)
        
        # === SETTINGS FRAME ===
        settings_frame = tk.LabelFrame(self.root, text="⚙️ Settings", 
                                      bg='#2b2b2b', fg='white', 
                                      font=('Arial', 11, 'bold'),
                                      padx=15, pady=15)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # GPU Info
        gpu_frame = tk.Frame(settings_frame, bg='#2b2b2b')
        gpu_frame.grid(row=0, column=0, columnspan=3, sticky='w', pady=5)
        
        ttk.Label(gpu_frame, text="🎮 GPU Status:").pack(side=tk.LEFT, padx=5)
        self.gpu_label = tk.Label(gpu_frame, text="Checking...", 
                                 bg='#2b2b2b', fg='yellow', font=('Arial', 9))
        self.gpu_label.pack(side=tk.LEFT, padx=5)
        
        # Audio Device
        ttk.Label(settings_frame, text="🔊 Audio Source:").grid(row=1, column=0, sticky='w', pady=5)
        self.device_combo = ttk.Combobox(settings_frame, width=40, state='readonly')
        self.device_combo.grid(row=1, column=1, columnspan=2, sticky='ew', pady=5, padx=5)
        
        # Device detail info
        self.device_detail_label = tk.Label(settings_frame, text="Select a device to see details",
                                           bg='#2b2b2b', fg='#888', font=('Arial', 8))
        self.device_detail_label.grid(row=2, column=1, columnspan=2, sticky='w', padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(settings_frame, text="🔄", command=self.refresh_devices,
                               bg='#3d3d3d', fg='white', font=('Arial', 8), width=3,
                               cursor='hand2', relief=tk.FLAT)
        refresh_btn.grid(row=1, column=3, padx=5)
        
        # Whisper Model
        ttk.Label(settings_frame, text="🧠 Whisper Model:").grid(row=3, column=0, sticky='w', pady=5)
        self.model_combo = ttk.Combobox(settings_frame, width=20, state='readonly',
                                       values=['tiny', 'base', 'small', 'medium', 'large-v2'])
        self.model_combo.set('medium')
        self.model_combo.grid(row=3, column=1, sticky='w', pady=5, padx=5)
        
        self.model_info = tk.Label(settings_frame, text="90-95% accuracy, ~0.5s latency",
                                   bg='#2b2b2b', fg='#888', font=('Arial', 8))
        self.model_info.grid(row=3, column=2, sticky='w', padx=5)
        self.model_combo.bind('<<ComboboxSelected>>', self.update_model_info)
        
        # Compute Type
        ttk.Label(settings_frame, text="⚡ Compute Type:").grid(row=4, column=0, sticky='w', pady=5)
        self.compute_combo = ttk.Combobox(settings_frame, width=20, state='readonly',
                                         values=['float16', 'int8', 'float32'])
        self.compute_combo.set('float16')
        self.compute_combo.grid(row=4, column=1, sticky='w', pady=5, padx=5)
        
        compute_info = tk.Label(settings_frame, text="float16: Fast GPU | int8: Save VRAM | float32: CPU",
                               bg='#2b2b2b', fg='#888', font=('Arial', 8))
        compute_info.grid(row=4, column=2, sticky='w', padx=5)
        
        # Beam Size
        ttk.Label(settings_frame, text="🎯 Beam Size:").grid(row=5, column=0, sticky='w', pady=5)
        self.beam_scale = tk.Scale(settings_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                  bg='#2b2b2b', fg='white', highlightthickness=0,
                                  length=150, troughcolor='#444')
        self.beam_scale.set(5)
        self.beam_scale.grid(row=5, column=1, sticky='w', pady=5, padx=5)
        
        beam_info = tk.Label(settings_frame, text="Higher = More accurate but slower",
                            bg='#2b2b2b', fg='#888', font=('Arial', 8))
        beam_info.grid(row=5, column=2, sticky='w', padx=5)
        
        # Silence Threshold
        ttk.Label(settings_frame, text="🔇 Silence Threshold:").grid(row=6, column=0, sticky='w', pady=5)
        self.threshold_scale = tk.Scale(settings_frame, from_=100, to=2000, orient=tk.HORIZONTAL,
                                       bg='#2b2b2b', fg='white', highlightthickness=0,
                                       length=150, troughcolor='#444')
        self.threshold_scale.set(500)
        self.threshold_scale.grid(row=6, column=1, sticky='w', pady=5, padx=5)
        
        threshold_info = tk.Label(settings_frame, text="Lower = More sensitive to sound",
                                 bg='#2b2b2b', fg='#888', font=('Arial', 8))
        threshold_info.grid(row=6, column=2, sticky='w', padx=5)
        
        # TTS Speed
        ttk.Label(settings_frame, text="🗣️ TTS Speed:").grid(row=7, column=0, sticky='w', pady=5)
        self.tts_scale = tk.Scale(settings_frame, from_=100, to=250, orient=tk.HORIZONTAL,
                                 bg='#2b2b2b', fg='white', highlightthickness=0,
                                 length=150, troughcolor='#444')
        self.tts_scale.set(180)
        self.tts_scale.grid(row=7, column=1, sticky='w', pady=5, padx=5)
        
        tts_info = tk.Label(settings_frame, text="Higher = Faster speech",
                           bg='#2b2b2b', fg='#888', font=('Arial', 8))
        tts_info.grid(row=7, column=2, sticky='w', padx=5)
        
        # TTS Engine Selection (Radio buttons)
        ttk.Label(settings_frame, text="🔊 TTS Engine:").grid(row=8, column=0, sticky='w', pady=5)
        
        self.tts_engine_var = tk.StringVar(value="edge")  # Default to Edge TTS
        
        tts_radio_frame = tk.Frame(settings_frame, bg='#2b2b2b')
        tts_radio_frame.grid(row=8, column=1, columnspan=2, sticky='w', pady=5, padx=5)
        
        tk.Radiobutton(tts_radio_frame, 
                      text="⚡ pyttsx3 (Fastest, ~50ms)",
                      variable=self.tts_engine_var,
                      value="pyttsx3",
                      bg='#2b2b2b', fg='white',
                      selectcolor='#1e1e1e',
                      activebackground='#2b2b2b',
                      activeforeground='white',
                      font=('Arial', 9)).pack(anchor='w')
        
        tk.Radiobutton(tts_radio_frame, 
                      text="🌐 Google TTS (Balanced, ~300ms)",
                      variable=self.tts_engine_var,
                      value="gtts",
                      bg='#2b2b2b', fg='white',
                      selectcolor='#1e1e1e',
                      activebackground='#2b2b2b',
                      activeforeground='white',
                      font=('Arial', 9)).pack(anchor='w')
        
        tk.Radiobutton(tts_radio_frame, 
                      text="🎯 Edge TTS (Best Quality, ~500ms)",
                      variable=self.tts_engine_var,
                      value="edge",
                      bg='#2b2b2b', fg='white',
                      selectcolor='#1e1e1e',
                      activebackground='#2b2b2b',
                      activeforeground='white',
                      font=('Arial', 9)).pack(anchor='w')
        
        # Pause Detection Time
        ttk.Label(settings_frame, text="⏸️ Pause Detection:").grid(row=9, column=0, sticky='w', pady=5)
        self.pause_scale = tk.Scale(settings_frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL,
                                   bg='#2b2b2b', fg='white', highlightthickness=0,
                                   length=150, troughcolor='#444')
        self.pause_scale.set(0.3)  # Default 0.3s for faster response
        self.pause_scale.grid(row=9, column=1, sticky='w', pady=5, padx=5)
        
        pause_info = tk.Label(settings_frame, text="Lower = Faster translation",
                             bg='#2b2b2b', fg='#888', font=('Arial', 8))
        pause_info.grid(row=9, column=2, sticky='w', padx=5)
        
        # Min Audio Length
        ttk.Label(settings_frame, text="📏 Min Audio Length:").grid(row=10, column=0, sticky='w', pady=5)
        self.min_audio_scale = tk.Scale(settings_frame, from_=0.2, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                       bg='#2b2b2b', fg='white', highlightthickness=0,
                                       length=150, troughcolor='#444')
        self.min_audio_scale.set(0.5)  # Default 0.5s for short sentences
        self.min_audio_scale.grid(row=10, column=1, sticky='w', pady=5, padx=5)
        
        min_audio_info = tk.Label(settings_frame, text="Lower = Catch short sentences",
                                 bg='#2b2b2b', fg='#888', font=('Arial', 8))
        min_audio_info.grid(row=10, column=2, sticky='w', padx=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # === CONTROL BUTTONS ===
        control_frame = tk.Frame(self.root, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = tk.Button(control_frame, text="▶️ START", 
                                   command=self.start_translation,
                                   bg='#4CAF50', fg='white', 
                                   font=('Arial', 12, 'bold'),
                                   width=15, height=2,
                                   cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP",
                                  command=self.stop_translation,
                                  bg='#f44336', fg='white',
                                  font=('Arial', 12, 'bold'),
                                  width=15, height=2,
                                  state=tk.DISABLED,
                                  cursor='hand2')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(control_frame, text="🗑️ CLEAR LOG",
                                   command=self.clear_log,
                                   bg='#FF9800', fg='white',
                                   font=('Arial', 12, 'bold'),
                                   width=15, height=2,
                                   cursor='hand2')
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # === STATUS BAR ===
        status_frame = tk.Frame(self.root, bg='#1e1e1e', height=30)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="⏸️ Idle", 
                                     bg='#1e1e1e', fg='#888',
                                     font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.latency_label = tk.Label(status_frame, text="Latency: -- ms",
                                      bg='#1e1e1e', fg='#888',
                                      font=('Arial', 10))
        self.latency_label.pack(side=tk.RIGHT, padx=10)
        
        # === LOG OUTPUT ===
        log_frame = tk.LabelFrame(self.root, text="📋 Translation Log",
                                 bg='#2b2b2b', fg='white',
                                 font=('Arial', 11, 'bold'),
                                 padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                  bg='#1e1e1e', fg='#4CAF50',
                                                  font=('Consolas', 9),
                                                  height=15,
                                                  wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags cho màu sắc
        self.log_text.tag_config('chinese', foreground='#2196F3')
        self.log_text.tag_config('vietnamese', foreground='#4CAF50')
        self.log_text.tag_config('info', foreground='#FFC107')
        self.log_text.tag_config('error', foreground='#f44336')
        
    def check_gpu(self):
        """Kiểm tra GPU"""
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            self.gpu_label.config(text=f"✅ {gpu_name} ({vram:.1f} GB)", fg='#4CAF50')
            self.log(f"✅ GPU Detected: {gpu_name} with {vram:.1f} GB VRAM", 'info')
        else:
            self.gpu_label.config(text="⚠️ No GPU - Using CPU", fg='orange')
            self.log("⚠️ No GPU detected, will use CPU (slower)", 'info')
            self.compute_combo.set('int8')
    
    def load_audio_devices(self):
        """Load danh sách audio devices"""
        devices = []
        self.device_indices = []
        self.device_infos = []
        
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                name = info['name']
                
                # Thêm icon cho các loại device
                if 'loopback' in name.lower():
                    icon = "🔁"
                elif 'microphone' in name.lower() or 'mic' in name.lower():
                    icon = "🎤"
                elif 'stereo mix' in name.lower():
                    icon = "🔊"
                else:
                    icon = "🔉"
                
                display_name = f"{icon} {name}"
                devices.append(display_name)
                self.device_indices.append(i)
                self.device_infos.append(info)
        
        self.device_combo['values'] = devices
        if devices:
            # Tự động chọn loopback device nếu có
            try:
                default = self.audio.get_default_wasapi_loopback()
                default_name = default['name']
                for idx, info in enumerate(self.device_infos):
                    if default_name == info['name']:
                        self.device_combo.current(idx)
                        break
                else:
                    self.device_combo.current(0)
            except:
                self.device_combo.current(0)
        
        # Bind sự kiện để hiển thị thông tin chi tiết
        self.device_combo.bind('<<ComboboxSelected>>', self.on_device_selected)
    
    def on_device_selected(self, event=None):
        """Hiển thị thông tin chi tiết về device được chọn"""
        if self.device_combo.current() >= 0:
            info = self.device_infos[self.device_combo.current()]
            detail = f"Sample Rate: {int(info['defaultSampleRate'])} Hz | "
            detail += f"Channels: {info['maxInputChannels']} | "
            detail += f"Type: {'Loopback' if 'loopback' in info['name'].lower() else 'Input'}"
            
            # Hiển thị tooltip hoặc status
            if hasattr(self, 'device_detail_label'):
                self.device_detail_label.config(text=detail)
    
    def update_model_info(self, event=None):
        """Cập nhật thông tin model"""
        model = self.model_combo.get()
        info_map = {
            'tiny': '70-75% accuracy, ~0.1s latency, 1GB VRAM',
            'base': '75-80% accuracy, ~0.2s latency, 1GB VRAM',
            'small': '85-90% accuracy, ~0.3s latency, 2GB VRAM',
            'medium': '90-95% accuracy, ~0.5s latency, 5GB VRAM',
            'large-v2': '97-99% accuracy, ~1s latency, 10GB VRAM'
        }
        self.model_info.config(text=info_map.get(model, ''))
    
    def log(self, message, tag='info'):
        """Ghi log"""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete(1.0, tk.END)
    
    def refresh_devices(self):
        """Refresh danh sách audio devices"""
        self.log("🔄 Refreshing audio devices...", 'info')
        self.load_audio_devices()
        self.log(f"✅ Found {len(self.device_indices)} audio devices", 'info')
    
    def start_translation(self):
        """Bắt đầu dịch"""
        if self.is_running:
            return
        
        # Kiểm tra device được chọn
        if not self.device_combo.get():
            self.log("❌ Please select an audio device!", 'error')
            return
        
        device_idx = self.device_indices[self.device_combo.current()]
        
        # Disable controls
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.device_combo.config(state=tk.DISABLED)
        self.model_combo.config(state=tk.DISABLED)
        self.compute_combo.config(state=tk.DISABLED)
        
        self.status_label.config(text="🔄 Starting...", fg='yellow')
        self.log("🚀 Initializing translator engine...", 'info')
        
        # Khởi tạo translator trong thread riêng
        threading.Thread(target=self._init_translator, 
                        args=(device_idx,), 
                        daemon=True).start()
    
    def _init_translator(self, device_idx):
        """Khởi tạo translator engine"""
        try:
            settings = {
                'model': self.model_combo.get(),
                'compute_type': self.compute_combo.get(),
                'beam_size': self.beam_scale.get(),
                'silence_threshold': self.threshold_scale.get(),
                'tts_speed': self.tts_scale.get(),
                'device_index': device_idx,
                'tts_engine': self.tts_engine_var.get(),  # TTS engine selection
                'pause_time': self.pause_scale.get(),  # Add pause detection time
                'min_audio_length': self.min_audio_scale.get()  # Add min audio length
            }
            
            self.translator_engine = TranslatorEngine(settings, self)
            self.is_running = True
            self.translator_engine.start()
            
            self.status_label.config(text="✅ Running", fg='#4CAF50')
            self.log("✅ Translation engine started!", 'info')
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", 'error')
            self.stop_translation()
    
    def stop_translation(self):
        """Dừng dịch"""
        if not self.is_running:
            return
        
        self.status_label.config(text="🔄 Stopping...", fg='yellow')
        self.log("🛑 Stopping translator...", 'info')
        
        if self.translator_engine:
            self.translator_engine.stop()
            self.translator_engine = None
        
        self.is_running = False
        
        # Enable controls
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.device_combo.config(state='readonly')
        self.model_combo.config(state='readonly')
        self.compute_combo.config(state='readonly')
        
        self.status_label.config(text="⏸️ Idle", fg='#888')
        self.log("✅ Translator stopped", 'info')
    
    def update_latency(self, latency_ms):
        """Cập nhật latency"""
        color = '#4CAF50' if latency_ms < 1000 else '#FFC107' if latency_ms < 2000 else '#f44336'
        self.latency_label.config(text=f"Latency: {latency_ms:.0f} ms", fg=color)


class TranslatorEngine:
    def __init__(self, settings, ui):
        self.settings = settings
        self.ui = ui
        self.is_running = False
        self.is_tts_playing = False  # Flag to pause capture during TTS playback
        
        self.audio = pyaudio.PyAudio()
        self.chunk = 512
        self.format = pyaudio.paInt16
        
        # Get device info to determine supported sample rate and channels
        device_info = self.audio.get_device_info_by_index(settings['device_index'])
        self.device_rate = int(device_info['defaultSampleRate'])
        self.channels = min(int(device_info['maxInputChannels']), 2)  # Use mono or stereo
        
        # Whisper expects 16kHz, we'll resample if needed
        self.whisper_rate = 16000
        self.rate = self.device_rate  # Use device's native rate for capture
        
        # Sentence detection parameters (configurable)
        self.pause_time = settings.get('pause_time', 0.3)  # Time to wait for silence
        self.min_audio_length = settings.get('min_audio_length', 0.5)  # Minimum audio duration
        
        self.ui.log(f"🎵 Device sample rate: {self.device_rate} Hz, Channels: {self.channels}", 'info')
        self.ui.log(f"⏸️ Pause detection: {self.pause_time}s, Min audio: {self.min_audio_length}s", 'info')
        
        # Queues
        self.audio_queue = queue.Queue(maxsize=5)
        self.text_queue = queue.Queue(maxsize=5)
        self.translation_queue = queue.Queue(maxsize=5)
        
        # Load Whisper
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ui.log(f"📥 Loading Whisper model '{settings['model']}' on {device}...", 'info')
        
        self.whisper_model = WhisperModel(
            settings['model'],
            device=device,
            compute_type=settings['compute_type']
        )
        
        self.ui.log("✅ Whisper model loaded!", 'info')
        
        # Translator
        self.translator = GoogleTranslator(source='zh-CN', target='vi')
        
        # TTS - Support pyttsx3, Google TTS, and Edge TTS
        self.tts_mode = settings.get('tts_engine', 'edge')  # 'pyttsx3', 'gtts', or 'edge'
        self.tts_engine = None
        self.selected_voice_id = None
        
        # TTS lock to prevent overlapping audio
        self.tts_lock = threading.Lock()
        
        # Initialize pygame mixer (used by both gTTS and Edge TTS)
        if self.tts_mode in ['gtts', 'edge']:
            try:
                pygame.mixer.init()
                self.ui.log(f"✅ Pygame mixer initialized for {self.tts_mode.upper()}", 'info')
            except Exception as e:
                self.ui.log(f"❌ pygame mixer error: {str(e)}", 'error')
        
        if self.tts_mode == 'edge':
            # Edge TTS - Use Microsoft Neural voices
            self.ui.log("✅ Edge TTS selected (Microsoft Neural Voices)", 'info')
            self.ui.log("   Available: HoaiMyNeural (Female), NamMinhNeural (Male)", 'info')
            
            # Store both voices
            self.edge_voice_female = "vi-VN-HoaiMyNeural"
            self.edge_voice_male = "vi-VN-NamMinhNeural"
            self.edge_voice = self.edge_voice_female  # Default to female
            
        elif self.tts_mode == 'gtts':
            # Google TTS
            self.ui.log("✅ Google TTS (gTTS) initialized!", 'info')
            
        else:  # pyttsx3
            # Use pyttsx3
            try:
                self.tts_engine = pyttsx3.init()
                
                # Set properties
                self.tts_engine.setProperty('rate', settings['tts_speed'])
                self.tts_engine.setProperty('volume', 1.0)  # Max volume
                
                # Try to find and use a Vietnamese voice if available
                voices = self.tts_engine.getProperty('voices')
                self.ui.log(f"🔊 Found {len(voices)} TTS voices on system", 'info')
                
                # List ALL voices for debugging
                self.ui.log("📋 Available voices:", 'info')
                for i, voice in enumerate(voices):
                    voice_info = f"  [{i+1}] {voice.name}"
                    # Add language info if available
                    if hasattr(voice, 'languages') and voice.languages:
                        voice_info += f" | Lang: {voice.languages}"
                    # Add ID for debugging
                    voice_info += f" | ID: {voice.id}"
                    self.ui.log(voice_info, 'info')
                
                # Look for Vietnamese voice with multiple patterns
                vietnamese_voice = None
                for voice in voices:
                    name_lower = voice.name.lower()
                    id_lower = voice.id.lower()
                    
                    # Check multiple patterns for Vietnamese
                    is_vietnamese = False
                    if 'vietnam' in name_lower or 'việt' in name_lower or 'viet' in name_lower:
                        is_vietnamese = True
                    if 'vi-' in id_lower or 'vi_' in id_lower or 'vi-vn' in id_lower or 'vivn' in id_lower:
                        is_vietnamese = True
                    if hasattr(voice, 'languages') and voice.languages:
                        for lang in voice.languages:
                            if 'vi' in str(lang).lower() or 'vietnam' in str(lang).lower():
                                is_vietnamese = True
                    
                    if is_vietnamese:
                        vietnamese_voice = voice
                        break
                
                if vietnamese_voice:
                    self.tts_engine.setProperty('voice', vietnamese_voice.id)
                    self.selected_voice_id = vietnamese_voice.id  # Store for later use
                    self.ui.log(f"✅ Using Vietnamese voice: {vietnamese_voice.name}", 'info')
                    self.ui.log(f"   Voice ID: {vietnamese_voice.id}", 'info')
                else:
                    # Use first available voice
                    if voices:
                        self.tts_engine.setProperty('voice', voices[0].id)
                        self.selected_voice_id = voices[0].id
                        self.ui.log(f"⚠️ No Vietnamese voice detected!", 'error')
                        self.ui.log(f"⚠️ Using fallback voice: {voices[0].name}", 'info')
                        self.ui.log(f"💡 TIP: Try Edge TTS for better Vietnamese support", 'info')
                    else:
                        self.ui.log("⚠️ No TTS voices available", 'info')
                        
            except Exception as e:
                self.ui.log(f"❌ TTS initialization error: {str(e)}", 'error')
                self.tts_engine = None
                self.selected_voice_id = None
    
    def start(self):
        """Bắt đầu các threads"""
        self.is_running = True
        
        threads = [
            threading.Thread(target=self.audio_capture_thread, daemon=True),
            threading.Thread(target=self.speech_to_text_thread, daemon=True),
            threading.Thread(target=self.translation_thread, daemon=True),
            threading.Thread(target=self.tts_thread, daemon=True)
        ]
        
        for t in threads:
            t.start()
    
    def stop(self):
        """Dừng engine"""
        self.is_running = False
        time.sleep(0.5)
    
    def calculate_rms(self, audio_data):
        """Tính RMS"""
        if not audio_data or len(audio_data) == 0:
            return 0.0
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            if len(audio_array) == 0:
                return 0.0
            
            # Calculate mean of squared values
            mean_square = np.mean(audio_array.astype(np.float64)**2)
            
            # Ensure non-negative before sqrt
            if mean_square < 0:
                return 0.0
            
            return np.sqrt(mean_square)
        except Exception:
            return 0.0
    
    def detect_gender(self, audio_array):
        """
        Detect gender based on pitch (fundamental frequency)
        Male: typically 85-180 Hz
        Female: typically 165-255 Hz
        Returns: 'male', 'female', or 'unknown'
        """
        try:
            # Simple pitch detection using autocorrelation
            correlation = np.correlate(audio_array, audio_array, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # Find the first peak after the zero lag
            diff = np.diff(correlation)
            start = np.where(diff > 0)[0]
            if len(start) == 0:
                return "unknown"
            
            start = start[0]
            peak = np.argmax(correlation[start:]) + start
            
            # Calculate frequency
            if peak == 0:
                return "unknown"
            
            frequency = self.whisper_rate / peak
            
            # Classify based on frequency
            if frequency < 165:
                return "male"
            elif frequency > 180:
                return "female"
            else:
                return "unknown"  # Overlap zone
                
        except Exception:
            return "unknown"
    
    def resample_audio(self, audio_data):
        """Resample audio from device rate to Whisper rate (16kHz)"""
        if self.device_rate == self.whisper_rate:
            return audio_data
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # If stereo, convert to mono
        if self.channels == 2:
            audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
        
        # Resample
        num_samples = int(len(audio_array) * self.whisper_rate / self.device_rate)
        resampled = np.interp(
            np.linspace(0, len(audio_array), num_samples),
            np.arange(len(audio_array)),
            audio_array
        ).astype(np.int16)
        
        return resampled.tobytes()
    
    def audio_capture_thread(self):
        """Capture audio"""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=self.settings['device_index'],
            frames_per_buffer=self.chunk
        )
        
        buffer = []
        silence_counter = 0
        is_speaking = False
        
        # Calculate frame counts based on user settings
        pause_frames = int(self.rate / self.chunk * self.pause_time)
        min_audio_frames = int(self.rate / self.chunk * self.min_audio_length)
        
        while self.is_running:
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                
                # Skip processing if TTS is playing to avoid feedback loop
                if self.is_tts_playing:
                    # Clear buffer when TTS starts
                    if buffer:
                        buffer = []
                        silence_counter = 0
                        is_speaking = False
                    continue
                
                rms = self.calculate_rms(data)
                
                if rms > self.settings['silence_threshold']:
                    buffer.append(data)
                    silence_counter = 0
                    if not is_speaking:
                        is_speaking = True
                        self.ui.log("🗣️ Speech detected...", 'info')
                else:
                    if is_speaking:
                        silence_counter += 1
                        buffer.append(data)
                        
                        # Use dynamic pause time instead of hardcoded 0.5
                        if silence_counter > pause_frames:
                            # Use dynamic min audio length instead of hardcoded 1.0
                            if len(buffer) > min_audio_frames:
                                audio_data = b''.join(buffer)
                                if not self.audio_queue.full():
                                    self.audio_queue.put(audio_data)
                                    self.ui.log(f"📤 Audio sent ({len(buffer)} frames, {len(buffer)*self.chunk/self.rate:.2f}s)", 'info')
                            
                            buffer = []
                            silence_counter = 0
                            is_speaking = False
                            
            except Exception as e:
                break
        
        stream.stop_stream()
        stream.close()
    
    def speech_to_text_thread(self):
        """STT thread"""
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                start_time = time.time()
                
                # Resample to 16kHz for Whisper
                resampled_data = self.resample_audio(audio_data)
                audio_array = np.frombuffer(resampled_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Detect gender from audio
                gender = self.detect_gender(audio_array)
                
                segments, info = self.whisper_model.transcribe(
                    audio_array,
                    language="zh",
                    beam_size=self.settings['beam_size'],
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=100),  # Faster VAD
                    no_speech_threshold=0.6,  # Skip if no speech detected
                    initial_prompt="以下是普通话的句子。"
                )
                
                transcript = " ".join([segment.text for segment in segments])
                stt_time = (time.time() - start_time) * 1000
                
                if transcript.strip():
                    gender_icon = "👨" if gender == "male" else "👩" if gender == "female" else "👤"
                    self.ui.log(f"🇨🇳 {gender_icon} [{stt_time:.0f}ms] {transcript}", 'chinese')
                    # Pass gender along with transcript
                    self.text_queue.put((transcript, time.time(), gender))
                
            except queue.Empty:
                continue
            except Exception as e:
                self.ui.log(f"❌ STT Error: {str(e)}", 'error')
    def tts_thread(self):
        """TTS thread"""
        while self.is_running:
            try:
                text, start_time = self.translation_queue.get(timeout=1)
                
                # Use lock to prevent overlapping TTS
                with self.tts_lock:
                    # Set flag to pause audio capture during TTS playback
                    self.is_tts_playing = True
                    
                    if self.tts_mode == 'edge':
                        # Use Edge TTS (Microsoft Neural Voice)
                        try:
                            tts_start = time.time()
                            self.ui.log(f"🔊 Speaking (Edge TTS): {text[:50]}...", 'info')
                            
                            # Stop any currently playing audio
                            try:
                                if pygame.mixer.music.get_busy():
                                    pygame.mixer.music.stop()
                                    time.sleep(0.05)  # Small delay after stopping
                            except:
                                pass
                            
                            # Create temporary file for audio
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                temp_file = fp.name
                            
                            # Generate speech with Edge TTS (async)
                            async def generate_edge_tts():
                                communicate = edge_tts.Communicate(text, self.edge_voice)
                                await communicate.save(temp_file)
                            
                            # Run the async function
                            asyncio.run(generate_edge_tts())
                            
                            generation_time = (time.time() - tts_start) * 1000
                            self.ui.log(f"   Generated audio in {generation_time:.0f}ms", 'info')
                            
                            # Play audio with pygame
                            pygame.mixer.music.load(temp_file)
                            time.sleep(0.1)  # Small delay to allow buffering
                            pygame.mixer.music.play()
                            
                            # Wait for playback to finish
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.05)
                            
                            # Clean up temp file
                            try:
                                os.unlink(temp_file)
                            except:
                                pass
                                
                        except Exception as tts_error:
                            self.ui.log(f"❌ Edge TTS error: {str(tts_error)}", 'error')
                            
                    elif self.tts_mode == 'gtts':
                        # Use Google TTS (optimized for speed)
                        try:
                            tts_start = time.time()
                            self.ui.log(f"🔊 Speaking (gTTS): {text[:50]}...", 'info')
                            
                            # Stop any currently playing audio
                            try:
                                if pygame.mixer.music.get_busy():
                                    pygame.mixer.music.stop()
                                    time.sleep(0.05)  # Small delay after stopping
                            except:
                                pass
                            
                            # Create temporary file for audio
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                temp_file = fp.name
                            
                            # Generate speech with gTTS (with timeout for faster failure)
                            tts = gTTS(text=text, lang='vi', slow=False, timeout=3)
                            tts.save(temp_file)
                            
                            generation_time = (time.time() - tts_start) * 1000
                            self.ui.log(f"   Generated audio in {generation_time:.0f}ms", 'info')
                            
                            # Play audio with pygame
                            pygame.mixer.music.load(temp_file)
                            time.sleep(0.1)  # Small delay to allow buffering
                            pygame.mixer.music.play()
                            
                            # Wait for playback to finish
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.05)
                            
                            # Clean up temp file
                            try:
                                os.unlink(temp_file)
                            except:
                                pass
                                
                        except Exception as tts_error:
                            self.ui.log(f"❌ gTTS error: {str(tts_error)}", 'error')
                            
                    else:  # pyttsx3
                        # Use pyttsx3 with proper thread handling
                        if self.tts_engine:
                            try:
                                self.ui.log(f"🔊 Speaking (pyttsx3): {text[:50]}...", 'info')
                                
                                # Create a new engine instance for each call to avoid event loop conflicts
                                temp_engine = pyttsx3.init()
                                temp_engine.setProperty('rate', self.settings['tts_speed'])
                                temp_engine.setProperty('volume', 1.0)
                                
                                # Use the stored voice ID
                                if hasattr(self, 'selected_voice_id') and self.selected_voice_id:
                                    temp_engine.setProperty('voice', self.selected_voice_id)
                                
                                temp_engine.say(text)
                                temp_engine.runAndWait()
                                
                                # Clean up the temporary engine
                                del temp_engine
                                
                            except Exception as tts_error:
                                self.ui.log(f"❌ TTS playback error: {str(tts_error)}", 'error')
                        else:
                            self.ui.log("⚠️ TTS engine not available", 'info')
                    
                    # Clear flag to resume audio capture
                    self.is_tts_playing = False
                
                total_time = (time.time() - start_time) * 1000
                self.ui.log(f"✅ Total latency: {total_time:.0f}ms\n{'='*50}", 'info')
                self.ui.update_latency(total_time)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.ui.log(f"❌ TTS Error: {str(e)}", 'error')


def main():
    print("🚀 Starting Real-time Audio Translator...")
    print("📦 Initializing Tkinter...")
    root = tk.Tk()
    print("🎨 Creating UI...")
    app = AudioTranslatorUI(root)
    print("✅ UI created successfully!")
    print("🔄 Starting main loop...")
    root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("Real-time Audio Translator - Chinese to Vietnamese")
    print("=" * 50)
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

