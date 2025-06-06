import subprocess
import sys
import uuid
import os

def run_cmd(cmd):
    result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE,
            text=True,
            stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        return ""

    return result.stdout.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python yt_merge.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]

    print("[*] Getting video and audio URLs using yt-dlp...")
    raw_output = run_cmd(["yt-dlp", "-g", url])
    lines = raw_output.splitlines()
    if len(lines) != 2:
        print("[-] Expected 2 URLs (video and audio), got:", len(lines))
        sys.exit(1)

    video_url, audio_url = lines
    print("[+] Video URL:", video_url[:60] + "...")
    print("[+] Audio URL:", audio_url[:60] + "...")

    filename = f"output_{uuid.uuid4().hex[:8]}.mp4"

    print("[*] Merging with ffmpeg...")
    run_cmd([
        "ffmpeg",
        "-y",  # Overwrite output if exists
        "-i", video_url,
        "-i", audio_url,
        "-c", "copy",
        filename
    ])

    print(f"[+] Done! Merged file saved as: {filename}")

if __name__ == "__main__":
    main()

