import os
import pandas as pd
import boto3
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Specify download directory
download_dir = "/tmp"  # Use a standard directory for cloud-based environments
os.makedirs(download_dir, exist_ok=True)

# Initialize WebDriver with headless settings (no local download)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless to avoid GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set download preferences for Chrome (to download directly to specified directory)
prefs = {
    "download.default_directory": download_dir,  # Specify the download folder
    "download.prompt_for_download": False,  # Disable the prompt for file download
    "directory_upgrade": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
driver.maximize_window()

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

driver.get("https://reports.bizom.in/users/login")
login()

driver.get("https://reports.bizom.in/reports/view/14085")

current_url = driver.current_url
if "login" in current_url:
    print("Redirected to login page again. Logging in again...")
    login()
time.sleep(5)

redirected_url = driver.current_url
if redirected_url != "https://reports.bizom.in/reports/view/14085?url=reports/view/14085&access_token=Xed2cvyDvk3rwbFnJuqSs5VzSpERSnNUTXQThFIs":
    driver.get("https://reports.bizom.in/reports/view/14085?url=reports/view/14085&access_token=Xed2cvyDvk3rwbFnJuqSs5VzSpERSnNUTXQThFIs")
    time.sleep(3)

# Clicking the Update Button
try:
    update_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "reportsUpdateButton"))
    )
    update_button.click()
    print("Update button clicked successfully!")
except Exception as e:
    print("Failed to click the Update button:", e)

time.sleep(5)

# Clicking the Download Dropdown
try:
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "option-dropdown"))
    )
    dropdown.click()
    print("Dropdown clicked successfully!")
except Exception as e:
    print("Failed to click the dropdown:", e)

# Clicking the Download Button
try:
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "downloadReportIcon"))
    )
    download_button.click()
    print("Download button clicked successfully!")
except Exception as e:
    print("Failed to click the download button:", e)

# Wait for file to download (20 seconds)
time.sleep(20)

# Check and convert downloaded file to CSV
def convert_to_csv(file_path):
    csv_file_path = file_path.rsplit('.', 1)[0] + '.csv'
    try:
        # Handle Excel files
        if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            df = pd.read_excel(file_path)
        # Handle text files
        elif file_path.endswith(".txt") or file_path.endswith(".csv"):
            df = pd.read_csv(file_path, sep=None, engine='python')  # Auto-detect separator
        else:
            raise ValueError("Unsupported file format. Unable to convert.")
        # Save as CSV
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print(f"Converted to CSV: {csv_file_path}")
        return csv_file_path
    except Exception as e:
        print(f"Failed to convert file to CSV: {e}")
        return None

downloaded_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
if downloaded_files:
    latest_file = max(downloaded_files, key=os.path.getctime)
    print(f"File downloaded: {latest_file}")
    csv_file = convert_to_csv(latest_file)
else:
    print("No file downloaded.")
    csv_file = None

driver.quit()

# Upload to S3 Function
def upload_to_s3(file_name, bucket_name, s3_key):
    try:
        s3 = boto3.client('s3', aws_access_key_id='AKIAZ3MGNBTBUTZ4UNEJ', aws_secret_access_key='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')
        with open(file_name, 'rb') as file_data:
            s3.upload_fileobj(file_data, bucket_name, s3_key)
        print(f"File uploaded to S3 bucket '{bucket_name}' with key '{s3_key}'.")
    except Exception as e:
        print("Failed to upload to S3:", e)

# Set S3 Bucket and Key
bucket_name = "attendance3122024"

if csv_file:
    s3_key = f"attendance/{os.path.basename(csv_file)}"
    upload_to_s3(csv_file, bucket_name, s3_key)
else:
    print("No file converted to CSV to upload.")
