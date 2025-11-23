"""
Context-Aware Translation Module
Lưu lịch sử câu để dịch chính xác hơn
"""

class TranslationContext:
    def __init__(self, max_history=3):
        """
        Initialize translation context
        
        Args:
            max_history: Số câu lưu trong lịch sử (default: 3)
        """
        self.history = []  # [(chinese, vietnamese), ...]
        self.max_history = max_history
    
    def add(self, chinese_text, vietnamese_text):
        """Thêm câu vào lịch sử"""
        self.history.append((chinese_text, vietnamese_text))
        
        # Giữ tối đa max_history câu
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context_prompt(self):
        """Tạo context prompt từ lịch sử"""
        if not self.history:
            return ""
        
        # Format: "Previous: 你好 -> Xin chào | 谢谢 -> Cảm ơn"
        context_parts = []
        for ch, vi in self.history:
            context_parts.append(f"{ch} -> {vi}")
        
        return "Context: " + " | ".join(context_parts)
    
    def get_context_text(self):
        """Lấy text context để gửi kèm"""
        if not self.history:
            return ""
        
        # Ghép 3 câu trước
        texts = [ch for ch, vi in self.history]
        return " ".join(texts)
    
    def clear(self):
        """Xóa lịch sử"""
        self.history = []
    
    def __len__(self):
        """Số câu trong lịch sử"""
        return len(self.history)
    
    def __str__(self):
        """String representation"""
        if not self.history:
            return "Context: Empty"
        
        return f"Context ({len(self.history)} sentences): " + \
               " | ".join([f"{ch[:20]}..." if len(ch) > 20 else ch 
                          for ch, vi in self.history])
