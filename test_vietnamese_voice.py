import pyttsx3

print("Testing Vietnamese TTS Voice...")
print("=" * 60)

# Initialize engine
engine = pyttsx3.init()

# Get all voices
voices = engine.getProperty('voices')
print(f"\nFound {len(voices)} voices:\n")

vietnamese_voices = []
for i, voice in enumerate(voices):
    print(f"[{i+1}] {voice.name}")
    print(f"    ID: {voice.id}")
    if hasattr(voice, 'languages'):
        print(f"    Languages: {voice.languages}")
    print()
    
    # Check if Vietnamese
    name_lower = voice.name.lower()
    id_lower = voice.id.lower()
    if 'vietnam' in name_lower or 'việt' in name_lower or 'viet' in name_lower:
        vietnamese_voices.append(voice)

print("=" * 60)
print(f"\nFound {len(vietnamese_voices)} Vietnamese voice(s):\n")

if vietnamese_voices:
    for voice in vietnamese_voices:
        print(f"Testing voice: {voice.name}")
        print(f"Voice ID: {voice.id}")
        
        try:
            # Set the voice
            engine.setProperty('voice', voice.id)
            
            # Test with Vietnamese text
            test_text = "Xin chào, tôi đang nói tiếng Việt"
            print(f"Speaking: '{test_text}'")
            
            engine.say(test_text)
            engine.runAndWait()
            
            print("✅ Voice test completed!\n")
            
        except Exception as e:
            print(f"❌ Error testing voice: {e}\n")
else:
    print("⚠️ No Vietnamese voices found!")
    print("\nTrying with default voice and Vietnamese text...")
    
    try:
        test_text = "Xin chào, tôi đang nói tiếng Việt"
        print(f"Speaking: '{test_text}'")
        engine.say(test_text)
        engine.runAndWait()
        print("✅ Default voice test completed!")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test completed!")
