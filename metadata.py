import sys
from pathlib import Path
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
from io import BytesIO

def get_audio_info(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    if file_path.suffix.lower() not in ['.m4a', '.mp4']:
        print("Only supports .m4a or .mp4 files")
        return

    try:
        audio = MP4(file_path)

        # Basic audio info
        bitrate = audio.info.bitrate if hasattr(audio.info, 'bitrate') else 0
        sample_rate = audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else 0
        length = audio.info.length if hasattr(audio.info, 'length') else 0
        file_size = file_path.stat().st_size / (1024*1024)

        # Determine audio quality
        if sample_rate >= 96000:
            quality = "Hi-Res (96kHz+)"
        elif sample_rate >= 48000 and bitrate >= 2000000:
            quality = "Lossless (48kHz)"
        elif sample_rate >= 44100 and bitrate >= 1000000:
            quality = "Lossless (44.1kHz)"
        elif bitrate >= 500000:
            quality = "High Quality AAC 500kbps+"
        elif bitrate >= 320000:
            quality = "AAC 320kbps"
        else:
            quality = "AAC 256kbps or lower"

        # Metadata tags
        title = audio.get('\xa9nam', ['Unknown'])[0]
        artist = audio.get('\xa9ART', ['Unknown'])[0]
        album = audio.get('\xa9alb', ['Unknown'])[0]
        album_artist = audio.get('aART', ['Unknown'])[0]

        # Embedded album art
        covers = audio.get('covr', [])
        if covers:
            cover = covers[0]
            image_format = 'JPEG' if cover.imageformat == MP4Cover.FORMAT_JPEG else 'PNG'
            image = Image.open(BytesIO(cover))
            resolution = image.size
            cover_size = len(cover)
        else:
            image_format = None
            resolution = None
            cover_size = None

        # Print results
        print(f"File: {file_path.name}")
        print(f"Title: {title}")
        print(f"Artist: {artist}")
        print(f"Album: {album}")
        print(f"Album Artist: {album_artist}")
        print(f"Bitrate: {bitrate//1000} kbps")
        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Duration: {int(length//60)}:{int(length%60):02d}")
        print(f"File Size: {file_size:.2f} MB")
        print(f"Quality: {quality}")
        if covers:
            print(f"Embedded Album Art: {image_format}, {resolution[0]}x{resolution[1]} px, {cover_size/1024:.2f} KB")
        else:
            print("No embedded album art found")

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_audio_metadata.py <file.m4a or file.mp4>")
        sys.exit(1)

    get_audio_info(sys.argv[1])
