import winreg
import sys

print("=" * 80)
print("CHECKING WINDOWS TTS VOICES VIA REGISTRY")
print("=" * 80)

def check_registry_voices():
    """Check TTS voices registered in Windows Registry"""
    try:
        # Check both 32-bit and 64-bit registry paths
        paths = [
            r"SOFTWARE\Microsoft\Speech\Voices\Tokens",
            r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens",
        ]
        
        all_voices = []
        
        for path in paths:
            print(f"\n🔍 Checking registry path: {path}")
            print("-" * 80)
            
            try:
                # Try to open the registry key
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
                
                # Enumerate all subkeys (voices)
                i = 0
                while True:
                    try:
                        voice_name = winreg.EnumKey(key, i)
                        voice_path = f"{path}\\{voice_name}"
                        
                        # Open the voice key
                        voice_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, voice_path, 0, winreg.KEY_READ)
                        
                        # Get voice properties
                        try:
                            friendly_name, _ = winreg.QueryValueEx(voice_key, "")
                        except:
                            friendly_name = voice_name
                        
                        # Check for language
                        try:
                            lang, _ = winreg.QueryValueEx(voice_key, "Language")
                        except:
                            lang = "Unknown"
                        
                        voice_info = {
                            'name': friendly_name,
                            'key': voice_name,
                            'language': lang,
                            'path': voice_path
                        }
                        
                        all_voices.append(voice_info)
                        
                        # Check if Vietnamese
                        is_vietnamese = False
                        reasons = []
                        
                        if 'vietnam' in str(friendly_name).lower() or 'việt' in str(friendly_name).lower() or 'viet' in str(friendly_name).lower():
                            is_vietnamese = True
                            reasons.append("Name contains Vietnamese")
                        
                        if 'vi' in str(lang).lower() or '42a' in str(lang).lower():  # 42a is Vietnamese language code
                            is_vietnamese = True
                            reasons.append(f"Language code: {lang}")
                        
                        marker = "⭐ VIETNAMESE!" if is_vietnamese else ""
                        print(f"\n  Voice #{i+1}: {friendly_name} {marker}")
                        print(f"    Key: {voice_name}")
                        print(f"    Language: {lang}")
                        if reasons:
                            print(f"    Reasons: {', '.join(reasons)}")
                        
                        winreg.CloseKey(voice_key)
                        i += 1
                        
                    except OSError:
                        break
                
                winreg.CloseKey(key)
                print(f"\n  ✅ Found {i} voices in this path")
                
            except FileNotFoundError:
                print(f"  ⚠️ Registry path not found")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return all_voices
        
    except Exception as e:
        print(f"❌ Error accessing registry: {e}")
        return []

# Run the check
voices = check_registry_voices()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

vietnamese_voices = [v for v in voices if 'vietnam' in v['name'].lower() or 'việt' in v['name'].lower() or 'viet' in v['name'].lower() or 'vi' in str(v['language']).lower()]

if vietnamese_voices:
    print(f"\n✅ Found {len(vietnamese_voices)} Vietnamese voice(s):")
    for v in vietnamese_voices:
        print(f"  - {v['name']} (Language: {v['language']})")
else:
    print("\n❌ No Vietnamese voices found in Windows Registry!")
    print("\nThis means:")
    print("  1. Vietnamese voice pack is NOT installed, OR")
    print("  2. It's installed but not registered properly")
    print("\nTo install Vietnamese voice:")
    print("  1. Open Settings → Time & Language → Language")
    print("  2. Add Vietnamese (if not already added)")
    print("  3. Click Vietnamese → Options → Download Text-to-speech")
    print("  4. Restart your computer after installation")

print(f"\nTotal voices found: {len(voices)}")
print("=" * 80)

input("\nPress Enter to exit...")
