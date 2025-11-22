# ===================================================================
# HƯỚNG DẪN IMPLEMENT ĐẦY ĐỦ TẤT CẢ TÍNH NĂNG
# File: voicetrans.py
# ===================================================================

## 🎯 MỤC TIÊU:
Thêm Edge TTS, fix vòng lặp vô tận, fix audio overlap, fix mất chữ đầu

## 📝 CÁC THAY ĐỔI CẦN THỰC HIỆN:

### 1️⃣ THÊM IMPORT (Dòng 10-11) - ✅ ĐÃ CÓ
```python
import edge_tts
import asyncio
```

### 2️⃣ THÊM RADIO BUTTONS CHO TTS ENGINE (Thay checkbox, dòng ~145-160)

Tìm dòng:
```python
self.use_gtts_var = tk.BooleanVar(value=False)
```

Thay bằng:
```python
# TTS Engine Selection
self.tts_engine_var = tk.StringVar(value='edge')  # Default to Edge TTS

tts_engine_frame = ttk.LabelFrame(settings_frame, text="🔊 TTS Engine", padding=10)
tts_engine_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

ttk.Radiobutton(tts_engine_frame, text="⚡ pyttsx3 (Fastest, ~50ms)", 
                variable=self.tts_engine_var, value='pyttsx3').pack(anchor=tk.W)
ttk.Radiobutton(tts_engine_frame, text="🌐 Google TTS (Balanced, ~300ms)", 
                variable=self.tts_engine_var, value='gtts').pack(anchor=tk.W)
ttk.Radiobutton(tts_engine_frame, text="🎯 Edge TTS (Best Quality, ~500ms) ⭐", 
                variable=self.tts_engine_var, value='edge').pack(anchor=tk.W)
```

### 3️⃣ CẬP NHẬT _init_translator (Dòng ~400-415)

Tìm dòng:
```python
'use_gtts': self.use_gtts_var.get(),
```

Thay bằng:
```python
'tts_engine': self.tts_engine_var.get(),
```

### 4️⃣ THÊM FLAG VÀ LOCK TRONG TranslatorEngine.__init__ (Dòng ~461)

Sau dòng:
```python
self.is_running = False
```

Thêm:
```python
self.is_tts_playing = False  # Flag to pause capture during TTS
self.tts_lock = threading.Lock()  # Lock to prevent audio overlap
```

### 5️⃣ CẬP NHẬT TTS INITIALIZATION (Dòng ~503-525)

Thay toàn bộ phần TTS initialization bằng:
```python
# TTS - Support pyttsx3, Google TTS, and Edge TTS
self.tts_mode = settings.get('tts_engine', 'edge')
self.tts_engine = None
self.selected_voice_id = None
self.tts_lock = threading.Lock()

# Initialize pygame mixer (used by both gTTS and Edge TTS)
if self.tts_mode in ['gtts', 'edge']:
    try:
        pygame.mixer.init()
        self.ui.log(f"✅ Pygame mixer initialized for {self.tts_mode.upper()}", 'info')
    except Exception as e:
        self.ui.log(f"❌ pygame mixer error: {str(e)}", 'error')

if self.tts_mode == 'edge':
    # Edge TTS - Microsoft Neural voices
    self.ui.log("✅ Edge TTS selected (Microsoft Neural Voices)", 'info')
    self.ui.log("   Using voice: vi-VN-HoaiMyNeural (Female)", 'info')
    self.edge_voice = "vi-VN-HoaiMyNeural"
    
elif self.tts_mode == 'gtts':
    # Google TTS
    self.ui.log("✅ Google TTS selected", 'info')
    
else:  # pyttsx3
    # pyttsx3 initialization (giữ nguyên code cũ)
    try:
        self.tts_engine = pyttsx3.init()
        # ... (giữ nguyên phần còn lại)
```

### 6️⃣ CẬP NHẬT audio_capture_thread (Dòng ~677-680)

Sau dòng:
```python
data = stream.read(self.chunk, exception_on_overflow=False)
```

Thêm:
```python
# Skip processing if TTS is playing to avoid feedback loop
if self.is_tts_playing:
    if buffer:
        buffer = []
        silence_counter = 0
        is_speaking = False
    continue
```

### 7️⃣ VIẾT LẠI HOÀN TOÀN tts_thread (Dòng ~761)

Thay toàn bộ hàm tts_thread bằng code mới (xem file TTS_THREAD_COMPLETE.py)

## ⚠️ LƯU Ý:
- Backup đã được tạo: voicetrans_backup_*.py
- Test từng bước sau khi thay đổi
- Nếu có lỗi, dùng backup để restore

## 🚀 SAU KHI HOÀN THÀNH:
```bash
python voicetrans.py
```

Chọn Edge TTS và test!
