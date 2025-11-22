"""
Kiểm tra file MP3 được Edge TTS generate
Xem có phải Edge TTS bỏ chữ đầu không
"""
import edge_tts
import asyncio
import os

print("=" * 70)
print("KIỂM TRA: Edge TTS có generate đầy đủ không?")
print("=" * 70)

text = "Xin chào các bạn, đây là bài test"
voice = "vi-VN-HoaiMyNeural"

output_file = "test_edge_output.mp3"

print(f"\n📝 Text: '{text}'")
print(f"🎤 Voice: {voice}")
print(f"💾 Output: {output_file}")

# Generate
async def generate():
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

print("\n⏳ Generating...")
asyncio.run(generate())
print("✅ Generated!")

# Check file
if os.path.exists(output_file):
    size = os.path.getsize(output_file)
    print(f"\n📊 File info:")
    print(f"   Path: {os.path.abspath(output_file)}")
    print(f"   Size: {size:,} bytes")
    
    print(f"\n🎧 QUAN TRỌNG:")
    print(f"   1. Mở file '{output_file}' bằng Windows Media Player")
    print(f"   2. Nghe xem có đầy đủ 'Xin chào các bạn' không")
    print(f"   3. Nếu file MP3 THIẾU → Vấn đề là Edge TTS")
    print(f"   4. Nếu file MP3 ĐẦY ĐỦ → Vấn đề là pygame")
    
    print(f"\n💡 File đã được lưu tại:")
    print(f"   {os.path.abspath(output_file)}")
    print(f"\n   → Click đúp vào file để nghe!")
else:
    print("❌ File không được tạo!")

print("\n" + "=" * 70)
