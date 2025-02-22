#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import concurrent.futures
import logging
from urllib.parse import urlparse, unquote

def log_and_print(message):
    print(message)
    logging.info(message)

def get_multiline_input(prompt):
    log_and_print(prompt)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

def test_cookies(cookies_file, test_link):
    log_and_print("\nTesting cookie validity using the first link...")
    result = subprocess.run(
        ["wget", "--load-cookies", cookies_file, "--spider", test_link],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        log_and_print("Warning: The test request using the provided cookies failed. This may indicate that the cookies are invalid or expired.")
        return False
    log_and_print("Cookie test passed.")
    return True

def download_link(link, cookies_file, dl_path, force_download, force_download_ask):
    # Parse the URL to extract a clean filename
    parsed = urlparse(link)
    output_filename = os.path.basename(parsed.path)
    output_filename = unquote(output_filename)
    if not output_filename:
        output_filename = "downloaded_file"
    output_file = os.path.join(dl_path, output_filename)
    
    # Check if file already exists
    if os.path.exists(output_file):
        if force_download_ask:
            answer = input(f"File '{output_file}' already exists. Download again? (y/n): ").strip().lower()
            if answer != "y":
                log_and_print(f"Skipping {link} because file {output_file} already exists.")
                return
        elif force_download:
            log_and_print(f"File '{output_file}' exists, but force download is enabled. Redownloading...")
        else:
            log_and_print(f"Skipping {link} because file {output_file} already exists.")
            return

    log_and_print(f"\nDownloading {link} as {output_file} ...")
    try:
        subprocess.run(
            ["wget", "--load-cookies", cookies_file, "-O", output_file, link],
            check=True,
        )
        log_and_print(f"Downloaded {link} successfully.")
    except subprocess.CalledProcessError as e:
        log_and_print(f"Error downloading {link}: {e}")

def main():
    # Derive the base name from the program's filename.
    try:
        basename = os.path.splitext(os.path.basename(__file__))[0]
    except NameError:
        basename = "program"
    
    # Environment variable defaults
    default_dl_path = os.environ.get("DL_PATH", ".")
    default_cookies_file = os.environ.get("COOKIES_FILE", f"{basename}_cookies.txt")
    default_links_file = os.environ.get("LINKS_FILE", f"{basename}_links.txt")
    default_log_file = os.environ.get("LOG_FILE", f"{basename}_log.txt")
    
    parser = argparse.ArgumentParser(
        description="Download files concurrently using cookies and links files."
    )
    parser.add_argument(
        "--dl-path",
        type=str,
        default=default_dl_path,
        help="Download path (default: current directory or DL_PATH environment variable)",
    )
    parser.add_argument(
        "--cookies",
        type=str,
        default=default_cookies_file,
        help="Cookies file (default: derived from program name or COOKIES_FILE environment variable)",
    )
    parser.add_argument(
        "--links",
        type=str,
        default=default_links_file,
        help="Links file (default: derived from program name or LINKS_FILE environment variable)",
    )
    parser.add_argument(
        "--log",
        type=str,
        default=default_log_file,
        help="Log file (default: derived from program name or LOG_FILE environment variable)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force download even if file exists",
    )
    parser.add_argument(
        "--force-download-ask",
        action="store_true",
        help="Ask for each file if it should be downloaded even if it exists",
    )
    args = parser.parse_args()

    # Configure logging to the log file.
    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    log_and_print(f"Log file created: {args.log}")

    # Resolve and ensure the download path exists.
    dl_path = os.path.abspath(args.dl_path)
    if not os.path.exists(dl_path):
        os.makedirs(dl_path, exist_ok=True)
        log_and_print(f"Created download path: {dl_path}")
    else:
        log_and_print(f"Using download path: {dl_path}")

    # If cookies file doesn't exist, prompt and save cookies exactly as pasted.
    if not os.path.exists(args.cookies):
        cookies = get_multiline_input("Paste your cookies (end with an empty line):")
        with open(args.cookies, "w") as f:
            f.write(cookies)
        log_and_print(f"Cookies saved to {args.cookies}.")
    else:
        log_and_print(f"Using existing cookies file: {args.cookies}")

    # If links file doesn't exist, prompt and save links exactly as pasted.
    if not os.path.exists(args.links):
        log_and_print("\nEnter your download links, one per line (end with an empty line):")
        links = []
        while True:
            link = input().strip()
            if link == "":
                break
            links.append(link)
        with open(args.links, "w") as f:
            for link in links:
                f.write(link + "\n")
        log_and_print(f"Links saved to {args.links}.")
    else:
        log_and_print(f"Using existing links file: {args.links}")

    # Read links from file (ignoring empty lines)
    with open(args.links, "r") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        log_and_print("No links found. Exiting.")
        sys.exit(1)

    # Test cookie validity using the first link.
    if not test_cookies(args.cookies, links[0]):
        proceed = input("The cookie test failed. Do you want to continue anyway? (y/n): ").strip().lower()
        if proceed != "y":
            log_and_print("Exiting.")
            sys.exit(1)

    download_now = input("\nDo you want to download the files now using wget? (y/n): ").strip().lower()
    if download_now == "y":
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(download_link, link, args.cookies, dl_path, args.force_download, args.force_download_ask): link
                for link in links
            }
            for future in concurrent.futures.as_completed(futures):
                link = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    log_and_print(f"Error downloading {link}: {exc}")
    else:
        log_and_print("Download skipped.")

if __name__ == "__main__":
    main()
