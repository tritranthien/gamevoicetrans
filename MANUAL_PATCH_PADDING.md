# 🔧 PATCH: Thêm Padding Slider vào voicetrans.py

## ⚠️ File voicetrans.py bị lỗi khi auto-edit

Vui lòng thêm thủ công theo hướng dẫn sau:

---

## 📝 BƯỚC 1: Thêm Slider vào UI (dòng ~210)

Tìm đoạn code:
```python
min_audio_info = tk.Label(settings_frame, text="Lower = Catch short sentences",
                         bg='#2b2b2b', fg='#888', font=('Arial', 8))
min_audio_info.grid(row=10, column=2, sticky='w', padx=5)

settings_frame.columnconfigure(1, weight=1)
```

Thay bằng:
```python
min_audio_info = tk.Label(settings_frame, text="Lower = Catch short sentences",
                         bg='#2b2b2b', fg='#888', font=('Arial', 8))
min_audio_info.grid(row=10, column=2, sticky='w', padx=5)

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

settings_frame.columnconfigure(1, weight=1)
```

---

## 📝 BƯỚC 2: Thêm vào settings dict (dòng ~420)

Tìm đoạn code:
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
    'min_audio_length': self.min_audio_scale.get()
}
```

Thêm dòng cuối:
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

---

## ✅ XONG!

TTS Engine sẽ tự động nhận `padding_words` từ settings.

---

## 🧪 TEST

1. Restart app: `python voicetrans.py`
2. Điều chỉnh slider "Padding (từ 'ừ')" từ 0-5
3. Start translation và test

---

Hoặc dùng demo UI để test trước:
```bash
python demo_padding_ui.py
```
