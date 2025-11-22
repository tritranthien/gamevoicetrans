"""
TEST: Nhiều câu khác nhau với padding
Kiểm tra xem vấn đề có phải do từ "Xin" không
"""
from tts_engine import TTSEngine
import time

print("=" * 70)
print("TEST: Nhiều câu khác nhau")
print("=" * 70)

# Các câu test khác nhau
test_sentences = [
    "Xin chào các bạn",
    "Chào buổi sáng",
    "Hôm nay trời đẹp",
    "Tôi là trợ lý ảo",
    "Việt Nam rất đẹp",
    "Cảm ơn bạn rất nhiều",
]

# Test với 3 từ "ừm"
padding_words = 3

print(f"\n🔧 Padding: {padding_words} từ 'ừm'")
print(f"📝 Sẽ test {len(test_sentences)} câu khác nhau\n")

tts = TTSEngine(
    mode='edge',
    settings={'padding_words': padding_words}
)

for i, sentence in enumerate(test_sentences, 1):
    print(f"{'='*70}")
    print(f"TEST {i}/{len(test_sentences)}")
    print(f"{'='*70}")
    print(f"📝 Câu gốc: '{sentence}'")
    
    # Tạo padding để show
    padding = " ".join(["ừm"] * padding_words) + ". "
    print(f"🔧 Sẽ phát: '{padding}{sentence}'")
    
    print(f"\n▶️ Đang phát...")
    tts.speak(sentence, gender='female')
    print("✅ Xong!")
    
    print(f"\n❓ Bạn nghe thấy gì?")
    print(f"   - Có nghe đầy đủ '{sentence}' không?")
    print(f"   - Có nghe thấy 'ừm' nào không?")
    
    if i < len(test_sentences):
        print(f"\n⏸️ Đợi 3 giây...\n")
        time.sleep(3)

print(f"\n{'='*70}")
print("📊 KẾT QUẢ:")
print(f"{'='*70}")
print("Câu nào nghe RÕ NHẤT?")
for i, sentence in enumerate(test_sentences, 1):
    print(f"{i}. {sentence}: ___")

print("\n💡 Nếu TẤT CẢ đều mất chữ đầu:")
print("   → Vấn đề KHÔNG phải từ 'Xin'")
print("   → Vấn đề là Edge TTS hoặc hardware")
print("\n💡 Nếu CHỈ câu 'Xin chào' mất:")
print("   → Vấn đề là từ 'Xin' đặc biệt")
print("   → Cần workaround riêng cho từ này")
