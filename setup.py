import time
import sqlite3
from colorama import Fore, Style, init
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Initialize colorama for colored output
init(autoreset=True)

# Ask for the URL with a colored prompt
print(Fore.YELLOW + "Please paste the URL of the Mega folder (format: https://www.mediafire.com/folder/.....)" + Style.RESET_ALL)
URL = input(Fore.GREEN + "Your URL: " + Style.RESET_ALL)

# Set up Chrome options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start the driver
driver = uc.Chrome(options=options)

# Database setup
db_name = "down_page_links.db"
table_name = "links"

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL
)
""")
conn.commit()

# Start the process
try:
    print(Fore.CYAN + "Connecting to MediaFire..." + Style.RESET_ALL)
    driver.get(URL)
    time.sleep(5)

    # Locate elements on the page
    elements = driver.find_elements(By.CLASS_NAME, "item-name")
    print(Fore.GREEN + f"Found {len(elements)} items to process." + Style.RESET_ALL)

    # Process each item
    for idx, element in enumerate(elements, start=1):
        try:
            print(Fore.YELLOW + f"Processing item {idx}/{len(elements)}: {element.text}" + Style.RESET_ALL)
            start_time = time.time()

            # Click and switch to new tab
            element.click()
            driver.switch_to.window(driver.window_handles[-1])

            # Capture the download URL
            download_url = driver.current_url.split("file?")[0]
            cursor.execute(f"INSERT INTO {table_name} (url) VALUES (?)", (download_url,))
            conn.commit()

            elapsed_time = time.time() - start_time
            print(Fore.GREEN + f"Captured URL: {download_url}" + Style.RESET_ALL)

            # Close the tab and return to the main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(Fore.RED + f"Error processing item {idx}: {e}" + Style.RESET_ALL)

finally:
    # Clean up resources
    time.sleep(1)
    driver.quit()
    conn.close()

# Final message
print(Fore.CYAN + f"All captured URLs have been stored in {db_name}" + Style.RESET_ALL)
print(Fore.CYAN + f"Next step : please execute main.py to start downloading." + Style.RESET_ALL)
