import os
import subprocess
import sys
from pathlib import Path
import glob
from mutagen import File
from mutagen.mp4 import MP4, MP4Tags
import re
import time

def get_script_directory():
    """Get the directory where the script is located"""
    return Path(__file__).parent.absolute()

def check_requirements():
    """Check if required files exist"""
    script_dir = get_script_directory()
    required_files = ['gamdl.exe', 'cookies.txt', 'mp4decrypt.exe']
    missing_files = []
    
    for file in required_files:
        file_path = script_dir / file
        if not file_path.exists():
            missing_files.append(file)
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    return True

def get_audio_info(file_path):
    """Get audio quality information from file"""
    try:
        if file_path.suffix.lower() in ['.m4a', '.mp4']:
            audio = MP4(file_path)
            
            # Get file size
            file_size = file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            # Get bitrate and other info
            bitrate = audio.info.bitrate if hasattr(audio.info, 'bitrate') else 0
            length = audio.info.length if hasattr(audio.info, 'length') else 0
            sample_rate = audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else 0
            
            # Determine quality based on bitrate and file size
            quality = "AAC 256kbps"  # Default for Apple Music web
            
            if bitrate >= 320000:
                quality = "AAC 320kbps"
            elif bitrate >= 256000:
                quality = "AAC 256kbps"
            elif bitrate >= 192000:
                quality = "AAC 192kbps"
            elif bitrate >= 128000:
                quality = "AAC 128kbps"
            
            return {
                'quality': quality,
                'bitrate': f"{bitrate//1000}kbps" if bitrate else "Unknown",
                'sample_rate': f"{sample_rate}Hz" if sample_rate else "Unknown",
                'file_size': f"{size_mb:.2f}MB",
                'duration': f"{int(length//60)}:{int(length%60):02d}" if length else "Unknown"
            }
            
    except Exception as e:
        print(f"Error getting audio info: {e}")
    
    return None

def clean_text(text):
    """Clean text by removing dashes, 'Single' word and other unwanted characters"""
    if not text:
        return text
    
    # Replace common patterns
    cleaned = str(text)
    
    # Remove dashes from artist names (e.g., "Flow-G" -> "Flow G")
    cleaned = cleaned.replace('-', ' ')
    
    # Remove "Single" word (case insensitive)
    cleaned = re.sub(r'\s*-\s*Single\s*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*\(Single\)\s*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Single\s*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^\s*Single\s*-\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Remove multiple spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()

def update_metadata(file_path):
    """Update music file metadata"""
    try:
        if file_path.suffix.lower() in ['.m4a', '.mp4']:
            audio = MP4(file_path)
            
            # Get current metadata
            title = audio.get('\xa9nam', [''])[0] if '\xa9nam' in audio else ''
            artist = audio.get('\xa9ART', [''])[0] if '\xa9ART' in audio else ''
            album = audio.get('\xa9alb', [''])[0] if '\xa9alb' in audio else ''
            album_artist = audio.get('aART', [''])[0] if 'aART' in audio else ''
            
            # Clean the metadata
            if artist:
                cleaned_artist = clean_text(artist)
                if cleaned_artist != artist:
                    audio['\xa9ART'] = [cleaned_artist]
                    print(f"Updated artist: {artist} -> {cleaned_artist}")
            
            if album_artist:
                cleaned_album_artist = clean_text(album_artist)
                if cleaned_album_artist != album_artist:
                    audio['aART'] = [cleaned_album_artist]
                    print(f"Updated album artist: {album_artist} -> {cleaned_album_artist}")
            
            if title:
                cleaned_title = clean_text(title)
                if cleaned_title != title:
                    audio['\xa9nam'] = [cleaned_title]
                    print(f"Updated title: {title} -> {cleaned_title}")
            
            if album:
                cleaned_album = clean_text(album)
                if cleaned_album != album:
                    audio['\xa9alb'] = [cleaned_album]
                    print(f"Updated album: {album} -> {cleaned_album}")
            
            # Save the changes
            audio.save()
            
    except Exception as e:
        print(f"Error updating metadata for {file_path.name}: {e}")

def combine_playlist_tracks(playlist_dir, playlist_name):
    """Combine individual tracks into a single file for playlist downloads"""
    try:
        audio_files = list(playlist_dir.rglob("*.m4a")) + list(playlist_dir.rglob("*.mp4"))
        
        if len(audio_files) <= 1:
            return False
            
        print(f"\n🎵 Combining {len(audio_files)} tracks into single playlist file...")
        
        # Create combined filename
        safe_playlist_name = re.sub(r'[<>:"/\\|?*]', '', playlist_name)
        combined_file = playlist_dir / f"{safe_playlist_name}.m4a"
        
        # Use ffmpeg to combine files
        script_dir = get_script_directory()
        ffmpeg_path = script_dir / "ffmpeg.exe"
        
        if ffmpeg_path.exists():
            # Create file list for ffmpeg
            file_list = playlist_dir / "file_list.txt"
            with open(file_list, 'w', encoding='utf-8') as f:
                for audio_file in sorted(audio_files):
                    f.write(f"file '{audio_file.absolute()}'\n")
            
            # Combine using ffmpeg
            cmd = [
                str(ffmpeg_path),
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list),
                '-c', 'copy',
                str(combined_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            # Clean up file list
            file_list.unlink()
            
            if result.returncode == 0 and combined_file.exists():
                print(f"✅ Successfully created combined playlist: {combined_file.name}")
                
                # Remove individual tracks
                for audio_file in audio_files:
                    try:
                        audio_file.unlink()
                    except:
                        pass
                return True
            else:
                print("❌ Failed to combine playlist tracks")
                if combined_file.exists():
                    combined_file.unlink()
        else:
            print("❌ ffmpeg.exe not found - skipping playlist combination")
            
    except Exception as e:
        print(f"❌ Error combining playlist: {e}")
    
    return False

def move_files_to_downloads_folder():
    """Move all files from subfolders to main downloads folder"""
    script_dir = get_script_directory()
    downloads_dir = script_dir / "downloads"
    
    if not downloads_dir.exists():
        return
    
    # Find all subfolders in downloads directory
    subfolders = [f for f in downloads_dir.iterdir() if f.is_dir()]
    
    for folder in subfolders:
        try:
            # Move all audio files from subfolder to main downloads folder
            audio_files = list(folder.rglob("*.m4a")) + list(folder.rglob("*.mp4"))
            
            for audio_file in audio_files:
                # Create new path in main downloads folder
                new_path = downloads_dir / audio_file.name
                
                # If file with same name exists, add number to filename
                counter = 1
                while new_path.exists():
                    name_parts = audio_file.stem, audio_file.suffix
                    new_path = downloads_dir / f"{name_parts[0]}_{counter}{name_parts[1]}"
                    counter += 1
                
                # Move the file
                audio_file.rename(new_path)
                print(f"Moved: {audio_file.name} to downloads folder")
            
            # Remove empty subfolder
            try:
                folder.rmdir()
            except:
                # Folder not empty, might have other files, leave it
                pass
                
        except Exception as e:
            print(f"Error moving files from {folder.name}: {e}")

def clean_downloads():
    """Remove .lrc files, rename audio files, update metadata and show quality info"""
    script_dir = get_script_directory()
    downloads_dir = script_dir / "downloads"
    
    if not downloads_dir.exists():
        return
    
    # Move all files from subfolders to main downloads folder
    move_files_to_downloads_folder()
    
    # Delete all .lrc files
    lrc_files = list(downloads_dir.rglob("*.lrc"))
    for lrc_file in lrc_files:
        try:
            lrc_file.unlink()
            print(f"Deleted: {lrc_file.name}")
        except Exception as e:
            print(f"Error deleting {lrc_file.name}: {e}")
    
    # Process audio files
    audio_files = list(downloads_dir.rglob("*.m4a")) + list(downloads_dir.rglob("*.mp4"))
    
    print("\n=== DOWNLOADED FILES QUALITY ===")
    
    for audio_file in audio_files:
        try:
            filename = audio_file.stem  # filename without extension
            extension = audio_file.suffix  # .m4a or .mp4
            
            # Remove track numbers like "01. ", "02. ", etc.
            new_filename = filename
            if filename[:3].isdigit() and filename[3:5] == ". ":
                new_filename = filename[5:]
            elif filename[:2].isdigit() and filename[2:4] == ". ":
                new_filename = filename[4:]
            elif filename[:2].isdigit() and filename[2:3] == " ":
                new_filename = filename[3:]
            
            # Clean filename from "Single" and other patterns
            new_filename = clean_text(new_filename)
            
            # Only rename if filename changed
            if new_filename != filename:
                new_file_path = audio_file.parent / (new_filename + extension)
                
                # If file with same name exists, add number to filename
                counter = 1
                while new_file_path.exists() and new_file_path != audio_file:
                    new_file_path = audio_file.parent / f"{new_filename}_{counter}{extension}"
                    counter += 1
                
                # Rename the file
                audio_file.rename(new_file_path)
                print(f"Renamed: {audio_file.name} -> {new_file_path.name}")
                audio_file = new_file_path  # Update reference to new file
            
            # Update metadata
            update_metadata(audio_file)
            
            # Show quality information
            audio_info = get_audio_info(audio_file)
            if audio_info:
                print(f"📊 {audio_file.name}:")
                print(f"   Quality: {audio_info['quality']}")
                print(f"   Bitrate: {audio_info['bitrate']}")
                print(f"   Sample Rate: {audio_info['sample_rate']}")
                print(f"   File Size: {audio_info['file_size']}")
                print(f"   Duration: {audio_info['duration']}")
                print()
            
        except Exception as e:
            print(f"Error processing {audio_file.name}: {e}")
    
    print("=== QUALITY CHECK COMPLETE ===")

def download_content(url, combine_playlist=False):
    """Download content using gamdl"""
    try:
        print(f"Downloading: {url}")
        
        script_dir = get_script_directory()
        
        # Build command - WALANG -flat parameter
        cmd = [
            str(script_dir / 'gamdl.exe'),
            '--cookies-path', str(script_dir / 'cookies.txt'),
            '--output-path', str(script_dir / 'downloads'),
            url
        ]
        
        # Run gamdl
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("Download completed successfully!")
            
            # Check if this is a playlist and user wants to combine
            if combine_playlist and "playlist" in url.lower():
                # Extract playlist name from output
                playlist_name = "Playlist"
                if "Downloading playlist:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "Downloading playlist:" in line:
                            playlist_name = line.split("Downloading playlist:")[-1].strip()
                            break
                
                # Find the downloaded playlist directory
                downloads_dir = script_dir / "downloads"
                latest_dir = max([d for d in downloads_dir.iterdir() if d.is_dir()], 
                               key=os.path.getmtime, default=None)
                
                if latest_dir:
                    combine_playlist_tracks(latest_dir, playlist_name)
            
            # Clean up downloads after successful download
            clean_downloads()
            
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print("Download failed!")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
                
    except Exception as e:
        print(f"Unexpected error: {e}")

def read_links_from_file(filename):
    """Read links from a text file"""
    script_dir = get_script_directory()
    file_path = script_dir / filename
    
    if not file_path.exists():
        print(f"❌ File '{filename}' not found!")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip() and line.startswith('https://music.apple.com/')]
        
        return links
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return []

def download_from_file(filename):
    """Download all links from a text file"""
    print(f"\n📖 Reading links from {filename}...")
    links = read_links_from_file(filename)
    
    if not links:
        print("❌ No valid Apple Music links found in the file.")
        return
    
    print(f"✅ Found {len(links)} valid links:")
    for i, link in enumerate(links, 1):
        print(f"   {i}. {link}")
    
    # Ask for playlist combination preference
    combine_playlist = False
    if any("playlist" in link.lower() for link in links):
        choice = input("\nCombine playlists into single files? (y/n): ").strip().lower()
        combine_playlist = choice in ['y', 'yes']
    
    # Download all links
    print(f"\n🚀 Starting download of {len(links)} items...")
    print("=" * 50)
    
    for i, url in enumerate(links, 1):
        print(f"\n📥 Downloading {i}/{len(links)}...")
        download_content(url, combine_playlist)
        print(f"✅ Completed {i}/{len(links)}")
        print("-" * 30)
    
    print(f"\n🎉 All downloads completed! Total: {len(links)} items")
    print(f"📍 All files are in the 'downloads' folder")

def main():
    print("Apple Music Downloader")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\nPlease make sure all required files are in the same folder.")
        input("Press Enter to exit...")
        return
    
    print("All requirements met!")
    print("\nSupported URLs:")
    print("• Song links")
    print("• Album links") 
    print("• Playlist links")
    print("\nOptions:")
    print("1. Enter URL manually")
    print("2. Download from links.txt file")
    print("3. Exit")
    print("=" * 50)
    
    while True:
        print("\n")
        choice = input("Choose option (1/2/3): ").strip()
        
        if choice == '1':
            url = input("Paste Apple Music URL: ").strip()
            
            if not url.startswith('https://music.apple.com/'):
                print("Invalid Apple Music URL!")
                continue
            
            # Ask user preference for playlist combination
            combine_playlist = False
            if "playlist" in url.lower():
                choice = input("Combine playlist into single file? (y/n): ").strip().lower()
                combine_playlist = choice in ['y', 'yes']
            
            download_content(url, combine_playlist)
            
        elif choice == '2':
            filename = input("Enter filename (default: links.txt): ").strip()
            if not filename:
                filename = "links.txt"
            download_from_file(filename)
            
        elif choice == '3':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice! Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()