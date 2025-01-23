
# Mega Folder Downloader

This project allows you to scrape and download video files from a MediaFire folder. It is composed of two main scripts:

- `setup.py`: Initializes a database with download links.
- `main.py`: Downloads the video files using the links stored in the database.

## Requirements

Before running the scripts, ensure you have the following Python libraries installed:

- `undetected-chromedriver`
- `selenium`
- `requests`
- `colorama`
- `sqlite3`
- `tqdm`

You can install them using pip:

```bash
pip install undetected-chromedriver selenium requests colorama tqdm
```

## Setup Instructions

### 1. Run `setup.py`

The `setup.py` script is responsible for connecting to a MediaFire folder, scraping the download links for video files, and storing them in a SQLite database.

#### Instructions:

1. Run the script:

   ```bash
   python setup.py
   ```

2. When prompted, enter the URL of the MediaFire folder (e.g., `https://www.mediafire.com/folder/.....`).
3. The script will scrape the items in the folder, capture the video download links, and save them in the `down_page_links.db` database.

### 2. Run `main.py`

After running `setup.py`, run `main.py` to start the download process.

#### Instructions:

1. Run the script:

   ```bash
   python main.py
   ```

2. The script will fetch all download links from the database and begin downloading the video files. A progress bar will display the status of each file being downloaded.

3. All downloaded files will be saved in a `downloads` folder.

### 3. Cleanup

Once the download process is completed, the script will clean up the temporary files created during the process (`temp_download_page_links.html` and `down_page_links.db`).

## Limitations

- **Folder Content Limitation**: The current version of the project only supports MediaFire folders that **contain only video files**. Image or other types of files will not be processed for download as they are rendered directly in the browser on MediaFire.
- **ChromeDriver Issues**: There may be warnings or errors related to the version of the ChromeDriver at the end of each script run. These warnings can be safely ignored as they do not affect the functionality of the script.

## How it works

1. **`setup.py`**:
   - It prompts the user for a MediaFire folder URL.
   - It scrapes the page for item links and extracts the download URL for video files.
   - The download URLs are stored in a SQLite database (`down_page_links.db`).

2. **`main.py`**:
   - It reads the database for saved URLs.
   - It launches a browser using `undetected-chromedriver` to bypass detection mechanisms.
   - For each URL, it captures the direct download link and stores it.
   - It proceeds to download each file with a progress bar showing download progress.

## Notes

- If you don't run `setup.py` first, `main.py` will display an error.
- Ensure you have the necessary permissions to download from the MediaFire folder.
- The browser will run in headless mode (no UI) by default to speed up the process.
- **Warnings/Errors**: If you encounter warnings or errors related to ChromeDriver’s current version, they can be ignored. These warnings do not impact the functionality of the script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
