"""
Test edge-tts để xem có nhanh hơn gTTS không
"""
import asyncio
import edge_tts
import time

async def test_edge_tts():
    text = "Xin chào, đây là bài kiểm tra giọng nói tiếng Việt"
    
    print("Testing Edge TTS...")
    print(f"Text: {text}")
    print("=" * 60)
    
    # List available Vietnamese voices
    print("\nAvailable Vietnamese voices:")
    voices = await edge_tts.list_voices()
    vi_voices = [v for v in voices if v['Locale'].startswith('vi')]
    
    for i, voice in enumerate(vi_voices, 1):
        print(f"{i}. {voice['ShortName']}")
        print(f"   Name: {voice.get('Name', 'N/A')}")
        print(f"   Gender: {voice.get('Gender', 'N/A')}")
        print()
    
    if vi_voices:
        # Test with first Vietnamese voice
        voice_name = vi_voices[0]['ShortName']
        print(f"Testing with: {voice_name}")
        
        start = time.time()
        
        # Generate speech
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save("test_edge.mp3")
        
        elapsed = (time.time() - start) * 1000
        print(f"✅ Generated in {elapsed:.0f}ms")
        print(f"   File saved: test_edge.mp3")
    else:
        print("❌ No Vietnamese voices found!")

if __name__ == "__main__":
    asyncio.run(test_edge_tts())
