"""
TTS Engine - OPTIMIZED VERSION
- Padding: 1 từ "ừ"
- Normalize punctuation: . ! ? ; : → ,
- OPTIMIZED: Cache regex, faster processing
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
        
        # Pre-create padding string (faster!)
        self._padding_cache = self._create_padding()
        
        if mode in ['edge', 'gtts']:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            except:
                pass
        
        if mode == 'edge':
            self._init_edge_tts()
        elif mode == 'gtts':
            self._init_google_tts()
        else:
            self._init_pyttsx3()
    
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
        """Initialize pyttsx3"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.settings.get('tts_speed', 150))
            self.tts_engine.setProperty('volume', 1.0)
            
            voices = self.tts_engine.getProperty('voices')
            self.selected_voice_id = None
            
            for voice in voices:
                name_lower = voice.name.lower()
                id_lower = voice.id.lower()
                
                if any(x in name_lower or x in id_lower for x in ['vietnam', 'việt', 'viet', 'vi-', 'vivn']):
                    self.selected_voice_id = voice.id
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            if not self.selected_voice_id and voices:
                self.selected_voice_id = voices[0].id
                self.tts_engine.setProperty('voice', voices[0].id)
                    
        except Exception as e:
            self.tts_engine = None
    
    def _create_padding(self):
        """Tạo padding text"""
        if self.padding_words <= 0:
            return ""
        
        # Dùng dấu phẩy (pause ngắn)
        padding = " ".join([self.padding_word] * self.padding_words) + ", "
        return padding
    
    def _normalize_punctuation(self, text):
        """Thay tất cả dấu ngắt câu thành dấu phẩy (OPTIMIZED)"""
        # Use pre-compiled regex (faster!)
        text = self.PUNCT_PATTERN.sub(',', text)
        text = self.COMMA_PATTERN.sub(',', text)
        return text.strip(',').strip()
    
    def speak(self, text, gender='female'):
        """Speak the given text"""
        with self.lock:
            self.is_playing = True
            
            try:
                # Normalize punctuation (fast!)
                text = self._normalize_punctuation(text)
                
                if self.mode == 'edge':
                    self._speak_edge(text, gender)
                elif self.mode == 'gtts':
                    self._speak_google(text)
                else:
                    self._speak_pyttsx3(text)
            finally:
                self.is_playing = False
    
    def _speak_edge(self, text, gender='female'):
        """Speak using Edge TTS"""
        try:
            voice = self.edge_voice_male if gender == 'male' else self.edge_voice_female
            
            # Use cached padding (faster!)
            padded_text = self._padding_cache + text
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            async def generate():
                communicate = edge_tts.Communicate(padded_text, voice)
                await communicate.save(temp_file)
            
            asyncio.run(generate())
            
            # Play
            sound = pygame.mixer.Sound(temp_file)
            sound.set_volume(1.0)
            
            try:
                os.unlink(temp_file)
            except:
                pass
            
            sound.play()
            
            while pygame.mixer.get_busy():
                time.sleep(0.05)
                
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Edge TTS error: {str(e)}", 'error')
    
    def _speak_google(self, text):
        """Speak using Google TTS"""
        try:
            padded_text = self._padding_cache + text
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            tts = gTTS(text=padded_text, lang='vi', slow=False, timeout=3)
            tts.save(temp_file)
            
            sound = pygame.mixer.Sound(temp_file)
            sound.set_volume(1.0)
            
            try:
                os.unlink(temp_file)
            except:
                pass
            
            sound.play()
            
            while pygame.mixer.get_busy():
                time.sleep(0.05)
                
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Google TTS error: {str(e)}", 'error')
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        if not self.tts_engine:
            return
        
        try:
            temp_engine = pyttsx3.init()
            temp_engine.setProperty('rate', self.settings.get('tts_speed', 150))
            temp_engine.setProperty('volume', 1.0)
            
            if self.selected_voice_id:
                temp_engine.setProperty('voice', self.selected_voice_id)
            
            temp_engine.say(text)
            temp_engine.runAndWait()
            
            del temp_engine
            
        except Exception as e:
            pass
