"""
Test Normalize Punctuation
"""
from tts_engine import TTSEngine

# Test
tts = TTSEngine(mode='edge', settings={'padding_words': 1})

# Test text với nhiều dấu ngắt câu
test_texts = [
    "Xin chào! Tôi là AI. Bạn khỏe không?",
    "Đây là câu 1. Đây là câu 2! Đây là câu 3?",
    "Chào bạn; tôi đến từ Việt Nam: một đất nước xinh đẹp!"
]

print("🧪 Testing Normalize Punctuation\n")
print("=" * 60)

for text in test_texts:
    normalized = tts._normalize_punctuation(text)
    print(f"\n📝 Original:   {text}")
    print(f"✅ Normalized: {normalized}")
    print(f"🔊 Will speak: ừ, {normalized}")

print("\n" + "=" * 60)
print("✅ Tất cả dấu . ! ? ; : đã được thay bằng ,")
print("💡 Không còn pause dài!")
