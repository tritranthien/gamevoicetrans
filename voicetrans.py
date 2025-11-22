"""
Real-time Audio Translator - Chinese to Vietnamese
With Gender Detection & Configurable Padding
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

# Import our modules
from tts_engine import TTSEngine
from audio_utils import AudioUtils
from config import Config


class TranslatorEngine:
    def __init__(self, settings, ui):
        self.settings = settings
        self.ui = ui
        self.is_running = False
        self.is_tts_playing = False
        
        self.audio = pyaudio.PyAudio()
        self.chunk = Config.AUDIO['chunk_size']
        self.format = pyaudio.paInt16
        
        device_info = self.audio.get_device_info_by_index(settings['device_index'])
        self.device_rate = int(device_info['defaultSampleRate'])
        self.channels = min(int(device_info['maxInputChannels']), 2)
        self.rate = self.device_rate
        self.whisper_rate = Config.AUDIO['whisper_rate']
        
        self.audio_queue = queue.Queue(maxsize=10)
        self.text_queue = queue.Queue(maxsize=10)
        self.translation_queue = queue.Queue(maxsize=10)
        
        self.pause_time = settings.get('pause_time', 0.5)
        self.min_audio_length = settings.get('min_audio_length', 1.0)
        
        # Load Whisper
        self.ui.log(f"🔄 Loading Whisper model: {settings['model']}...", 'info')
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = WhisperModel(
            settings['model'],
            device=device,
            compute_type=settings['compute_type']
        )
        self.ui.log(f"✅ Whisper loaded on {device.upper()}", 'info')
        
        self.translator = GoogleTranslator(source='zh-CN', target='vi')
        
        # TTS Engine with padding
        self.tts_engine = TTSEngine(
            mode=settings.get('tts_engine', 'edge'),
            ui=ui,
            settings=settings
        )
    
    def start(self):
        self.is_running = True
        threading.Thread(target=self.audio_capture_thread, daemon=True).start()
        threading.Thread(target=self.speech_to_text_thread, daemon=True).start()
        threading.Thread(target=self.translation_thread, daemon=True).start()
        threading.Thread(target=self.tts_thread, daemon=True).start()
    
    def stop(self):
        self.is_running = False
        time.sleep(0.5)
    
    def audio_capture_thread(self):
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
        
        pause_frames = int(self.rate / self.chunk * self.pause_time)
        min_audio_frames = int(self.rate / self.chunk * self.min_audio_length)
        
        while self.is_running:
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                
                if self.is_tts_playing:
                    if buffer:
                        buffer = []
                        silence_counter = 0
                        is_speaking = False
                    continue
                
                rms = AudioUtils.calculate_rms(data)
                
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
                        
                        if silence_counter > pause_frames:
                            if len(buffer) > min_audio_frames:
                                audio_data = b''.join(buffer)
                                if not self.audio_queue.full():
                                    self.audio_queue.put(audio_data)
                            
                            buffer = []
                            silence_counter = 0
                            is_speaking = False
                            
            except:
                break
        
        stream.stop_stream()
        stream.close()
    
    def speech_to_text_thread(self):
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                start_time = time.time()
                
                resampled_data = AudioUtils.resample_audio(
                    audio_data, self.device_rate, self.whisper_rate, self.channels
                )
                audio_array = np.frombuffer(resampled_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                gender = AudioUtils.detect_gender(audio_array, self.whisper_rate)
                
                segments, info = self.whisper_model.transcribe(
                    audio_array,
                    language="zh",
                    beam_size=self.settings['beam_size'],
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=100),
                    no_speech_threshold=0.6
                )
                
                transcript = " ".join([segment.text for segment in segments])
                stt_time = (time.time() - start_time) * 1000
                
                if transcript.strip():
                    gender_icon = AudioUtils.get_gender_icon(gender)
                    self.ui.log(f"🇨🇳 {gender_icon} [{stt_time:.0f}ms] {transcript}", 'chinese')
                    self.text_queue.put((transcript, time.time(), gender))
                
            except queue.Empty:
                continue
            except Exception as e:
                self.ui.log(f"❌ STT Error: {str(e)}", 'error')
    
    def translation_thread(self):
        while self.is_running:
            try:
                text, start_time, gender = self.text_queue.get(timeout=1)
                translated = self.translator.translate(text)
                trans_time = (time.time() - start_time) * 1000
                self.ui.log(f"🇻🇳 [{trans_time:.0f}ms] {translated}", 'vietnamese')
                self.translation_queue.put((translated, start_time, gender))
            except queue.Empty:
                continue
            except Exception as e:
                self.ui.log(f"❌ Translation Error: {str(e)}", 'error')
    
    def tts_thread(self):
        while self.is_running:
            try:
                text, start_time, gender = self.translation_queue.get(timeout=1)
                self.is_tts_playing = True
                self.tts_engine.speak(text, gender)
                self.is_tts_playing = False
                total_time = (time.time() - start_time) * 1000
                self.ui.log(f"✅ Total: {total_time:.0f}ms\n{'='*50}", 'info')
                self.ui.update_latency(total_time)
            except queue.Empty:
                continue
            except Exception as e:
                self.is_tts_playing = False
                self.ui.log(f"❌ TTS Error: {str(e)}", 'error')


class AudioTranslatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Real-time Audio Translator - Chinese to Vietnamese")
        self.root.geometry("900x750")
        self.root.configure(bg=Config.COLORS['bg'])
        
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
        
        # Header
        header = ttk.Label(self.root, text="🎙️ Real-time Audio Translator", 
                          font=('Arial', 14, 'bold'))
        header.pack(pady=10)
        
        # Settings
        settings_frame = ttk.LabelFrame(self.root, text="⚙️ Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Audio Device
        ttk.Label(settings_frame, text="🎤 Audio Device:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.device_combo = ttk.Combobox(settings_frame, width=40, state='readonly')
        self.device_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Model
        ttk.Label(settings_frame, text="🤖 Whisper Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_combo = ttk.Combobox(settings_frame, values=Config.WHISPER_MODELS, 
                                       state='readonly', width=15)
        self.model_combo.set(Config.DEFAULTS['model'])
        self.model_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Compute
        ttk.Label(settings_frame, text="⚡ Compute:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.compute_combo = ttk.Combobox(settings_frame, values=Config.COMPUTE_TYPES,
                                         state='readonly', width=15)
        self.compute_combo.set(Config.DEFAULTS['compute_type'])
        self.compute_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # TTS Engine
        ttk.Label(settings_frame, text="🔊 TTS Engine:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tts_engine_var = tk.StringVar(value='edge')
        tts_frame = ttk.Frame(settings_frame)
        tts_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        for mode_key, mode_info in Config.TTS_MODES.items():
            ttk.Radiobutton(tts_frame, text=mode_info['display'],
                          variable=self.tts_engine_var, value=mode_key).pack(anchor=tk.W)
        
        # Sliders
        self.create_sliders(settings_frame)
        
        # GPU Info
        self.gpu_label = ttk.Label(settings_frame, text="🔍 Checking GPU...")
        self.gpu_label.grid(row=10, column=0, columnspan=2, pady=5)
        
        # Controls
        self.create_controls()
        
        # Log
        self.create_log_area()
    
    def create_sliders(self, parent):
        row = 4
        
        # Beam Size
        ttk.Label(parent, text="🎯 Beam Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.beam_scale = tk.Scale(parent, from_=1, to=10, orient=tk.HORIZONTAL, 
                                   bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.beam_scale.set(Config.DEFAULTS['beam_size'])
        self.beam_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Silence Threshold
        ttk.Label(parent, text="🔇 Silence:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.threshold_scale = tk.Scale(parent, from_=100, to=2000, orient=tk.HORIZONTAL,
                                       bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.threshold_scale.set(Config.DEFAULTS['silence_threshold'])
        self.threshold_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # TTS Speed
        ttk.Label(parent, text="🗣️ TTS Speed:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tts_scale = tk.Scale(parent, from_=100, to=250, orient=tk.HORIZONTAL,
                                 bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.tts_scale.set(Config.DEFAULTS['tts_speed'])
        self.tts_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Pause Time
        ttk.Label(parent, text="⏸️ Pause (s):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.pause_scale = tk.Scale(parent, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                   bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.pause_scale.set(Config.DEFAULTS['pause_time'])
        self.pause_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Min Audio
        ttk.Label(parent, text="⏱️ Min Audio (s):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.min_audio_scale = tk.Scale(parent, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL,
                                       bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.min_audio_scale.set(Config.DEFAULTS['min_audio_length'])
        self.min_audio_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1
        
        # Padding Words (NEW!)
        ttk.Label(parent, text="🔧 Padding (từ 'ừ'):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.padding_scale = tk.Scale(parent, from_=0, to=5, resolution=1, orient=tk.HORIZONTAL,
                                     bg=Config.COLORS['bg'], fg=Config.COLORS['fg'])
        self.padding_scale.set(Config.DEFAULTS.get('padding_words', 1))
        self.padding_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
    
    def create_controls(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶️ Start", command=self.start_translation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop", command=self.stop_translation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.latency_label = ttk.Label(control_frame, text="⏱️ Latency: -- ms", font=('Arial', 11, 'bold'))
        self.latency_label.pack(side=tk.LEFT, padx=20)
    
    def create_log_area(self):
        log_frame = ttk.LabelFrame(self.root, text="📝 Translation Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#1e1e1e', fg=Config.COLORS['success'],
                                                 font=('Consolas', 9), height=12, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_config('chinese', foreground=Config.COLORS['chinese'])
        self.log_text.tag_config('vietnamese', foreground=Config.COLORS['vietnamese'])
        self.log_text.tag_config('info', foreground=Config.COLORS['info'])
        self.log_text.tag_config('error', foreground=Config.COLORS['error'])
    
    def load_audio_devices(self):
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
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
            'padding_words': self.padding_scale.get()  # NEW!
        }
        
        self.translator_engine = TranslatorEngine(settings, self)
        self.translator_engine.start()
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.log("🚀 Translation started!", 'info')
    
    def stop_translation(self):
        if self.translator_engine:
            self.translator_engine.stop()
        
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.log("⏹️ Translation stopped!", 'info')
    
    def log(self, message, tag='info'):
        self.log_text.insert(tk.END, message + '\n', tag)
        self.log_text.see(tk.END)
    
    def update_latency(self, latency_ms):
        self.latency_label.config(text=f"⏱️ Latency: {latency_ms:.0f} ms")


def main():
    print("=" * 50)
    print("Real-time Audio Translator")
    print("With Gender Detection & Padding")
    print("=" * 50)
    print("🚀 Starting...")
    
    root = tk.Tk()
    app = AudioTranslatorUI(root)
    
    print("✅ Ready!")
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
