"""
TTS Engine Module - Handles all Text-to-Speech functionality
Supports: pyttsx3, Google TTS, Edge TTS
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


class TTSEngine:
    def __init__(self, mode='edge', ui=None, settings=None):
        """
        Initialize TTS Engine
        
        Args:
            mode: 'pyttsx3', 'gtts', or 'edge'
            ui: UI instance for logging
            settings: Dict with TTS settings
        """
        self.mode = mode
        self.ui = ui
        self.settings = settings or {}
        self.lock = threading.Lock()
        self.is_playing = False
        
        # Initialize based on mode
        if mode == 'edge':
            self._init_edge_tts()
        elif mode == 'gtts':
            self._init_google_tts()
        else:  # pyttsx3
            self._init_pyttsx3()
    
    def _init_edge_tts(self):
        """Initialize Edge TTS"""
        try:
            pygame.mixer.init()
            self.edge_voice = "vi-VN-HoaiMyNeural"  # Female voice
            self.edge_voice_male = "vi-VN-NamMinhNeural"  # Male voice
            self.edge_voice_female = "vi-VN-HoaiMyNeural"  # Female voice
            
            if self.ui:
                self.ui.log("✅ Edge TTS initialized (Microsoft Neural Voices)", 'info')
                self.ui.log("   Female: HoaiMyNeural | Male: NamMinhNeural", 'info')
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Edge TTS init error: {str(e)}", 'error')
    
    def _init_google_tts(self):
        """Initialize Google TTS"""
        try:
            pygame.mixer.init()
            if self.ui:
                self.ui.log("✅ Google TTS initialized", 'info')
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Google TTS init error: {str(e)}", 'error')
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.settings.get('tts_speed', 150))
            self.tts_engine.setProperty('volume', 1.0)
            
            # Find Vietnamese voice
            voices = self.tts_engine.getProperty('voices')
            self.selected_voice_id = None
            
            for voice in voices:
                name_lower = voice.name.lower()
                id_lower = voice.id.lower()
                
                if any(x in name_lower or x in id_lower for x in ['vietnam', 'việt', 'viet', 'vi-', 'vivn']):
                    self.selected_voice_id = voice.id
                    self.tts_engine.setProperty('voice', voice.id)
                    if self.ui:
                        self.ui.log(f"✅ Using Vietnamese voice: {voice.name}", 'info')
                    break
            
            if not self.selected_voice_id and voices:
                self.selected_voice_id = voices[0].id
                self.tts_engine.setProperty('voice', voices[0].id)
                if self.ui:
                    self.ui.log(f"⚠️ No Vietnamese voice found, using: {voices[0].name}", 'info')
                    
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ pyttsx3 init error: {str(e)}", 'error')
            self.tts_engine = None
    
    def speak(self, text, gender='female'):
        """
        Speak the given text
        
        Args:
            text: Text to speak
            gender: 'male' or 'female' (for Edge TTS)
        """
        with self.lock:
            self.is_playing = True
            
            try:
                if self.mode == 'edge':
                    self._speak_edge(text, gender)
                elif self.mode == 'gtts':
                    self._speak_google(text)
                else:  # pyttsx3
                    self._speak_pyttsx3(text)
            finally:
                self.is_playing = False
    
    def _speak_edge(self, text, gender='female'):
        """Speak using Edge TTS"""
        try:
            start_time = time.time()
            
            # Select voice based on gender
            voice = self.edge_voice_male if gender == 'male' else self.edge_voice_female
            voice_name = "NamMinh (Male)" if gender == 'male' else "HoaiMy (Female)"
            
            if self.ui:
            try:
                os.unlink(temp_file)
            except:
                pass
                
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Edge TTS error: {str(e)}", 'error')
    
    def _speak_google(self, text):
        """Speak using Google TTS"""
        try:
            start_time = time.time()
            
            if self.ui:
                self.ui.log(f"🔊 Speaking (Google TTS): {text[:50]}...", 'info')
            
            # Stop any playing audio
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    time.sleep(0.05)
            except:
                pass
            
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # Generate speech
            tts = gTTS(text=text, lang='vi', slow=False, timeout=3)
            tts.save(temp_file)
            
            gen_time = (time.time() - start_time) * 1000
            if self.ui:
                self.ui.log(f"   Generated in {gen_time:.0f}ms", 'info')
            
            # Play audio
            pygame.mixer.music.load(temp_file)
            time.sleep(0.1)  # Buffer time
            pygame.mixer.music.play()
            
            # Wait for playback
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            
            # Cleanup
            try:
                os.unlink(temp_file)
            except:
                pass
                
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ Google TTS error: {str(e)}", 'error')
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        if not self.tts_engine:
            if self.ui:
                self.ui.log("⚠️ pyttsx3 engine not available", 'info')
            return
        
        try:
            if self.ui:
                self.ui.log(f"🔊 Speaking (pyttsx3): {text[:50]}...", 'info')
            
            # Create new engine instance for thread safety
            temp_engine = pyttsx3.init()
            temp_engine.setProperty('rate', self.settings.get('tts_speed', 150))
            temp_engine.setProperty('volume', 1.0)
            
            if self.selected_voice_id:
                temp_engine.setProperty('voice', self.selected_voice_id)
            
            temp_engine.say(text)
            temp_engine.runAndWait()
            
            del temp_engine
            
        except Exception as e:
            if self.ui:
                self.ui.log(f"❌ pyttsx3 error: {str(e)}", 'error')
