"""
TTS Engine - OPTIMIZED VERSION
- Padding: 1 từ "ừ"
- Normalize punctuation: . ! ? ; : → ,
- OPTIMIZED: Cache regex, faster processing
- Added generate_audio for gapless playback
"""
import pyttsx3
from gtts import gTTS
import edge_tts
import asyncio
import pygame
import tempfile
import os
import time
import threading
import re

class TTSEngine:
    # Compile regex once (faster!)
    PUNCT_PATTERN = re.compile(r'[.!?;:]')
    COMMA_PATTERN = re.compile(r',+')
    
    def __init__(self, mode='edge', ui=None, settings=None):
        """Initialize TTS Engine"""
        self.mode = mode
        self.ui = ui
        self.settings = settings or {}
        self.lock = threading.Lock()
        self.is_playing = False
        
        # Padding: 1 từ "ừ"
        self.padding_words = self.settings.get('padding_words', 1)
        self.padding_word = self.settings.get('padding_word', 'ừ')
        
        # Track last playback time for smart padding
        self.last_playback_time = 0
        
        # Pre-create padding string (faster!)
        self._padding_cache = self._create_padding()
        
        # Always initialize mixer for playback (even for pyttsx3)
        self._ensure_mixer_init()
        
        if mode == 'edge':
            self._init_edge_tts()
        elif mode == 'gtts':
            self._init_google_tts()
        else:
            self._init_pyttsx3()
    
    def _ensure_mixer_init(self):
        """Ensure pygame mixer is initialized"""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=1024)
                if self.ui: self.ui.log("✅ Audio Mixer Initialized", 'info')
            except Exception as e:
                if self.ui: self.ui.log(f"⚠️ Mixer Init Failed: {e}", 'warning')

    def _init_edge_tts(self):
        """Initialize Edge TTS"""
        self.edge_voice_male = "vi-VN-NamMinhNeural"
        self.edge_voice_female = "vi-VN-HoaiMyNeural"
        
        if self.ui:
            self.ui.log("✅ Edge TTS initialized", 'info')
            self.ui.log(f"   🔧 Padding: {self.padding_words} x '{self.padding_word}'", 'info')
    
    def _init_google_tts(self):
        """Initialize Google TTS"""
        if self.ui:
            self.ui.log("✅ Google TTS initialized", 'info')
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 settings (Engine init is delayed)"""
        if self.ui:
            self.ui.log("✅ pyttsx3 (Offline) mode selected", 'info')

    def _create_padding(self):
        """Tạo padding text"""
        if self.padding_words <= 0:
            return ""
        
        # Dùng dấu phẩy (pause ngắn)
        padding = " ".join([self.padding_word] * self.padding_words) + ", "
        return padding

    def update_padding(self, word, count):
        """Update padding settings dynamically"""
        self.padding_word = word
        self.padding_words = count
        self._padding_cache = self._create_padding()
        if self.ui:
            self.ui.log(f"🔄 Updated padding: {count} x '{word}'", 'info')
    
    def _normalize_punctuation(self, text):
        """Thay tất cả dấu ngắt câu thành dấu phẩy (OPTIMIZED)"""
        # Use pre-compiled regex (faster!)
        text = self.PUNCT_PATTERN.sub(',', text)
        text = self.COMMA_PATTERN.sub(',', text)
        return text.strip(',').strip()

    def generate_audio(self, text, gender='female'):
        """
        Generate audio bytes for the given text
        Smart Padding: Only add padding if silence > 2s
        """
        if not text:
            return None
            
        # Check time since last playback
        current_time = time.time()
        time_since_last = current_time - self.last_playback_time
        
        # Determine if we need padding
        need_padding = time_since_last > 2.0
        
        # Update last playback time
        self.last_playback_time = current_time
        
        # Prepare text (handle word padding here)
        final_text = text
        
        if need_padding:
            # Use padding word if available, otherwise default to "Dạ vâng" if empty
            padding = self.padding_word if self.padding_word and self.padding_word.strip() else "Dạ vâng"
            final_text = f"{padding} {text}"
            if self.ui: self.ui.log(f"➕ Smart Padding: '{padding}'", 'info')

        try:
            # Generate main audio
            audio_data = None
            if self.mode == 'edge':
                audio_data = self._generate_edge_audio(final_text, gender)
            elif self.mode == 'gtts':
                audio_data = self._generate_gtts_audio(final_text)
            else:
                audio_data = self._generate_pyttsx3_audio(final_text)
            
            if not audio_data:
                return None

            # Return list for compatibility with voicetrans.py
            return [audio_data]
            
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Audio generation error: {str(e)}", 'error')
            return None

    def _generate_edge_audio(self, text, gender):
        """Generate audio bytes using Edge TTS"""
        voice = self.edge_voice_male if gender == 'male' else self.edge_voice_female
        
        speed = self.settings.get('tts_speed', 150)
        rate_str = f"{'+' if speed >= 100 else ''}{speed - 100}%"
        
        temp_file = os.path.join(tempfile.gettempdir(), f"tts_{int(time.time()*1000)}.mp3")
        
        async def generate():
            communicate = edge_tts.Communicate(text, voice, rate=rate_str)
            await communicate.save(temp_file)
        
        try:
            asyncio.run(generate())
            
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
                
            try:
                os.unlink(temp_file)
            except:
                pass
                
            return audio_data
        except Exception as e:
            raise e

    def _generate_gtts_audio(self, text):
        """Generate audio bytes using gTTS"""
        tts = gTTS(text=text, lang='vi')
        
        temp_file = os.path.join(tempfile.gettempdir(), f"gtts_{int(time.time()*1000)}.mp3")
        tts.save(temp_file)
        
        with open(temp_file, 'rb') as f:
            audio_data = f.read()
            
        try:
            os.unlink(temp_file)
        except:
            pass
            
        return audio_data

    def _generate_pyttsx3_audio(self, text):
        """Generate audio bytes using pyttsx3 (Thread-Safe)"""
        temp_file = os.path.join(tempfile.gettempdir(), f"pyttsx3_{int(time.time()*1000)}.wav")
        
        try:
            # Initialize engine LOCALLY to avoid threading issues
            engine = pyttsx3.init()
            engine.setProperty('rate', self.settings.get('tts_speed', 150))
            engine.setProperty('volume', 1.0)
            
            # Select Voice
            voices = engine.getProperty('voices')
            selected_voice_id = None
            for voice in voices:
                name_lower = voice.name.lower()
                id_lower = voice.id.lower()
                if any(x in name_lower or x in id_lower for x in ['vietnam', 'việt', 'viet', 'vi-', 'vivn']):
                    selected_voice_id = voice.id
                    break
            
            if selected_voice_id:
                engine.setProperty('voice', selected_voice_id)
            
            # Generate
            engine.save_to_file(text, temp_file)
            engine.runAndWait()
            
            # Read file
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                with open(temp_file, 'rb') as f:
                    audio_data = f.read()
            else:
                audio_data = None
                
        except Exception as e:
            if self.ui: self.ui.log(f"⚠️ pyttsx3 Error: {e}", 'warning')
            audio_data = None
        finally:
            # Cleanup temp file
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
            
        return audio_data

    def speak(self, text, gender='female'):
        """
        Direct Speak Method (For Thread 3)
        Handles both generation and playback synchronously.
        """
        if not text: return

        # Smart Padding (Simple)
        current_time = time.time()
        if current_time - self.last_playback_time > 2.0:
             padding = self.padding_word if self.padding_word else ""
             if padding:
                 text = f"{padding} {text}"
                 if self.ui: self.ui.log(f"➕ Padding: '{padding}'", 'info')
        self.last_playback_time = current_time

        try:
            if self.mode == 'pyttsx3':
                self._speak_pyttsx3(text)
            else:
                # Edge / gTTS (File based)
                audio_data = self.generate_audio(text, gender)
                if audio_data:
                    # generate_audio returns list, take first item
                    data = audio_data[0] if isinstance(audio_data, list) else audio_data
                    self._play_with_pygame(data)
        except Exception as e:
            if self.ui: self.ui.log(f"❌ Speak Error: {e}", 'error')

    def _speak_pyttsx3(self, text):
        """Direct speak using pyttsx3 (No temp files)"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.settings.get('tts_speed', 150))
            engine.setProperty('volume', 1.0)
            
            # Select Voice
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'viet' in voice.name.lower() or 'vivn' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            if self.ui: self.ui.log(f"⚠️ pyttsx3 Error: {e}", 'warning')

    def _play_with_pygame(self, audio_data):
        """Simple Pygame Playback"""
        self._ensure_mixer_init()
        try:
            # Detect format
            ext = ".wav" if audio_data[:4] == b'RIFF' else ".mp3"
            temp_file = os.path.join(tempfile.gettempdir(), f"play_{int(time.time()*1000)}_{threading.get_ident()}{ext}")
            
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish (Blocking)
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            try:
                os.unlink(temp_file)
            except:
                pass
        except Exception as e:
            if self.ui: self.ui.log(f"❌ Pygame Error: {e}", 'error')

    # Remove old complex playback methods
    def play_audio_data(self, audio_data):
        pass
    def cleanup_files(self):
        pass
