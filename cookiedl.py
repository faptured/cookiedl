#!/usr/bin/env python3
import os
import argparse
import subprocess
import concurrent.futures

def get_multiline_input(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

def test_cookies(cookies_file, test_link):
    print("\nTesting cookie validity using the first link...")
    # Use wget in spider mode to test the request (no file downloaded)
    result = subprocess.run(
        ["wget", "--load-cookies", cookies_file, "--spider", test_link],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print("Warning: The test request using the provided cookies failed. This may indicate that the cookies are invalid or expired.")
        return False
    print("Cookie test passed.")
    return True

def download_link(link, cookies_file, dl_path):
    # Determine output filename from the URL
    output_filename = link.split("/")[-1]
    if not output_filename:
        output_filename = "downloaded_file"
    output_file = os.path.join(dl_path, output_filename)
    print(f"\nDownloading {link} as {output_file} ...")
    try:
        subprocess.run(
            ["wget", "--load-cookies", cookies_file, "-O", output_file, link],
            check=True,
        )
        print(f"Downloaded {link} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {link}: {e}")

def main():
    # Use environment variables as defaults if defined
    default_dl_path = os.environ.get("DL_PATH", ".")
    default_cookies_file = os.environ.get("COOKIES_FILE", "cookies.txt")
    default_links_file = os.environ.get("LINKS_FILE", "links.txt")
    
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
        help="Cookies file (default: cookies.txt or COOKIES_FILE environment variable)",
    )
    parser.add_argument(
        "--links",
        type=str,
        default=default_links_file,
        help="Links file (default: links.txt or LINKS_FILE environment variable)",
    )
    args = parser.parse_args()

    # Resolve and ensure the download path exists
    dl_path = os.path.abspath(args.dl_path)
    if not os.path.exists(dl_path):
        os.makedirs(dl_path, exist_ok=True)
        print(f"Created download path: {dl_path}")
    else:
        print(f"Using download path: {dl_path}")

    # Check for cookies file; if missing, prompt for cookies input and save it.
    if not os.path.exists(args.cookies):
        cookies = get_multiline_input("Paste your cookies (end with an empty line):")
        with open(args.cookies, "w") as f:
            f.write(cookies)
        print(f"Cookies saved to {args.cookies}.")
    else:
        print(f"Using existing cookies file: {args.cookies}")

    # Check for links file; if missing, prompt for links and save them.
    if not os.path.exists(args.links):
        print("\nEnter your download links, one per line (end with an empty line):")
        links = []
        while True:
            link = input().strip()
            if link == "":
                break
            links.append(link)
        with open(args.links, "w") as f:
            for link in links:
                f.write(link + "\n")
        print(f"Links saved to {args.links}.")
    else:
        print(f"Using existing links file: {args.links}")

    # Read links from file (ignoring empty lines)
    with open(args.links, "r") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("No links found. Exiting.")
        return

    # Test cookie validity using the first link
    if not test_cookies(args.cookies, links[0]):
        proceed = input("The cookie test failed. Do you want to continue anyway? (y/n): ").strip().lower()
        if proceed != "y":
            print("Exiting.")
            return

    # Confirm download action
    download_now = input("\nDo you want to download the files now using wget? (y/n): ").strip().lower()
    if download_now == "y":
        # Download files concurrently using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(download_link, link, args.cookies, dl_path): link
                for link in links
            }
            for future in concurrent.futures.as_completed(futures):
                link = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f"Error downloading {link}: {exc}")
    else:
        print("Download skipped.")

if __name__ == "__main__":
    main()
