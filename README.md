Download With Cookies
Download With Cookies is a Python utility that downloads multiple files concurrently using wget while preserving your cookies. It prompts you for cookies and download links (if not already saved), validates your cookies, and downloads files with flexible options.

Features
Cookie & Link Input:

If the cookies file does not exist, the script prompts you to paste your cookies (preserving all characters exactly as provided).
If the links file does not exist, you can paste multiple download links (one per line).
Automatic File Naming:

Default filenames for cookies, links, and logs are derived from the script's basename (e.g., if the script is named download_with_cookies.py, the defaults will be:
download_with_cookies_cookies.txt
download_with_cookies_links.txt
download_with_cookies_log.txt).
Environment Variables & Command-Line Options:

Override defaults using environment variables:
DL_PATH for the download directory.
COOKIES_FILE for the cookies file.
LINKS_FILE for the links file.
LOG_FILE for the log file.
Also available via command-line options: --dl-path, --cookies, --links, and --log.
Cookie Validation:

Tests the provided cookies on the first URL using wget’s spider mode to ensure they’re valid before starting downloads.
Download Control Options:

Skip Existing Files: By default, the script skips files that already exist.
Force Download: Use --force-download to always re-download files regardless of existence.
Prompt for Download: Use --force-download-ask to prompt for each file that already exists.
Concurrent Downloads:

Downloads files concurrently using Python’s ThreadPoolExecutor.
Logging:

Key events and errors are logged to a log file, making it easy to track the process.
Requirements
Python 3.x
wget installed and available in your system’s PATH
Installation
Clone or download the repository containing the script.
Navigate to the project directory.
Make the script executable:
bash
Copy
chmod +x download_with_cookies.py
Usage
Run the script without any arguments to use the defaults:

bash
Copy
./download_with_cookies.py
Command-Line Options
--dl-path PATH
Specify the download directory (default: current directory or the value of DL_PATH).

--cookies FILE
Specify the cookies file (default: <scriptname>_cookies.txt or the value of COOKIES_FILE).

--links FILE
Specify the links file (default: <scriptname>_links.txt or the value of LINKS_FILE).

--log FILE
Specify the log file (default: <scriptname>_log.txt or the value of LOG_FILE).

--force-download
Force download even if the file already exists.

--force-download-ask
Ask for each file if it should be downloaded when it already exists.

Environment Variables
You can set the following environment variables to override the default paths:

bash
Copy
export DL_PATH="/path/to/downloads"
export COOKIES_FILE="my_cookies.txt"
export LINKS_FILE="my_links.txt"
export LOG_FILE="my_log.txt"
Examples
Default Run:

bash
Copy
./download_with_cookies.py
Using Environment Variables:

bash
Copy
export DL_PATH="/downloads"
export COOKIES_FILE="cookies.txt"
export LINKS_FILE="links.txt"
export LOG_FILE="download_log.txt"
./download_with_cookies.py
Overriding via Command-Line:

bash
Copy
./download_with_cookies.py --dl-path /another/path --cookies custom_cookies.txt --links custom_links.txt --log custom_log.txt
Force Download Options:

Force re-download without prompt:
bash
Copy
./download_with_cookies.py --force-download
Prompt for each file if it already exists:
bash
Copy
./download_with_cookies.py --force-download-ask
How It Works
Input Handling:
If the cookies or links file does not exist, the script prompts you to paste the necessary data exactly as-is and saves it to a file.

Cookie Testing:
The script uses wget’s spider mode to test the cookies on the first URL. If the test fails, you can choose to abort or continue.

Concurrent Downloads:
Files are downloaded concurrently, with each file saved under its original filename (extracted from the URL).

Logging:
All major actions and errors are recorded in a log file for troubleshooting.

License
This project is licensed under the MIT License.

Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

This README should provide a clear overview of what the script does, how to install and use it, and what features are available.
