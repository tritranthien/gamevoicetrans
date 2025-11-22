"""
Auto-patch script: Thêm padding slider vào voicetrans.py
"""
import re

print("🔧 Auto-patch: Adding padding slider to voicetrans.py")
print("=" * 60)

# Read file
try:
    with open('voicetrans.py', 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"❌ Error reading file: {e}")
    print("\n💡 Vui lòng restore file voicetrans.py từ backup hoặc git")
    exit(1)

# Check if already patched
if 'padding_scale' in content:
    print("✅ File đã có padding slider rồi!")
    exit(0)

# Find position to add slider (after min_audio_scale)
pattern1 = r"(self\.min_audio_scale\.grid\(row=10.*?\n.*?min_audio_info.*?\n.*?min_audio_info\.grid\(row=10.*?\n)"

if not re.search(pattern1, content, re.DOTALL):
    print("❌ Không tìm thấy vị trí phù hợp để thêm slider")
    print("💡 File có thể đã bị sửa đổi. Vui lòng restore từ backup")
    exit(1)

# Add padding slider code
padding_slider_code = '''
        # Padding Words (NEW!)
        ttk.Label(settings_frame, text="🔧 Padding (từ 'ừ'):").grid(row=11, column=0, sticky='w', pady=5)
        self.padding_scale = tk.Scale(settings_frame, from_=0, to=5, resolution=1, orient=tk.HORIZONTAL,
                                     bg='#2b2b2b', fg='white', highlightthickness=0,
                                     length=150, troughcolor='#444')
        self.padding_scale.set(1)  # Default 1 từ "ừ"
        self.padding_scale.grid(row=11, column=1, sticky='w', pady=5, padx=5)
        
        padding_info = tk.Label(settings_frame, text="Fix mất chữ đầu",
                               bg='#2b2b2b', fg='#888', font=('Arial', 8))
        padding_info.grid(row=11, column=2, sticky='w', padx=5)
'''

content = re.sub(pattern1, r'\1' + padding_slider_code + '\n', content, flags=re.DOTALL)

# Add to settings dict
pattern2 = r"('min_audio_length': self\.min_audio_scale\.get\(\))"
replacement2 = r"\1,\n                'padding_words': self.padding_scale.get()  # NEW!"

if re.search(pattern2, content):
    content = re.sub(pattern2, replacement2, content)
else:
    print("⚠️ Không tìm thấy settings dict, bỏ qua bước này")

# Write back
try:
    with open('voicetrans.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Đã patch thành công!")
    print("\n🎯 Đã thêm:")
    print("   - Padding slider vào UI (row 11)")
    print("   - padding_words vào settings dict")
    print("\n💡 Restart app để test:")
    print("   python voicetrans.py")
except Exception as e:
    print(f"❌ Error writing file: {e}")
    exit(1)
