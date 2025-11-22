# 🎛️ HƯỚNG DẪN: THÊM PADDING SLIDER VÀO UI

## 📝 Cần Thêm Vào `voicetrans.py`

### 1. Trong `create_sliders()` method (dòng ~330-350)

Thêm slider mới sau slider "Min Audio Length":

```python
# Padding Words (NEW!)
ttk.Label(parent, text="🔧 Padding (từ 'ừ'):").grid(row=row, column=0, sticky=tk.W, pady=5)
self.padding_scale = tk.Scale(
    parent, 
    from_=0, 
    to=5, 
    orient=tk.HORIZONTAL,
    bg=Config.COLORS['bg'], 
    fg=Config.COLORS['fg']
)
self.padding_scale.set(Config.DEFAULTS['padding_words'])  # Default: 1
self.padding_scale.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
row += 1
```

### 2. Trong `start_translation()` method (dòng ~410-420)

Thêm padding_words vào settings dict:

```python
settings = {
    'model': self.model_combo.get(),
    'compute_type': self.compute_combo.get(),
    'beam_size': self.beam_scale.get(),
    'silence_threshold': self.threshold_scale.get(),
    'tts_speed': self.tts_scale.get(),
    'device_index': device_idx,
    'tts_engine': self.tts_engine_var.get(),
    'pause_time': self.pause_scale.get(),
    'min_audio_length': self.min_audio_scale.get(),
    'padding_words': self.padding_scale.get()  # NEW!
}
```

### 3. Trong `TranslatorEngine.__init__()` (dòng ~60-70)

TTS Engine sẽ tự động nhận padding_words từ settings:

```python
# TTS Engine (đã support padding)
self.tts_engine = TTSEngine(
    mode=settings.get('tts_engine', 'edge'),
    ui=ui,
    settings=settings  # Bao gồm padding_words
)
```

## 🎯 Hoặc Dùng Demo UI

Chạy demo UI để test:
```bash
python demo_padding_ui.py
```

Demo UI cho phép:
- ✅ Điều chỉnh padding từ 0-5
- ✅ Xem preview text sẽ phát
- ✅ Test ngay lập tức
- ✅ Tìm giá trị tối ưu cho sound card

## 📊 Giá Trị Khuyến Nghị

| Sound Card | Padding |
|------------|---------|
| Tốt | 0-1 |
| Trung bình | 1-2 |
| Xấu | 2-3 |

## 💡 Lưu Ý

- Padding = 0: Không thêm "ừ" (có thể mất chữ đầu)
- Padding = 1: Thêm 1 "ừ" (đủ cho hầu hết sound card)
- Padding = 2+: Thêm nhiều "ừ" (cho sound card xấu)

Mỗi từ "ừ" ≈ 150-200ms latency

---

Bạn muốn tôi integrate trực tiếp vào `voicetrans.py` không? 🚀
