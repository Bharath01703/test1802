import os
import pandas as pd
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set download directory
download_dir = "/tmp"  # Temporary directory for cloud environments
os.makedirs(download_dir, exist_ok=True)

# Initialize WebDriver with headless settings (no local download)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless to avoid GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set download preferences for Chrome (to download directly to specified directory)
prefs = {
    "download.default_directory": download_dir,  # Specify the download folder
    "download.prompt_for_download": False,       # Disable the prompt for file download
    "directory_upgrade": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
driver.maximize_window()

def login():
    """Log in to Bizom using environment variables for credentials."""
    try:
        username = os.getenv("BIZOM_USERNAME")
        password = os.getenv("BIZOM_PASSWORD")
        if not username or not password:
            raise ValueError("Bizom credentials not set in environment variables.")

        username_field = driver.find_element(By.XPATH, "//input[@placeholder='Username']")
        password_field = driver.find_element(By.XPATH, "//input[@placeholder='Password']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        print("Logged in successfully!")
    except Exception as e:
        print("Login failed:", e)
        driver.quit()
        exit()

# Navigate to Bizom login page and log in
driver.get("https://reports.bizom.in/users/login")
login()

# Navigate to the report page
driver.get("https://reports.bizom.in/reports/view/14085")

current_url = driver.current_url
if "login" in current_url:
    print("Redirected to login page again. Logging in again...")
    login()
time.sleep(5)

# Redirect to a specific URL if required
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

# Wait time to allow the file to download
time.sleep(20)

# Check the downloaded file type
downloaded_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
if downloaded_files:
    latest_file = max(downloaded_files, key=os.path.getctime)
    print(f"File downloaded: {latest_file}")

    # Convert file to CSV if it is Excel file
    if latest_file.endswith(".xlsx") or latest_file.endswith(".xls"):
        print("Converting Excel to CSV...")
        try:
            df = pd.read_excel(latest_file)
            csv_file_path = latest_file.replace('.xlsx', '.csv').replace('.xls', '.csv')
            df.to_csv(csv_file_path, index=False)
            print(f"Converted to CSV: {csv_file_path}")
            latest_file = csv_file_path  # Update to the new CSV file path
        except Exception as e:
            print(f"Failed to convert Excel to CSV: {e}")
    else:
        print("File is not an Excel file. No conversion applied.")
else:
    print("No file downloaded.")

driver.quit()

def upload_to_s3(file_name, bucket_name, s3_key):
    """Upload the file to S3 using environment variables for AWS credentials."""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        with open(file_name, 'rb') as file_data:
            s3.upload_fileobj(file_data, bucket_name, s3_key)
        print(f"File uploaded to S3 bucket '{bucket_name}' with key '{s3_key}'.")
    except Exception as e:
        print("Failed to upload to S3:", e)

# Upload the downloaded file to S3
bucket_name = "attendance3122024"
if downloaded_files:
    s3_key = f"attendance/{os.path.basename(latest_file)}"
    upload_to_s3(latest_file, bucket_name, s3_key)
else:
    print("No file downloaded to upload.")
