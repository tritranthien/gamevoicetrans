"""
Audio Utilities Module
Helper functions for audio processing
"""
import numpy as np


class AudioUtils:
    """Audio processing utilities"""
    
    @staticmethod
    def calculate_rms(audio_data):
        """
        Calculate RMS (Root Mean Square) of audio data
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            float: RMS value
        """
        if not audio_data or len(audio_data) == 0:
            return 0.0
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            if len(audio_array) == 0:
                return 0.0
            
            mean_square = np.mean(audio_array.astype(np.float64)**2)
            
            if mean_square < 0:
                return 0.0
            
            return np.sqrt(mean_square)
        except Exception:
            return 0.0
    
    @staticmethod
    def resample_audio(audio_data, from_rate, to_rate, channels=1):
        """
        Resample audio from one sample rate to another
        
        Args:
            audio_data: Raw audio bytes
            from_rate: Source sample rate
            to_rate: Target sample rate
            channels: Number of audio channels
            
        Returns:
            bytes: Resampled audio data
        """
        if from_rate == to_rate:
            return audio_data
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # If stereo, convert to mono
        if channels == 2:
            audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
        
        # Resample
        num_samples = int(len(audio_array) * to_rate / from_rate)
        resampled = np.interp(
            np.linspace(0, len(audio_array), num_samples),
            np.arange(len(audio_array)),
            audio_array
        ).astype(np.int16)
        
        return resampled.tobytes()
    
    @staticmethod
    def detect_gender(audio_array, sample_rate=16000):
        """
        Detect gender based on pitch (fundamental frequency)
        
        Args:
            audio_array: Normalized audio array (float32, -1 to 1)
            sample_rate: Sample rate of audio
            
        Returns:
            str: 'male', 'female', or 'unknown'
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
            
            frequency = sample_rate / peak
            
            # Classify based on frequency
            # Male: typically 85-180 Hz
            # Female: typically 165-255 Hz
            if frequency < 165:
                return "male"
            elif frequency > 180:
                return "female"
            else:
                return "unknown"  # Overlap zone
                
        except Exception:
            return "unknown"
    
    @staticmethod
    def get_gender_icon(gender):
        """
        Get emoji icon for gender
        
        Args:
            gender: 'male', 'female', or 'unknown'
            
        Returns:
            str: Emoji icon
        """
        icons = {
            'male': '👨',
            'female': '👩',
            'unknown': '👤'
        }
        return icons.get(gender, '👤')
