"""
Test Google TTS xem có bị mất chữ đầu không
"""
from gtts import gTTS
import pygame
import tempfile
import os

print("=" * 70)
print("TEST: Google TTS có bị mất chữ đầu không?")
print("=" * 70)

pygame.mixer.init()

text = "Xin chào các bạn, đây là Google TTS"

print(f"\n📝 Text: '{text}'")
print("🎤 Engine: Google TTS")

# Generate
with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
    temp_file = fp.name

print("\n⏳ Generating...")
tts = gTTS(text=text, lang='vi', slow=False)
tts.save(temp_file)
print("✅ Generated!")

# Play
sound = pygame.mixer.Sound(temp_file)
sound.set_volume(1.0)

print("\n▶️ Playing...")
sound.play()

while pygame.mixer.get_busy():
    pygame.time.wait(50)

print("✅ Done!")

# Cleanup
os.unlink(temp_file)

print("\n" + "=" * 70)
print("📊 KẾT QUẢ:")
print("=" * 70)
print("Google TTS có nghe đầy đủ 'Xin chào' không?")
print("\n💡 Nếu Google TTS OK:")
print("   → Vấn đề là Edge TTS voice")
print("   → Giải pháp: Dùng Google TTS hoặc thử voice khác")
print("\n💡 Nếu Google TTS cũng mất:")
print("   → Vấn đề là pygame hoặc loa")
print("   → Cần kiểm tra hardware")
