import os
from pathlib import Path
from mutagen import File
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE

def get_audio_bitrate(file_path):
    """Get the bitrate of audio file in kbps"""
    try:
        file_ext = file_path.suffix.lower()
        
        if file_ext in ['.m4a', '.mp4']:
            audio = MP4(file_path)
            bitrate = audio.info.bitrate if hasattr(audio.info, 'bitrate') else 0
            return bitrate // 1000  # Convert to kbps
            
        elif file_ext == '.mp3':
            audio = MP3(file_path)
            bitrate = audio.info.bitrate if hasattr(audio.info, 'bitrate') else 0
            return bitrate // 1000  # Convert to kbps
            
        elif file_ext == '.flac':
            audio = FLAC(file_path)
            # FLAC doesn't have bitrate in the same way, calculate it
            if hasattr(audio.info, 'bitrate'):
                return audio.info.bitrate // 1000
            else:
                # Calculate approximate bitrate from file size and duration
                file_size = file_path.stat().st_size
                duration = audio.info.length if hasattr(audio.info, 'length') else 0
                if duration > 0:
                    return int((file_size * 8) / (duration * 1000))
                return 0
                
        elif file_ext in ['.wav', '.wave']:
            audio = WAVE(file_path)
            # WAV is uncompressed, calculate bitrate
            file_size = file_path.stat().st_size
            duration = audio.info.length if hasattr(audio.info, 'length') else 0
            if duration > 0:
                return int((file_size * 8) / (duration * 1000))
            return 0
            
        elif file_ext in ['.aac', '.ogg', '.opus', '.wma']:
            audio = File(file_path)
            if audio and hasattr(audio.info, 'bitrate'):
                return audio.info.bitrate // 1000
            return 0
            
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return 0
    
    return 0

def get_audio_quality(bitrate):
    """Get quality description based on bitrate"""
    if bitrate >= 320:
        return "320kbps (High Quality)"
    elif bitrate >= 256:
        return "256kbps (Good Quality)"
    elif bitrate >= 192:
        return "192kbps (Medium Quality)"
    elif bitrate >= 128:
        return "128kbps (Standard Quality)"
    elif bitrate > 0:
        return f"{bitrate}kbps (Low Quality)"
    else:
        return "Unknown Quality"

def check_audio_quality():
    """Check bitrate of all audio files"""
    script_dir = Path(__file__).parent.absolute()
    
    audio_extensions = ['.mp3', '.m4a', '.flac', '.wav', '.aac', '.ogg', '.wma', '.opus']
    
    print("Audio Quality Checker")
    print("=" * 60)
    
    # Find all audio files
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(script_dir.rglob(f"*{ext}"))
    
    if not audio_files:
        print("No audio files found!")
        return
    
    print(f"Found {len(audio_files)} audio files\n")
    
    # Check quality for each file
    quality_stats = {
        "320kbps (High Quality)": 0,
        "256kbps (Good Quality)": 0,
        "192kbps (Medium Quality)": 0,
        "128kbps (Standard Quality)": 0,
        "Low Quality": 0,
        "Unknown Quality": 0
    }
    
    total_size = 0
    print("📊 Audio File Quality Report:")
    print("-" * 60)
    
    for audio_file in audio_files:
        try:
            file_size = audio_file.stat().st_size / (1024*1024)  # MB
            total_size += file_size
            
            bitrate = get_audio_bitrate(audio_file)
            quality = get_audio_quality(bitrate)
            
            # Update statistics
            if "320kbps" in quality:
                quality_stats["320kbps (High Quality)"] += 1
            elif "256kbps" in quality:
                quality_stats["256kbps (Good Quality)"] += 1
            elif "192kbps" in quality:
                quality_stats["192kbps (Medium Quality)"] += 1
            elif "128kbps" in quality:
                quality_stats["128kbps (Standard Quality)"] += 1
            elif "Low Quality" in quality:
                quality_stats["Low Quality"] += 1
            else:
                quality_stats["Unknown Quality"] += 1
            
            print(f"🔊 {audio_file.name}")
            print(f"   📁 Location: {audio_file.parent.name}/")
            print(f"   📊 Size: {file_size:.2f} MB")
            print(f"   🎵 Bitrate: {bitrate} kbps")
            print(f"   ⭐ Quality: {quality}")
            print()
            
        except Exception as e:
            print(f"❌ Error checking {audio_file.name}: {e}")
            quality_stats["Unknown Quality"] += 1
            print()
    
    # Print summary
    print("=" * 60)
    print("📈 QUALITY SUMMARY:")
    print("=" * 60)
    
    for quality_type, count in quality_stats.items():
        if count > 0:
            percentage = (count / len(audio_files)) * 100
            print(f"{quality_type}: {count} files ({percentage:.1f}%)")
    
    print(f"\n📦 Total files: {len(audio_files)}")
    print(f"💾 Total size: {total_size:.2f} MB")

def check_specific_folder():
    """Check audio quality in a specific folder"""
    folder_path = input("Enter folder path to check: ").strip()
    
    if not folder_path:
        print("No folder specified!")
        return
    
    target_folder = Path(folder_path)
    
    if not target_folder.exists():
        print(f"Folder '{folder_path}' does not exist!")
        return
    
    audio_extensions = ['.mp3', '.m4a', '.flac', '.wav', '.aac', '.ogg', '.wma', '.opus']
    
    print(f"\nChecking audio quality in: {target_folder}")
    print("=" * 60)
    
    # Find all audio files in the specified folder
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(target_folder.rglob(f"*{ext}"))
    
    if not audio_files:
        print("No audio files found in the specified folder!")
        return
    
    print(f"Found {len(audio_files)} audio files\n")
    
    # Group by bitrate
    bitrate_groups = {}
    
    for audio_file in audio_files:
        try:
            bitrate = get_audio_bitrate(audio_file)
            quality = get_audio_quality(bitrate)
            
            if quality not in bitrate_groups:
                bitrate_groups[quality] = []
            bitrate_groups[quality].append(audio_file)
            
        except Exception as e:
            print(f"Error checking {audio_file.name}: {e}")
    
    # Print grouped results
    for quality, files in bitrate_groups.items():
        print(f"\n{quality} ({len(files)} files):")
        for audio_file in files:
            file_size = audio_file.stat().st_size / (1024*1024)  # MB
            print(f"   🔊 {audio_file.name} ({file_size:.1f} MB)")

def quick_quality_check():
    """Quick check - show only summary without detailed file list"""
    script_dir = Path(__file__).parent.absolute()
    
    audio_extensions = ['.mp3', '.m4a', '.flac', '.wav', '.aac', '.ogg', '.wma', '.opus']
    
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(script_dir.rglob(f"*{ext}"))
    
    if not audio_files:
        print("No audio files found!")
        return
    
    quality_stats = {}
    total_size = 0
    
    for audio_file in audio_files:
        try:
            file_size = audio_file.stat().st_size / (1024*1024)
            total_size += file_size
            
            bitrate = get_audio_bitrate(audio_file)
            quality = get_audio_quality(bitrate)
            
            quality_stats[quality] = quality_stats.get(quality, 0) + 1
            
        except Exception:
            quality_stats["Unknown Quality"] = quality_stats.get("Unknown Quality", 0) + 1
    
    print("\n🎵 QUICK QUALITY CHECK:")
    print("=" * 40)
    print(f"Total files: {len(audio_files)}")
    print(f"Total size: {total_size:.1f} MB")
    print("\nQuality Distribution:")
    
    for quality, count in sorted(quality_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(audio_files)) * 100
        print(f"  {quality}: {count} files ({percentage:.1f}%)")

def main():
    print("Audio Quality Checker")
    print("=" * 50)
    print("Check bitrate and quality of your audio files")
    
    while True:
        print("\nOptions:")
        print("1. Check all audio files (detailed report)")
        print("2. Quick quality check (summary only)")
        print("3. Check specific folder")
        print("4. Exit")
        
        choice = input("\nChoose option (1/2/3/4): ").strip()
        
        if choice == '1':
            check_audio_quality()
            
        elif choice == '2':
            quick_quality_check()
            
        elif choice == '3':
            check_specific_folder()
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()