# 🎛️ HƯỚNG DẪN: CONFIGURABLE PADDING

## 🎯 Mục Đích

Thêm từ "ừm" vào đầu audio để hy sinh thay vì mất chữ thật.

## 🔧 Cách Sử Dụng

### 1. Tìm Số Padding Tối Ưu

Chạy test:
```bash
python test_find_optimal_padding.py
```

Test sẽ thử từ 1-5 từ "ừm" và bạn nghe để chọn số tối ưu.

### 2. Config TTS Engine

```python
from tts_engine import TTSEngine

# Tạo engine với số padding tùy chỉnh
tts = TTSEngine(
    mode='edge',
    settings={
        'padding_words': 3  # Số từ "ừm" (1-5)
    }
)

# Speak
tts.speak("Xin chào", gender='female')
```

## 📊 Ví Dụ

### padding_words = 0 (Không padding)
- Text: "Xin chào"
- Phát: "Xin chào"
- Nghe: "chào" (mất "Xin")

### padding_words = 1
- Text: "Xin chào"
- Phát: "ừm. Xin chào"
- Nghe: "Xin chào" hoặc "chào" (tùy hardware)

### padding_words = 3 (Recommended)
- Text: "Xin chào"
- Phát: "ừm ừm ừm. Xin chào"
- Nghe: "Xin chào" (đầy đủ!)

### padding_words = 5
- Text: "Xin chào"
- Phát: "ừm ừm ừm ừm ừm. Xin chào"
- Nghe: "ừm. Xin chào" (thừa padding)

## 🎯 Cách Chọn Số Tối Ưu

Chọn số **NHỎ NHẤT** mà:
1. ✅ Nghe đầy đủ text gốc
2. ✅ KHÔNG nghe thấy "ừm" (đã bị hy sinh hết)

## 💡 Khuyến Nghị

| Sound Card | Padding Words |
|------------|---------------|
| Tốt (ít mất) | 1-2 |
| Trung bình | 3 |
| Xấu (mất nhiều) | 4-5 |

## 🔄 Update Config

Sau khi tìm được số tối ưu, update trong code:

```python
# config.py
DEFAULTS = {
    # ...
    'padding_words': 3,  # ← Update số này
}
```

## 📝 Ghi Chú

- Mỗi từ "ừm" ≈ 150-200ms
- padding_words = 3 ≈ 450-600ms padding
- Tăng padding = tăng latency nhưng đảm bảo không mất chữ

---

Chạy test và cho tôi biết số nào tối ưu nhất! 🎧
