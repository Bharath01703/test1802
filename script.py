import os
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Specify download directory
download_dir = "C:\\temp"
os.makedirs(download_dir, exist_ok=True)

# Initialize WebDriver without headless mode (for debugging)
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set download preferences
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
driver.maximize_window()

# Login Function
def login():
    try:
        username_field = driver.find_element(By.XPATH, "//input[@placeholder='Username']")
        password_field = driver.find_element(By.XPATH, "//input[@placeholder='Password']")
        username_field.send_keys("6361219727")
        password_field.send_keys("Swastiks#2024")
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        print("Logged in successfully!")
    except Exception as e:
        print("Login failed:", e)
        driver.quit()
        exit()

# Navigate and Login
driver.get("https://reports.bizom.in/users/login")
login()

# Go to Report Page
driver.get("https://reports.bizom.in/reports/view/14085")
if "login" in driver.current_url:
    print("Redirected to login page again. Logging in again...")
    login()

# Click Update and Download
try:
    update_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "reportsUpdateButton"))
    )
    update_button.click()
    print("Update button clicked successfully!")

    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "option-dropdown"))
    )
    dropdown.click()
    print("Dropdown clicked successfully!")

    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "downloadReportIcon"))
    )
    download_button.click()
    print("Download button clicked successfully!")
except Exception as e:
    print("Error during update or download process:", e)

# Wait for download
time.sleep(20)

# Check if file downloaded
def check_download():
    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
    if files:
        latest_file = max(files, key=os.path.getctime)
        print(f"File downloaded: {latest_file}")
        return latest_file
    print("No file downloaded.")
    return None

downloaded_file = check_download()

# Fallback Download with Requests (if URL known)
def download_with_requests(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            print(f"File downloaded using requests: {save_path}")
            return save_path
    except Exception as e:
        print(f"Failed to download with requests: {e}")
    return None

# Replace `file_url` with the direct file link if identified
file_url = None
if not downloaded_file and file_url:
    downloaded_file = download_with_requests(file_url, os.path.join(download_dir, "fallback_download.csv"))

driver.quit()

# Convert to CSV if needed (additional logic here)
if downloaded_file:
    print(f"Proceed with file: {downloaded_file}")
else:
    print("Download failed. No file to process.")
