"""
Demo UI với Padding Slider
"""
import tkinter as tk
from tkinter import ttk
from tts_engine import TTSEngine

class PaddingDemoUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎛️ TTS Padding Demo")
        self.root.geometry("500x400")
        
        # Create UI
        self.create_ui()
        
        # Init TTS
        self.tts = None
        self.update_tts()
    
    def create_ui(self):
        # Header
        header = ttk.Label(self.root, text="🎛️ TTS Padding Settings", 
                          font=('Arial', 14, 'bold'))
        header.pack(pady=20)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(self.root, text="⚙️ Padding Config", padding=20)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Padding Words Slider
        ttk.Label(settings_frame, text="🔧 Số từ 'ừ' padding:", 
                 font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        self.padding_var = tk.IntVar(value=1)
        self.padding_scale = tk.Scale(
            settings_frame,
            from_=0,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.padding_var,
            command=self.on_padding_change,
            length=300
        )
        self.padding_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Value Label
        self.value_label = ttk.Label(settings_frame, text="1 từ", 
                                     font=('Arial', 10, 'bold'))
        self.value_label.grid(row=0, column=2, padx=10)
        
        # Info
        info_frame = ttk.LabelFrame(self.root, text="ℹ️ Thông tin", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, 
                                font=('Consolas', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Test Button
        test_btn = ttk.Button(self.root, text="🔊 Test Phát", 
                             command=self.test_speak)
        test_btn.pack(pady=10)
        
        # Update info
        self.update_info()
    
    def on_padding_change(self, value):
        """Callback khi slider thay đổi"""
        padding = int(value)
        
        # Update label
        if padding == 0:
            self.value_label.config(text="Không padding")
        elif padding == 1:
            self.value_label.config(text="1 từ")
        else:
            self.value_label.config(text=f"{padding} từ")
        
        # Update TTS
        self.update_tts()
        
        # Update info
        self.update_info()
    
    def update_tts(self):
        """Update TTS engine với padding mới"""
        padding = self.padding_var.get()
        self.tts = TTSEngine(
            mode='edge',
            settings={'padding_words': padding}
        )
    
    def update_info(self):
        """Update thông tin"""
        padding = self.padding_var.get()
        
        self.info_text.delete(1.0, tk.END)
        
        if padding == 0:
            self.info_text.insert(tk.END, "⚠️ KHÔNG PADDING\n\n")
            self.info_text.insert(tk.END, "Text phát: Xin chào\n")
            self.info_text.insert(tk.END, "Nghe: chào (mất 'Xin')\n")
        else:
            padding_text = " ".join(["ừ"] * padding)
            self.info_text.insert(tk.END, f"✅ PADDING: {padding} từ 'ừ'\n\n")
            self.info_text.insert(tk.END, f"Text phát: {padding_text}, Xin chào\n")
            self.info_text.insert(tk.END, f"Mất: {'ừ' if padding == 1 else 'ừ đầu'}\n")
            self.info_text.insert(tk.END, f"Nghe: ")
            
            if padding == 1:
                self.info_text.insert(tk.END, "Xin chào ✅\n")
            else:
                remaining = " ".join(["ừ"] * (padding - 1))
                self.info_text.insert(tk.END, f"{remaining}, Xin chào\n")
        
        self.info_text.insert(tk.END, "\n💡 Khuyến nghị:\n")
        self.info_text.insert(tk.END, "   - Sound card tốt: 0-1\n")
        self.info_text.insert(tk.END, "   - Sound card trung bình: 1-2\n")
        self.info_text.insert(tk.END, "   - Sound card xấu: 2-3\n")
    
    def test_speak(self):
        """Test phát"""
        text = "Xin chào, đây là bài test"
        padding = self.padding_var.get()
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"🔊 Đang phát với {padding} từ padding...\n\n")
        
        self.tts.speak(text, gender='female')
        
        self.info_text.insert(tk.END, "✅ Hoàn thành!\n\n")
        self.info_text.insert(tk.END, "Có nghe đầy đủ 'Xin chào' không?")


if __name__ == "__main__":
    root = tk.Tk()
    app = PaddingDemoUI(root)
    root.mainloop()
