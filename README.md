# 🍎 GAMDL — Apple Music Downloader

> A command-line app for downloading Apple Music songs, music videos, and post videos — fast, clean, and straightforward.

---

## ✨ Features

- 🎵 Download **Apple Music songs** in high quality
- 🎬 Download **music videos** and **post videos**
- 🏷️ Accurate **metadata** on every download
- 🍪 Cookie-based authentication — uses your existing Apple Music session
- ⚙️ Fully configurable via `config.json`
- 📋 Batch downloading via `links.txt`
- 🖥️ Simple command-line interface

---

## 📋 Requirements

- Python 3.8+
- An active **Apple Music subscription**
- [mp4decrypt](https://www.bento4.com/) — included as `mp4decrypt.exe`
- Valid Apple Music **cookies** (see setup below)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Finnapple/GAMDL.git
cd GAMDL
```

### 2. Configure your cookies

Export your Apple Music browser cookies and save them as `cookies.txt` in the project folder. You can use a browser extension like **Get cookies.txt LOCALLY** to do this.

### 3. Edit the config (optional)

Open `config.json` to customize download settings such as output path, quality, and more.

### 4. Add your links

Paste your Apple Music URLs into `links.txt`, one per line:

```
https://music.apple.com/...
https://music.apple.com/...
```

### 5. Run the downloader

**Windows:**
```bash
gamdl.bat
```

**Or directly with Python:**
```bash
python gamdl.py
```

---

## 🗂️ Project Structure

```
GAMDL/
├── gamdl.py          # Core downloader script
├── gamdl.bat         # Windows launcher
├── gamdl.exe         # Standalone executable
├── metadata.py       # Metadata handling
├── check.py          # Dependency/environment checker
├── config.json       # Configuration file
├── cookies.txt       # Your Apple Music cookies (required)
├── links.txt         # List of URLs to download
├── command.txt       # Reference commands
├── gamdl.txt         # Additional notes
└── mp4decrypt.exe    # Decryption tool (Bento4)
```

---

## ⚙️ Configuration

Edit `config.json` to customize behavior:

```json
{
  "output_path": "./downloads",
  "quality": "best"
}
```

> Refer to `command.txt` for available CLI options and usage examples.

---

## ⚠️ Disclaimer

This tool is intended for **personal use only**. Downloading content from Apple Music may violate their [Terms of Service](https://www.apple.com/legal/internet-services/itunes/). Use responsibly and only for content you are licensed to access. The author is not responsible for any misuse.

---

## 🤝 Contributing

Issues and pull requests are welcome!  
Feel free to open an [issue](https://github.com/Finnapple/GAMDL/issues) if you run into problems or have suggestions.

---

<p align="center">Made with ❤️ by <a href="https://github.com/Finnapple">Finnapple</a></p>
