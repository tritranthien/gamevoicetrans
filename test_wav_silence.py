"""
GIẢI PHÁP ĐƠN GIẢN: Tạo file WAV với silence padding
Không cần ffmpeg
"""
import numpy as np
import wave
from gtts import gTTS
import pygame
import tempfile
import os

print("=" * 70)
print("TEST: Thêm silence bằng cách tạo file WAV")
print("=" * 70)

pygame.mixer.init(frequency=22050)

text = "Xin chào các bạn"

# Test với các độ dài silence khác nhau
silence_durations = [0, 100, 300, 500, 1000]  # milliseconds

for silence_ms in silence_durations:
    print(f"\n{'='*70}")
    print(f"TEST: {silence_ms}ms silence ở đầu")
    print(f"{'='*70}")
    
    # Generate TTS
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_mp3 = fp.name
    
    tts = gTTS(text=text, lang='vi', slow=False)
    tts.save(temp_mp3)
    
    # Load MP3 với pygame để convert sang raw audio
    pygame.mixer.music.load(temp_mp3)
    
    # Tạo file WAV với silence
    sample_rate = 22050
    silence_samples = int(sample_rate * silence_ms / 1000)
    
    # Tạo silence (zeros)
    silence = np.zeros(silence_samples, dtype=np.int16)
    
    # Lưu thành WAV tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
        temp_wav = fp.name
    
    with wave.open(temp_wav, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(silence.tobytes())
    
    # Play silence + MP3
    print(f"▶️ Playing ({silence_ms}ms silence + audio)...")
    
    # Play silence first
    if silence_ms > 0:
        silence_sound = pygame.mixer.Sound(temp_wav)
        silence_sound.play()
        while pygame.mixer.get_busy():
            pygame.time.wait(10)
    
    # Then play actual audio
    pygame.mixer.music.load(temp_mp3)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.wait(10)
    
    print("✅ Done!")
    print(f"   → Có nghe 'Xin chào' đầy đủ không?")
    
    # Cleanup
    os.unlink(temp_mp3)
    os.unlink(temp_wav)
    
    if silence_ms != silence_durations[-1]:
        print("\n⏸️ Đợi 2 giây...")
        pygame.time.wait(2000)

print(f"\n{'='*70}")
print("📊 KẾT LUẬN:")
print(f"{'='*70}")
print("Silence nào nghe rõ 'Xin chào' nhất?")
for ms in silence_durations:
    print(f"- {ms}ms")
