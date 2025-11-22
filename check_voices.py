import pyttsx3

print("=" * 80)
print("CHECKING ALL AVAILABLE TTS VOICES ON YOUR SYSTEM")
print("=" * 80)

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print(f"\n✅ Found {len(voices)} TTS voices:\n")
    
    for i, voice in enumerate(voices):
        print(f"\n{'='*80}")
        print(f"Voice #{i + 1}:")
        print(f"{'='*80}")
        print(f"  ID: {voice.id}")
        print(f"  Name: {voice.name}")
        
        # Print all attributes
        if hasattr(voice, 'languages'):
            print(f"  Languages: {voice.languages}")
        if hasattr(voice, 'gender'):
            print(f"  Gender: {voice.gender}")
        if hasattr(voice, 'age'):
            print(f"  Age: {voice.age}")
        
        # Check if it might be Vietnamese with more patterns
        is_vietnamese = False
        reasons = []
        
        # Check name
        name_lower = voice.name.lower()
        if 'vietnam' in name_lower or 'việt' in name_lower or 'viet' in name_lower:
            is_vietnamese = True
            reasons.append("Name contains Vietnamese keywords")
        
        # Check ID
        id_lower = voice.id.lower()
        if 'vi-' in id_lower or 'vi_' in id_lower or 'vietnam' in id_lower or 'viet' in id_lower:
            is_vietnamese = True
            reasons.append("ID contains Vietnamese keywords")
        
        # Check languages
        if hasattr(voice, 'languages') and voice.languages:
            for lang in voice.languages:
                lang_str = str(lang).lower()
                if 'vi' in lang_str or 'vietnam' in lang_str:
                    is_vietnamese = True
                    reasons.append(f"Language tag: {lang}")
        
        if is_vietnamese:
            print(f"\n  ⭐⭐⭐ VIETNAMESE VOICE DETECTED! ⭐⭐⭐")
            print(f"  Reasons: {', '.join(reasons)}")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    vietnamese_count = 0
    for voice in voices:
        name_lower = voice.name.lower()
        id_lower = voice.id.lower()
        if 'vietnam' in name_lower or 'việt' in name_lower or 'viet' in name_lower or 'vi-' in id_lower or 'vi_' in id_lower:
            vietnamese_count += 1
            print(f"✅ Vietnamese: {voice.name}")
    
    if vietnamese_count == 0:
        print("❌ No Vietnamese voices found!")
        print("\nPossible reasons:")
        print("1. Voice pack not installed correctly")
        print("2. Windows needs to be restarted after installation")
        print("3. Voice is installed but not registered with pyttsx3")
        print("\nTry using Google TTS instead (check the box in the app)")
    else:
        print(f"\n✅ Found {vietnamese_count} Vietnamese voice(s)!")
    
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")
