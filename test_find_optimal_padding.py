"""
TEST: Tìm số từ "ừm" tối ưu để hy sinh
Test từ 1-5 từ "ừm"
"""
from tts_engine import TTSEngine
import time

print("=" * 70)
print("TEST: Tìm số từ 'ừm' tối ưu")
print("=" * 70)

text = "Xin chào các bạn, đây là bài test"

# Test với 1-5 từ "ừm"
for num_padding in range(1, 6):
    print(f"\n{'='*70}")
    print(f"TEST {num_padding}: Thêm {num_padding} từ 'ừm'")
    print(f"{'='*70}")
    
    # Tạo TTS engine với padding
    tts = TTSEngine(
        mode='edge', 
        ui=None, 
        settings={'padding_words': num_padding}
    )
    
    print(f"📝 Text gốc: '{text}'")
    
    # Tạo padding
    padding = " ".join(["ừm"] * num_padding) + ". "
    print(f"🔧 Padding: '{padding}'")
    print(f"📢 Text phát: '{padding + text}'")
    
    print(f"\n▶️ Đang phát với {num_padding} từ 'ừm'...")
    tts.speak(text, gender='female')
    print("✅ Hoàn thành!")
    
    print(f"\n❓ Kết quả:")
    print(f"   - Có nghe đầy đủ 'Xin chào các bạn' không?")
    print(f"   - Còn nghe thấy từ 'ừm' nào không?")
    
    if num_padding < 5:
        print(f"\n⏸️ Đợi 3 giây trước test tiếp theo...")
        time.sleep(3)

print(f"\n{'='*70}")
print("📊 KẾT QUẢ:")
print(f"{'='*70}")
print("Số từ 'ừm' nào là tối ưu?")
print("")
print("1 từ 'ừm': ___")
print("2 từ 'ừm': ___")
print("3 từ 'ừm': ___")
print("4 từ 'ừm': ___")
print("5 từ 'ừm': ___")
print("")
print("💡 Chọn số nhỏ nhất mà:")
print("   - Nghe đầy đủ 'Xin chào các bạn'")
print("   - KHÔNG nghe thấy 'ừm' (đã bị hy sinh hết)")
