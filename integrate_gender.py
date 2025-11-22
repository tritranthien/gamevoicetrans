"""
Script tự động tích hợp Gender Detection vào voicetrans.py
"""
import re

print("=" * 70)
print("TÍCH HỢP GENDER DETECTION VÀO VOICETRANS.PY")
print("=" * 70)

# Đọc file gốc
print("\n📖 Đọc file voicetrans.py...")
with open('voicetrans.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("✅ Đã đọc file!")

# Backup
print("\n💾 Tạo backup...")
with open('voicetrans_before_gender.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ Backup tạo tại: voicetrans_before_gender.py")

# Các thay đổi cần thực hiện
changes = []

# 1. Thêm import edge_tts và asyncio (nếu chưa có)
if 'import edge_tts' not in content:
    changes.append("❌ Thiếu: import edge_tts")
    print("\n⚠️ Cần thêm imports:")
    print("   import edge_tts")
    print("   import asyncio")
else:
    changes.append("✅ Đã có: import edge_tts")

# 2. Kiểm tra TTS engine selection
if 'tts_engine_var' in content:
    changes.append("✅ Đã có: TTS engine selection")
else:
    changes.append("❌ Thiếu: TTS engine radio buttons")

# 3. Kiểm tra gender detection function
if 'detect_gender' in content:
    changes.append("✅ Đã có: detect_gender function")
else:
    changes.append("❌ Thiếu: detect_gender function")

# 4. Kiểm tra Edge TTS voices
if 'HoaiMyNeural' in content:
    changes.append("✅ Đã có: Edge TTS voices")
else:
    changes.append("❌ Thiếu: Edge TTS voice configuration")

# 5. Kiểm tra is_tts_playing flag
if 'is_tts_playing' in content:
    changes.append("✅ Đã có: is_tts_playing flag")
else:
    changes.append("❌ Thiếu: is_tts_playing flag")

# Hiển thị kết quả
print("\n" + "=" * 70)
print("KẾT QUẢ KIỂM TRA:")
print("=" * 70)
for change in changes:
    print(f"  {change}")

# Đếm số lượng
missing = sum(1 for c in changes if c.startswith("❌"))
complete = sum(1 for c in changes if c.startswith("✅"))

print(f"\n📊 Tổng kết: {complete}/{len(changes)} tính năng đã có")
print(f"   Còn thiếu: {missing} tính năng")

if missing == 0:
    print("\n🎉 HOÀN HẢO! File đã có đầy đủ tính năng!")
    print("   Chỉ cần test và verify!")
else:
    print(f"\n⚠️ Cần thêm {missing} tính năng")
    print("\n💡 Giải pháp:")
    print("   1. Sử dụng modules đã tạo (tts_engine.py, audio_utils.py)")
    print("   2. Hoặc tôi tạo file voicetrans.py mới hoàn chỉnh")
    print("   3. Hoặc integrate từng phần theo hướng dẫn")

print("\n" + "=" * 70)
