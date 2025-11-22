"""
TTS Engine với DELAY THÊM sau khi load Sound
Test xem delay có giúp không
"""
import pygame
import edge_tts
import asyncio
import tempfile
import os
import time

print("=" * 70)
print("TEST: pygame.Sound VỚI DELAY")
print("=" * 70)

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

text = "Xin chào các bạn, đây là bài test"
voice = "vi-VN-HoaiMyNeural"

print(f"\n🔊 Text: '{text}'")
print("   Voice: HoaiMyNeural (Female)")

# Generate
with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
    temp_file = fp.name

async def generate():
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_file)

print("\n⏳ Generating audio...")
asyncio.run(generate())
print("✅ Generated!")

# Test với các delay khác nhau
delays = [0, 0.1, 0.2, 0.3, 0.5]

for delay in delays:
    print(f"\n{'='*70}")
    print(f"TEST: Delay {delay}s sau khi load Sound")
    print(f"{'='*70}")
    
    # Load sound
    sound = pygame.mixer.Sound(temp_file)
    sound.set_volume(1.0)
    
    # DELAY
    if delay > 0:
        print(f"⏳ Đợi {delay}s...")
        time.sleep(delay)
    
    # Play
    print("▶️ Playing...")
    sound.play()
    
    # Wait
    while pygame.mixer.get_busy():
        time.sleep(0.05)
    
    print("✅ Done!")
    print(f"   → Có nghe 'Xin chào' đầy đủ không?")
    
    if delay < delays[-1]:
        print("\n⏸️ Đợi 3 giây trước test tiếp theo...")
        time.sleep(3)

# Cleanup
os.unlink(temp_file)

print(f"\n{'='*70}")
print("📊 KẾT LUẬN:")
print(f"{'='*70}")
print("Delay nào nghe rõ 'Xin chào' nhất?")
print("- 0s (không delay)")
print("- 0.1s")
print("- 0.2s")
print("- 0.3s")
print("- 0.5s")
