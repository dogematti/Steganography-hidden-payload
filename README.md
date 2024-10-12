# Steganography Hidden Payload Injector

This project allows you to dynamically inject payloads, such as reverse shells, into various media files using steganography techniques or metadata manipulation. It supports multiple media formats and provides an easy-to-use command-line interface for injecting and extracting payloads from files.

## Features
- **Dynamic Compatibility Check**: Ensures the media file is supported for payload injection.
- **Reverse Shell Payload Generation**: Dynamically generate reverse shell payloads by specifying an IP and port.
- **Steganography Injection**: Hide payloads within image files using steganography.
- **Metadata Injection**: Inject payloads into media files (e.g., images, videos, PDFs, DOCX, ZIP) using metadata fields.
- **Payload Extraction**: Extract payloads from supported media types.
- **Base64 Encoding**: Optionally encode payloads in Base64 for transport or obfuscation.
- **One-Liner Command Generation**: Create ready-to-use one-liners to extract and execute the hidden payload from a media file.

## Inspiration

This project is inspired by the ideas found in **rMETASHELL**, which provided the foundation and concept for dynamic payload injection and extraction using steganography and metadata manipulation. Thanks to **rMETASHELL** for the inspiration!

## Requirements

The following dependencies are required to run this project:

- **Python 3.x**
- **steghide** (for steganography-based injection)
- **exiftool** (for manipulating metadata in image files)
- **ffmpeg** and **ffprobe** (for handling media files such as mp4 and mp3)
- **unzip** (for extracting payloads from DOCX and ZIP files)

### Install external dependencies:

```bash
sudo apt-get install steghide exiftool ffmpeg unzip# Steganography-hidden-payload