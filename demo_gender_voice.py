"""
Demo: Gender Detection + Voice Selection
Test tính năng phát hiện giọng nam/nữ và chọn voice phù hợp
"""
from tts_engine import TTSEngine
from audio_utils import AudioUtils
import numpy as np

print("=" * 60)
print("DEMO: Gender Detection + Voice Selection")
print("=" * 60)

# Tạo TTS Engine với Edge TTS
print("\n1️⃣ Khởi tạo Edge TTS Engine...")
tts = TTSEngine(mode='edge', ui=None, settings={'tts_speed': 150})
print("✅ Edge TTS initialized!")
print(f"   Female voice: {tts.edge_voice_female}")
print(f"   Male voice: {tts.edge_voice_male}")

# Test với giọng nữ
print("\n2️⃣ Test với giọng NỮ...")
print("   Đang phát: 'Xin chào, tôi là giọng nữ'")
tts.speak("Xin chào, tôi là giọng nữ", gender='female')
print("✅ Hoàn thành!")

# Test với giọng nam
print("\n3️⃣ Test với giọng NAM...")
print("   Đang phát: 'Xin chào, tôi là giọng nam'")
tts.speak("Xin chào, tôi là giọng nam", gender='male')
print("✅ Hoàn thành!")

# Test gender detection
print("\n4️⃣ Test Gender Detection...")
print("   Tạo audio giả lập...")

# Tạo audio giả với tần số thấp (nam)
sample_rate = 16000
duration = 1.0
frequency_male = 120  # Hz - giọng nam
t = np.linspace(0, duration, int(sample_rate * duration))
audio_male = np.sin(2 * np.pi * frequency_male * t).astype(np.float32)

detected_gender = AudioUtils.detect_gender(audio_male, sample_rate)
icon = AudioUtils.get_gender_icon(detected_gender)
print(f"   Audio với {frequency_male}Hz → Detected: {detected_gender} {icon}")

# Tạo audio giả với tần số cao (nữ)
frequency_female = 220  # Hz - giọng nữ
audio_female = np.sin(2 * np.pi * frequency_female * t).astype(np.float32)

detected_gender = AudioUtils.detect_gender(audio_female, sample_rate)
icon = AudioUtils.get_gender_icon(detected_gender)
print(f"   Audio với {frequency_female}Hz → Detected: {detected_gender} {icon}")

print("\n" + "=" * 60)
print("✅ DEMO HOÀN THÀNH!")
print("=" * 60)
print("\n💡 Tính năng hoạt động:")
print("   - Phát hiện giọng nam/nữ từ pitch")
print("   - Tự động chọn voice phù hợp")
print("   - Edge TTS với 2 giọng Việt chất lượng cao")
print("\n🎯 Sẵn sàng tích hợp vào ứng dụng chính!")
