"""
Test với SSML - thêm silence break ở đầu
"""
import edge_tts
import asyncio
import pygame
import tempfile
import os

print("=" * 70)
print("TEST: Dùng SSML để thêm silence break")
print("=" * 70)

pygame.mixer.init()

text = "Xin chào các bạn"
voice = "vi-VN-HoaiMyNeural"

# Test với các cách khác nhau
tests = [
    ("1. Không padding", text),
    ("2. Padding: dấu chấm", ". " + text),
    ("3. Padding: 3 dấu chấm", "... " + text),
    ("4. Padding: khoảng trắng", "   " + text),
    ("5. SSML: 200ms break", f'<speak><break time="200ms"/>{text}</speak>'),
    ("6. SSML: 500ms break", f'<speak><break time="500ms"/>{text}</speak>'),
]

for name, test_text in tests:
    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"Text: '{test_text}'")
    print(f"{'='*70}")
    
    # Generate
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_file = fp.name
    
    async def generate():
        communicate = edge_tts.Communicate(test_text, voice)
        await communicate.save(temp_file)
    
    try:
        asyncio.run(generate())
        
        # Play
        sound = pygame.mixer.Sound(temp_file)
        sound.set_volume(1.0)
        
        print("▶️ Playing...")
        sound.play()
        
        while pygame.mixer.get_busy():
            pygame.time.wait(50)
        
        print("✅ Done!")
        print("   → Có nghe 'Xin chào' đầy đủ không?")
        
        # Cleanup
        os.unlink(temp_file)
        
        # Wait before next test
        if name != tests[-1][0]:
            print("\n⏸️ Đợi 2 giây...")
            pygame.time.wait(2000)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            os.unlink(temp_file)
        except:
            pass

print(f"\n{'='*70}")
print("📊 KẾT QUẢ:")
print(f"{'='*70}")
print("Cách nào nghe rõ 'Xin chào' nhất?")
print("1. Không padding")
print("2. Dấu chấm")
print("3. 3 dấu chấm")
print("4. Khoảng trắng")
print("5. SSML 200ms break")
print("6. SSML 500ms break")
