"""
Test nhiều câu khác nhau để xác định vấn đề
"""
from tts_engine import TTSEngine
import time

print("=" * 70)
print("TEST: Kiểm tra mất chữ đầu với nhiều câu khác nhau")
print("=" * 70)

# Khởi tạo
tts = TTSEngine(mode='edge', ui=None, settings={})

# Danh sách câu test
test_sentences = [
    "Xin chào các bạn",
    "Chào buổi sáng",
    "Hôm nay trời đẹp",
    "Một hai ba bốn năm",
    "Tôi là trợ lý ảo",
    "Đây là bài kiểm tra",
    "Việt Nam đẹp lắm",
    "Xin cảm ơn bạn"
]

print("\n🎤 Sẽ phát 8 câu, mỗi câu cách nhau 2 giây")
print("📝 Hãy chú ý xem câu nào bị mất chữ đầu!\n")

for i, sentence in enumerate(test_sentences, 1):
    print(f"{i}. Đang phát: '{sentence}'")
    tts.speak(sentence, gender='female')
    print(f"   ✅ Xong!")
    
    if i < len(test_sentences):
        print("   ⏳ Đợi 2 giây...\n")
        time.sleep(2)

print("\n" + "=" * 70)
print("✅ TEST HOÀN THÀNH!")
print("=" * 70)
print("\n📊 Kết quả:")
print("   Những câu nào bị mất chữ đầu?")
print("   1. Xin chào các bạn → Nghe: ___ chào các bạn")
print("   2. Chào buổi sáng → Nghe: ___ buổi sáng")
print("   3. Hôm nay trời đẹp → Nghe: ___ nay trời đẹp")
print("   4. Một hai ba bốn năm → Nghe: ___ hai ba bốn năm")
print("   5. Tôi là trợ lý ảo → Nghe: ___ là trợ lý ảo")
print("   6. Đây là bài kiểm tra → Nghe: ___ là bài kiểm tra")
print("   7. Việt Nam đẹp lắm → Nghe: ___ Nam đẹp lắm")
print("   8. Xin cảm ơn bạn → Nghe: ___ cảm ơn bạn")
print("\n💡 Nếu TẤT CẢ đều mất chữ đầu → Vấn đề là pygame.Sound")
print("   Nếu CHỈ một vài câu → Vấn đề là Edge TTS generation")
