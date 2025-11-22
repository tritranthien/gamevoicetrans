"""
GIẢI PHÁP CUỐI CÙNG: Thêm silence vào đầu file MP3
Dùng pydub để edit audio file
"""
import os
import sys

# Check if pydub is installed
try:
    from pydub import AudioSegment
    from pydub.playback import play
    print("✅ pydub đã cài đặt")
except ImportError:
    print("❌ Chưa cài pydub!")
    print("\n📦 Đang cài đặt pydub...")
    os.system("pip install pydub")
    print("\n✅ Đã cài xong! Chạy lại script này.")
    sys.exit(0)

from gtts import gTTS
import tempfile

print("=" * 70)
print("GIẢI PHÁP: Thêm 500ms silence vào đầu audio")
print("=" * 70)

text = "Xin chào các bạn, đây là test cuối cùng"

print(f"\n📝 Text: '{text}'")

# Generate TTS
with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
    temp_file = fp.name

print("\n⏳ Generating TTS...")
tts = gTTS(text=text, lang='vi', slow=False)
tts.save(temp_file)
print("✅ Generated!")

# Load audio
print("\n⏳ Loading audio...")
audio = AudioSegment.from_mp3(temp_file)
print(f"   Duration: {len(audio)}ms")

# Create silence (500ms)
silence_duration = 500  # milliseconds
silence = AudioSegment.silent(duration=silence_duration)

# Add silence to beginning
print(f"\n⏳ Adding {silence_duration}ms silence to beginning...")
audio_with_silence = silence + audio
print(f"   New duration: {len(audio_with_silence)}ms")

# Save
output_file = "test_with_silence.mp3"
audio_with_silence.export(output_file, format="mp3")
print(f"\n✅ Saved to: {output_file}")

# Play
print("\n▶️ Playing with pydub...")
play(audio_with_silence)

print("\n" + "=" * 70)
print("📊 KẾT QUẢ:")
print("=" * 70)
print("Có nghe đầy đủ 'Xin chào' không?")
print("\n💡 Nếu OK:")
print("   → Giải pháp: Luôn thêm 500ms silence vào đầu")
print("   → Tôi sẽ update TTS engine")
print("\n💡 Nếu vẫn mất:")
print("   → Vấn đề là sound card/driver")
print("   → Cần update driver hoặc dùng loa khác")
