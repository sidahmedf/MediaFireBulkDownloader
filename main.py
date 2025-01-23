import os
import requests
import sqlite3
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm  # For the progress bar

if not os.path.exists('down_page_links.db'):
    print("\033[1;31mError: Please launch setup.py first to initialize the database.\033[0m")

print("\033[1;34mStarting the download process...\033[0m")

options = uc.ChromeOptions()
#options.add_argument("--headless")  # Run in headless mode (no UI)
options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
options.add_argument("--no-sandbox")  # Disable sandboxing (for certain environments)
options.add_argument("--disable-dev-shm-usage")  # Fixes issues with Docker

# Fetch all links from the database
db_path = "down_page_links.db"
print(f"\033[1;33mFetching links from database: {db_path}\033[0m")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM links")  # Fetch all URLs
    results = cursor.fetchall()
    conn.close()
    if results:
        download_page_urls = [result[0] for result in results]  # List of URLs
        print(f"\033[1;32mFetched {len(download_page_urls)} links.\033[0m")
    else:
        raise Exception("No links found in the database!")
except Exception as e:
    print(f"\033[1;31mError accessing database: {e}\033[0m")
    exit(1)

# Create a temporary HTML file with the download page links
html_file_path = "temp_download_page_links.html"
with open(html_file_path, "w") as f:
    f.write("<html><body>")
    for url in download_page_urls:
        f.write(f'<a href="{url}" target="_blank">{url}</a><br>')  # Open links in a new tab
    f.write("</body></html>")

# Launch browser
print('\033[1;33mLaunching the browser...\033[0m')
print('\033[1;34mPlease stand by, the browser will shut itself down after completing the tasks.\033[0m')
driver = uc.Chrome(options=options)

download_links = []
try:
    driver.get(f"file:///{os.path.abspath(html_file_path)}")  # Open the HTML file locally
    sleep(1)

    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"\033[1;32mFound {len(links)} links in database.\033[0m")

    for link in links:
        link.click()  # Links will open in new tabs due to target="_blank"
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
        sleep(1)  # Give the page time to load

        try:
            cookie_button = driver.find_element(By.ID, value="ez-accept-all")
            cookie_button.click()
        except Exception:
            pass  # No cookie button, proceed silently

        try:
            download_button = driver.find_element(By.ID, value="downloadButton")
            download_link = download_button.get_attribute("href")
            download_links.append(download_link)
        except Exception as e:
            print(f"Error fetching download link for {link.text}: {e}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the main tab
finally:
    driver.quit()
    if os.path.exists(html_file_path):
        os.remove(html_file_path)
    if os.path.exists('down_page_links.db'):
        os.remove('down_page_links.db')

# Total number of files to download
total_files = len(download_links)
print(f"\033[1;33mStarting download of {total_files} file(s)...\033[0m")

# List to store download statistics for later
all_downloaded_files = []

# Loop through all the fetched download links and process each
for index, download_link in enumerate(download_links, start=1):
    # Define download folder
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    # Define the file name and path
    file_name = download_link.split("/")[-1]  # Extract file name from the link
    file_path = os.path.join(download_folder, file_name)

    headers = {
        "Connection": "keep-alive"
    }

    response = requests.get(download_link, stream=True, headers=headers)
    if response.status_code == 200:
        total_size = int(response.headers.get("Content-Length", 0))  # Get the total file size
        chunk_size = 8192  # Increased chunk size for faster download
        with open(file_path, "wb") as file, tqdm(
                desc=f"Downloading {index}/{total_files}: \033[1;34m{file_name}\033[0m",  # File number and name
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                bar_format="{l_bar}{bar:50}{r_bar}",  # Keeps the bar on a single line
                colour="cyan"  # Progress bar color
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                progress_bar.update(len(chunk))

        all_downloaded_files.append((file_name, total_size))
    else:
        print("\033[1;31mFailed to download the file. Status code:\033[0m", response.status_code)

# After all downloads, print the summary report
print("\n\033[1;32mDownload Process Completed.\033[0m")
total_size_mb = 0
for file_name, size in all_downloaded_files:
    total_size_mb += size / 1024 / 1024  # Convert to MB
print(f"\033[1;36mTotal Files Downloaded: {total_files}\033[0m")
print(f"\033[1;36mTotal Size of All Downloads: {total_size_mb:.2f} MB\033[0m")
print(f"\033[1;36mPlease check your '/downloads' folder for the downloaded files.\033[0m")
