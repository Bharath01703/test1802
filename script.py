import os
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Bizom credentials hardcoded (as per the provided values)
BIZOM_USERNAME = "6361219727"
BIZOM_PASSWORD = "Swastiks#2024"

# AWS credentials read from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Check if AWS credentials are set
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("AWS credentials are not set in environment variables.")
else:
    print("AWS credentials are set.")

# Check if Bizom credentials are set
if not BIZOM_USERNAME or not BIZOM_PASSWORD:
    print("Bizom credentials are not set in the script.")
else:
    print("Bizom credentials are set.")

# Logic for Bizom login using Selenium (example)
if not BIZOM_USERNAME or not BIZOM_PASSWORD:
    raise ValueError("Bizom credentials not set in the script.")

# Initialize the webdriver for Bizom login (using Chrome in this example)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
driver = webdriver.Chrome(options=options)

# Navigate to Bizom login page
driver.get("https://app.bizom.com/login")

# Locate the username and password fields and input credentials
username_field = driver.find_element(By.ID, "username")  # Replace with actual field ID
password_field = driver.find_element(By.ID, "password")  # Replace with actual field ID

username_field.send_keys(BIZOM_USERNAME)
password_field.send_keys(BIZOM_PASSWORD)

# Click the login button (replace with actual button selector)
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()

# Wait for the page to load after login
time.sleep(5)  # Adjust if necessary

# Check if login was successful (replace with actual check)
if "dashboard" in driver.current_url:
    print("Successfully logged in to Bizom!")
else:
    print("Login failed. Please check your credentials.")

# Logic for AWS SDK (e.g., using Boto3 to interact with AWS)
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    # Initialize the AWS session using Boto3
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1"  # Replace with your desired region
    )

    # Example: List S3 buckets
    s3_client = session.client('s3')
    response = s3_client.list_buckets()

    print("AWS S3 Buckets:")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

# Close the browser
driver.quit()
