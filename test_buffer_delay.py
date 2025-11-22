"""
Quick Fix: Test với buffer delay lớn hơn
"""
import edge_tts
import asyncio
import pygame
import tempfile
import os
import time

print("=" * 60)
print("TEST: Fix mất chữ đầu với delay lớn hơn")
print("=" * 60)

# Init pygame
pygame.mixer.init()
print("✅ Pygame initialized")

# Test với giọng nữ
text = "Xin chào, tôi là giọng nữ"
voice = "vi-VN-HoaiMyNeural"

print(f"\n🔊 Đang phát: '{text}'")
print("   Sử dụng buffer delay 300ms...")

# Create temp file
with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
    temp_file = fp.name

# Generate
async def generate():
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_file)

asyncio.run(generate())
print("✅ Audio generated")

# Play với buffer delay LỚN
pygame.mixer.music.load(temp_file)
pygame.mixer.music.set_volume(1.0)

print("⏳ Buffering 300ms...")
time.sleep(0.3)  # 300ms buffer

pygame.mixer.music.play()
print("▶️ Playing...")

# Wait
while pygame.mixer.music.get_busy():
    time.sleep(0.05)

# Cleanup
os.unlink(temp_file)

print("\n✅ HOÀN THÀNH!")
print("\n💡 Nếu vẫn nghe đầy đủ 'Xin chào...' → Delay 300ms là đủ")
print("   Nếu vẫn mất 'Xin' → Cần tăng lên 500ms hoặc có vấn đề khác")
