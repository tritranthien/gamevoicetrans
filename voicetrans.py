"""
Real-time Audio Translator - Chinese to Vietnamese
Architecture: 3-Thread Pipeline (Listen -> Translate -> Speak)
"""
import pyaudiowpatch as pyaudio
import numpy as np
import threading
import queue
import time
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import ttk, scrolledtext
import torch
import sys
import pygame
import os
import tempfile

# Import our modules
from tts_engine import TTSEngine
from audio_utils import AudioUtils
from config import Config

class TranslatorEngine:
    def __init__(self, settings, ui):
        self.settings = settings
        self.ui = ui
        self.is_running = False
        
        # Audio settings
        self.audio = pyaudio.PyAudio()
        self.chunk = Config.AUDIO['chunk_size']
        self.format = pyaudio.paFloat32 # Use Float32 for WASAPI compatibility
        self.device_index = settings.get('device_index', None) # Store user-selected device
        
        # Queues for 3-Thread Pipeline
        self.trans_queue = queue.Queue() # Thread 1 -> Thread 2
        self.tts_queue = queue.Queue()   # Thread 2 -> Thread 3
        
        # Initialize Engines
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = WhisperModel(
            settings['model'],
            device=device,
            compute_type=settings['compute_type']
        )
        if ui: ui.log(f"✅ Whisper loaded on {device.upper()}", 'info')
        
        try:
            self.translator = GoogleTranslator(source='zh-CN', target='vi')
            if ui: ui.log("✅ Google Translate ready", 'success')
        except Exception as e:
            if ui: ui.log(f"❌ Translator Error: {e}", 'error')
            
        self.tts_engine = TTSEngine(
            mode=settings.get('tts_engine', 'edge'),
            ui=ui,
            settings=settings
        )

    def start(self):
        self.is_running = True
        
        # Thread 1: Listen & Transcribe
        self.thread1 = threading.Thread(target=self.speech_to_text_thread, daemon=True)
        self.thread1.start()
        
        # Thread 2: Translate
        self.thread2 = threading.Thread(target=self.translation_thread, daemon=True)
        self.thread2.start()
        
        # Thread 3: Output (TTS & Play)
        self.thread3 = threading.Thread(target=self.output_thread, daemon=True)
        self.thread3.start()
        
        if self.ui: self.ui.log("🚀 3-Thread Pipeline Started!", 'success')

    def stop(self):
        self.is_running = False
        if hasattr(self, 'audio'):
            self.audio.terminate()

    def speech_to_text_thread(self):
        """Thread 1: Listen -> Text -> Queue 1"""
        if self.ui: self.ui.log("🧠 Thread 1 (Listen) started", 'info')
        
        # Audio Capture Setup
        try:
            # Use user-selected device if available
            if self.device_index is not None:
                default_speakers = self.audio.get_device_info_by_index(self.device_index)
                if self.ui: self.ui.log(f"✅ Using selected device: {default_speakers['name']}", 'success')
            else:
                # Fallback: Auto-detect loopback device
                wasapi_info = self.audio.get_host_api_info_by_type(pyaudio.paWASAPI)
                default_speakers = self.audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
                
                # Debug: List all devices
                if self.ui:
                    self.ui.log(f"🔍 Scanning {self.audio.get_device_count()} devices...", 'info')
                    for i in range(self.audio.get_device_count()):
                        dev = self.audio.get_device_info_by_index(i)
                        is_loop = dev.get("isLoopbackDevice", False)
                        if is_loop: # Only log loopback candidates to reduce spam
                             self.ui.log(f"[{i}] {dev['name']} (In:{dev['maxInputChannels']}) Loopback: {is_loop}", 'info')

                if not default_speakers["isLoopbackDevice"]:
                    found_loopback = False
                    # 1. Try exact name match using indexed iteration
                    for i in range(self.audio.get_device_count()):
                        loopback = self.audio.get_device_info_by_index(i)
                        if loopback.get("isLoopbackDevice", False) and loopback["name"] == default_speakers["name"]:
                            default_speakers = loopback
                            found_loopback = True
                            if self.ui: self.ui.log(f"✅ Found exact loopback match: {loopback['name']}", 'success')
                            break
                    
                    # 2. Fallback: Find ANY loopback device
                    if not found_loopback:
                        if self.ui: self.ui.log("⚠️ Exact loopback match failed, using first available loopback.", 'warning')
                        for i in range(self.audio.get_device_count()):
                            loopback = self.audio.get_device_info_by_index(i)
                            if loopback.get("isLoopbackDevice", False):
                                default_speakers = loopback
                                found_loopback = True
                                if self.ui: self.ui.log(f"✅ Using loopback device: {loopback['name']}", 'success')
                                break
                
                if not default_speakers.get("isLoopbackDevice", False):
                     if self.ui: self.ui.log("❌ No Loopback device found!", 'error')
                     return
            
            if self.ui: self.ui.log(f"🎤 Device: {default_speakers['name']} (Channels: {default_speakers['maxInputChannels']})", 'info')
            
            # Try to open stream with fallback strategy
            stream = None
            try_channels = [
                int(default_speakers["maxInputChannels"]), # Native
                2, # Stereo
                1  # Mono
            ]
            
            # Remove duplicates and filter invalid
            try_channels = sorted(list(set([c for c in try_channels if c > 0])), reverse=True)
            
            for channels in try_channels:
                try:
                    if self.ui: self.ui.log(f"🔌 Trying to open with {channels} channels...", 'info')
                    stream = self.audio.open(format=self.format,
                                           channels=channels,
                                           rate=int(default_speakers["defaultSampleRate"]),
                                           input=True,
                                           input_device_index=default_speakers["index"],
                                           frames_per_buffer=self.chunk)
                    self.channels = channels # Update actual channels used
                    if self.ui: self.ui.log(f"✅ Success with {channels} channels!", 'success')
                    break
                except Exception as e:
                    if self.ui: self.ui.log(f"⚠️ Failed {channels} ch: {e}", 'warning')
            
            if stream is None:
                raise Exception("Could not open audio stream with any channel configuration.")
                
        except Exception as e:
            if self.ui: self.ui.log(f"❌ Audio Device Error: {e}", 'error')
            return

        if self.ui: self.ui.log(f"🎤 Listening on: {default_speakers['name']}", 'info')
        
        frames = []
        silence_threshold = 0.01
        min_audio_length = 1.0 # Reduce to 1.0s for faster response
        pause_time = 0.3 # Reduce to 0.3s for faster silence detection
        max_buffer_duration = 4.0 # Force processing after 4s even without silence
        last_speech_time = time.time()
        first_speech_time = None
        
        while self.is_running:
            try:
                data = stream.read(self.chunk)
                audio_np = np.frombuffer(data, dtype=np.float32)
                volume = np.abs(audio_np).mean()
                
                if volume > silence_threshold:
                    if first_speech_time is None:
                        first_speech_time = time.time()
                    frames.append(audio_np)
                    last_speech_time = time.time()
                    
                    # Force processing if buffer is too long
                    buffer_duration = time.time() - first_speech_time
                    if buffer_duration > max_buffer_duration:
                        if self.ui: self.ui.log(f"⏱️ Max buffer reached ({buffer_duration:.1f}s), processing...", 'info')
                        # Process immediately
                        if len(frames) > 0:
                            self._process_audio_buffer(frames, default_speakers, first_speech_time)
                            frames = []
                            first_speech_time = None
                            
                elif frames:
                    # Silence detected
                    if time.time() - last_speech_time > pause_time:
                        duration = (time.time() - first_speech_time) if first_speech_time else 0
                        if duration > min_audio_length:
                            self._process_audio_buffer(frames, default_speakers, first_speech_time)
                        frames = []
                        first_speech_time = None
                        
            except Exception as e:
                if self.ui: self.ui.log(f"⚠️ Audio error: {e}", 'warning')
    
    def _process_audio_buffer(self, frames, device_info, start_time):
        """Helper method to process accumulated audio frames"""
        try:
            audio_float = np.concatenate(frames)
            sample_rate = int(device_info["defaultSampleRate"])
            duration = len(audio_float) / sample_rate
            
            # Downmix stereo to mono for Whisper
            if device_info["maxInputChannels"] == 2:
                # Reshape to (samples, 2) and average channels
                audio_float = audio_float.reshape(-1, 2).mean(axis=1)
            
            # Ensure audio is in valid range [-1, 1]
            max_val = np.abs(audio_float).max()
            if max_val > 1.0:
                audio_float = audio_float / max_val
            
            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                if self.ui: self.ui.log(f"🔄 Resampling from {sample_rate}Hz to 16000Hz", 'info')
                # Simple resampling using numpy
                target_length = int(len(audio_float) * 16000 / sample_rate)
                audio_float = np.interp(
                    np.linspace(0, len(audio_float), target_length),
                    np.arange(len(audio_float)),
                    audio_float
                )
            
            if self.ui: self.ui.log(f"🎧 Processing {duration:.1f}s audio ({len(audio_float)} samples @ 16kHz, max: {max_val:.3f})", 'info')
            
            segments, info = self.whisper_model.transcribe(
                audio_float, 
                beam_size=5, 
                language='zh',
                vad_filter=False,  # Disable VAD temporarily to debug
                no_speech_threshold=0.6
            )
            
            segment_list = list(segments)
            if self.ui: self.ui.log(f"📊 Whisper found {len(segment_list)} segments", 'info')
            
            text = " ".join([s.text for s in segment_list]).strip()
            
            if text:
                if self.ui: self.ui.log(f"🗣️ Heard: {text}", 'chinese')
                self.trans_queue.put(text)
            else:
                if self.ui: self.ui.log(f"⚠️ No text detected in {duration:.1f}s audio (lang: {info.language}, prob: {info.language_probability:.2f})", 'warning')
                
        except Exception as e:
            if self.ui: self.ui.log(f"❌ Processing error: {e}", 'error')
            import traceback
            if self.ui: self.ui.log(f"Stack: {traceback.format_exc()}", 'error')

    def translation_thread(self):
        """Thread 2: Queue 1 -> Translate -> Queue 2"""
        if self.ui: self.ui.log("🌍 Thread 2 (Translate) started", 'info')
        
        while self.is_running:
            try:
                text = self.trans_queue.get(timeout=0.5)
                
                translated = self.translator.translate(text)
                if translated:
                    if self.ui: self.ui.log(f"✅ Trans: {translated}", 'vietnamese')
                    self.tts_queue.put(translated)
                    
                self.trans_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.ui: self.ui.log(f"❌ Trans Error: {e}", 'error')

    def output_thread(self):
        """Thread 3: Queue 2 -> Speak (Direct)"""
        if self.ui: self.ui.log("🔊 Thread 3 (Output) started", 'info')
        
        while self.is_running:
            try:
                text = self.tts_queue.get(timeout=0.5)
                
                if self.ui: self.ui.log(f"▶️ Speaking: {text[:20]}...", 'info')
                self.tts_engine.speak(text)
                
                self.tts_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.ui: self.ui.log(f"❌ Output Error: {e}", 'error')

class AudioTranslatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Real-time Audio Translator - Chinese to Vietnamese")
        self.root.geometry("900x750")
        self.root.configure(bg=Config.COLORS['bg'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.is_running = False
        self.translator_engine = None
        self.audio = pyaudio.PyAudio()
        
        self.create_ui()
        self.load_audio_devices()
        self.check_gpu()
    
    def create_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=Config.COLORS['bg'], foreground=Config.COLORS['fg'])
        
        header = ttk.Label(self.root, text="🎙️ Real-time Audio Translator", font=('Arial', 14, 'bold'))
        header.pack(pady=10)
        
        settings_frame = ttk.LabelFrame(self.root, text="⚙️ Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Audio Device
        ttk.Label(settings_frame, text="🎤 Audio Device:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.device_combo = ttk.Combobox(settings_frame, width=40, state='readonly')
        self.device_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Model
        ttk.Label(settings_frame, text="🤖 Whisper Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_combo = ttk.Combobox(settings_frame, values=Config.WHISPER_MODELS, state='readonly', width=15)
        self.model_combo.set(Config.DEFAULTS['model'])
        self.model_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Compute
        ttk.Label(settings_frame, text="⚡ Compute:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.compute_combo = ttk.Combobox(settings_frame, values=Config.COMPUTE_TYPES, state='readonly', width=15)
        self.compute_combo.set(Config.DEFAULTS['compute_type'])
        self.compute_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # TTS Engine
        ttk.Label(settings_frame, text="🔊 TTS Engine:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tts_engine_var = tk.StringVar(value='edge')
        tts_frame = ttk.Frame(settings_frame)
        tts_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        for mode_key, mode_info in Config.TTS_MODES.items():
            ttk.Radiobutton(tts_frame, text=mode_info['display'], variable=self.tts_engine_var, value=mode_key).pack(anchor=tk.W)
        
        # Sliders
        self.create_sliders(settings_frame)
        
        # GPU Info
        self.gpu_label = ttk.Label(settings_frame, text="🔍 Checking GPU...")
        self.gpu_label.grid(row=20, column=0, columnspan=2, pady=5)
        
        # Controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶️ Start", command=self.start_translation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop", command=self.stop_translation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.latency_label = ttk.Label(control_frame, text="⏱️ Latency: -- ms", font=('Arial', 11, 'bold'))
        self.latency_label.pack(side=tk.LEFT, padx=20)
        
        # Log
        log_frame = ttk.LabelFrame(self.root, text="📝 Translation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#1e1e1e', fg=Config.COLORS['success'], font=('Consolas', 9), height=12, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_config('chinese', foreground=Config.COLORS['chinese'])
        self.log_text.tag_config('vietnamese', foreground=Config.COLORS['vietnamese'])
        self.log_text.tag_config('info', foreground=Config.COLORS['info'])
        self.log_text.tag_config('error', foreground=Config.COLORS['error'])
        self.log_text.tag_config('success', foreground=Config.COLORS['success'])
        self.log_text.tag_config('warning', foreground='orange')

    def create_sliders(self, parent):
        row = 4
        
        # Beam Size
        ttk.Label(parent, text="🎯 Beam Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.beam_scale = tk.Scale(parent, from_=1, to=10, orient=tk.HORIZONTAL, bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.beam_scale.set(Config.DEFAULTS['beam_size'])
        self.beam_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Silence Threshold
        ttk.Label(parent, text="🔇 Silence:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.threshold_scale = tk.Scale(parent, from_=100, to=2000, orient=tk.HORIZONTAL, bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.threshold_scale.set(Config.DEFAULTS['silence_threshold'])
        self.threshold_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # TTS Speed
        ttk.Label(parent, text="🗣️ TTS Speed:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tts_scale = tk.Scale(parent, from_=100, to=250, orient=tk.HORIZONTAL, bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.tts_scale.set(Config.DEFAULTS['tts_speed'])
        self.tts_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Pause Time
        ttk.Label(parent, text="⏸️ Pause (s):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.pause_scale = tk.Scale(parent, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.pause_scale.set(Config.DEFAULTS['pause_time'])
        self.pause_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Min Audio
        ttk.Label(parent, text="⏱️ Min Audio (s):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.min_audio_scale = tk.Scale(parent, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.min_audio_scale.set(Config.DEFAULTS['min_audio_length'])
        self.min_audio_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Padding Words
        ttk.Label(parent, text="🔧 Padding (số từ):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.padding_scale = tk.Scale(parent, from_=0, to=5, resolution=1, orient=tk.HORIZONTAL, bg=Config.COLORS['bg'], fg=Config.COLORS['fg'], command=self.on_padding_change)
        self.padding_scale.set(Config.DEFAULTS.get('padding_words', 1))
        self.padding_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Padding Word Text
        ttk.Label(parent, text="📝 Từ đệm:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.padding_word_var = tk.StringVar(value=Config.DEFAULTS.get('padding_word', 'ừm'))
        self.padding_word_var.trace('w', self.on_padding_change)
        self.padding_word_entry = ttk.Entry(parent, width=20, textvariable=self.padding_word_var)
        self.padding_word_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)

    def on_padding_change(self, *args):
        if self.translator_engine and hasattr(self.translator_engine, 'tts_engine'):
            try:
                word = self.padding_word_var.get()
                count = self.padding_scale.get()
                self.translator_engine.tts_engine.update_padding(word, count)
            except:
                pass

    def load_audio_devices(self):
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            # Only show Loopback devices for system audio capture
            if info.get('isLoopbackDevice', False):
                devices.append(f"{i}: {info['name']}")
        self.device_combo['values'] = devices
        if devices:
            self.device_combo.current(0)

    def check_gpu(self):
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            self.gpu_label.config(text=f"✅ GPU: {gpu_name}")
        else:
            self.gpu_label.config(text="⚠️ No GPU - Using CPU")

    def start_translation(self):
        if self.is_running: return
        
        device_idx = int(self.device_combo.get().split(':')[0])
        settings = {
            'model': self.model_combo.get(),
            'compute_type': self.compute_combo.get(),
            'beam_size': self.beam_scale.get(),
            'silence_threshold': self.threshold_scale.get(),
            'tts_speed': self.tts_scale.get(),
            'device_index': device_idx,
            'tts_engine': self.tts_engine_var.get(),
            'pause_time': self.pause_scale.get(),
            'min_audio_length': self.min_audio_scale.get(),
            'padding_words': self.padding_scale.get(),
            'padding_word': self.padding_word_entry.get()
        }
        
        self.start_btn.config(state=tk.DISABLED)
        self.log("⏳ Initializing...", 'warning')
        
        def init_and_start():
            try:
                self.translator_engine = TranslatorEngine(settings, self)
                self.translator_engine.start()
                self.root.after(0, lambda: self._on_start_success())
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ Error: {e}", 'error'))
                self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
        
        threading.Thread(target=init_and_start, daemon=True).start()

    def _on_start_success(self):
        self.is_running = True
        self.stop_btn.config(state=tk.NORMAL)

    def stop_translation(self):
        if not self.is_running: return
        if self.translator_engine:
            self.translator_engine.stop()
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("⏹️ Stopped!", 'info')

    def on_closing(self):
        if self.is_running:
            self.stop_translation()
        self.root.destroy()
        sys.exit(0)

    def log(self, message, tag='info'):
        try:
            if self.root.winfo_exists():
                self.log_text.insert(tk.END, message + '\n', tag)
                self.log_text.see(tk.END)
        except: pass

    def update_latency(self, latency):
        try:
            if self.root.winfo_exists():
                self.latency_label.config(text=f"⏱️ Latency: {latency:.0f} ms")
        except: pass

def main():
    root = tk.Tk()
    app = AudioTranslatorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
