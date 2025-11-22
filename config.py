"""
Configuration Module
Centralized settings management
"""

class Config:
    """Application configuration"""
    
    # TTS Settings
    TTS_MODES = {
        'pyttsx3': {
            'name': 'pyttsx3',
            'display': '⚡ pyttsx3 (Fastest, ~50ms)',
            'latency': 50
        },
        'gtts': {
            'name': 'Google TTS',
            'display': '🌐 Google TTS (Balanced, ~300ms)',
            'latency': 300
        },
        'edge': {
            'name': 'Edge TTS',
            'display': '🎯 Edge TTS (Best Quality, ~500ms) ⭐',
            'latency': 500
        }
    }
    
    # Edge TTS Voices
    EDGE_VOICES = {
        'female': 'vi-VN-HoaiMyNeural',
        'male': 'vi-VN-NamMinhNeural'
    }
    
    # Whisper Models
    WHISPER_MODELS = ['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']
    
    # Compute Types
    COMPUTE_TYPES = ['int8', 'float16', 'float32']
    
    # Default Settings
    DEFAULTS = {
        'model': 'base',
        'compute_type': 'int8',
        'beam_size': 3,
        'silence_threshold': 500,
        'tts_speed': 150,
        'tts_engine': 'edge',  # Default to Edge TTS
        'pause_time': 0.5,
        'min_audio_length': 1.0,
        'padding_words': 1  # Số từ "ừ" để padding
    }
    
    # Audio Settings
    AUDIO = {
        'chunk_size': 512,
        'whisper_rate': 16000,
        'format': 'paInt16'
    }
    
    # Gender Detection
    GENDER_DETECTION = {
        'male_max_hz': 165,
        'female_min_hz': 180,
        'enabled': True
    }
    
    # UI Colors
    COLORS = {
        'bg': '#2b2b2b',
        'fg': 'white',
        'chinese': '#2196F3',
        'vietnamese': '#4CAF50',
        'info': '#FFC107',
        'error': '#f44336',
        'success': '#4CAF50'
    }
    
    @staticmethod
    def get_default_settings():
        """Get default settings dictionary"""
        return Config.DEFAULTS.copy()
