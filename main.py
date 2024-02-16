import subprocess
import os
import time
import sys
import json
import boto3
import logging
from colorama import init, Fore
from dotenv import load_dotenv
from json_credentials import aws_credentials

init(autoreset=True)
load_dotenv('.env')
env = os.environ.copy()

class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.WARNING:
            return Fore.YELLOW + super().format(record)
        elif record.levelno >= logging.ERROR:
            return Fore.RED + super().format(record)
        else:
            return Fore.WHITE + super().format(record)
        
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def check_os():
    platforms = {
        'linux': 'Linux',
        'linux2': 'Linux',
        'darwin': 'macOS',
        'win32': 'Windows'
    }
    return platforms.get(sys.platform, 'Unknown')

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    os.system("pause" if os.name == "nt" else "read -n 1 -s")
    
def main_tf_file():
    try:
        print("\nReview the logs of your AWS account.  ")
        logger.info("Searching for your main.tf file... ")
        time.sleep(3)
        if os.path.exists("main.tf"):
            logger.info("Found main.tf file.")
            time.sleep(1)
            launch_notice()
    except (FileNotFoundError, PermissionError, Exception, KeyError):
        print("\nERROR - Unable to process main.tf file.  ")
        print("NOTICE - Ensure that your main.tf file is in this exact directory. ")
        print("NOTICE - Ensure you also have admin permissions to access your main.tf file. ")
        pause()
        sys.exit(1)
    
def launch_notice():
    print("\nNOTICE - Terraform will require you to provide the following information: ")
    print("1) Your AWS account credentials set as environment variables ina .env file or a json file. ")
    print("2) A specific AWS region. ")
    print("3) A unique S3 bucket name. ")
    print("4) A terraform.tfvars file for the bucket name and region. ")
    print("\n")
    print("FINAL NOTE - Ensure you have proper IAM permissions to proceed. ")
    launch = None
    while not launch:
        try:
            laucnh = input("Launch Terraform template? (yes/no): ").strip().lower()
            if laucnh == 'yes':
                logger.warning("If your bucket name is not unique terraform wont be able to continue. ")
                launch_tf_template(env)
            else:
                print("Exiting... ")
                time.sleep(1)
                sys.exit(1)
        except ValueError:
            print("ERROR - Incorrect input, enter yes or no. ")
            pause()

def launch_tf_template(env):
    try:
        logger.info("Executing Terraform, please wait...")
        subprocess.run(['terraform', 'validate'], check=True, env=env)
        subprocess.run(['terraform', 'init'], check=True, env=env)
        apply_process = subprocess.run(['terraform', 'apply', '-auto-approve', '-var-file=terraform.tfvars'], check=True, env=env)
        if apply_process.returncode != 0:
            logger.error("Terraform apply failed.")
            time.sleep(3)
            logger.error(apply_process.stderr)
            execute_terraform_destroy(env)
            sys.exit(1)

        logger.info("Terraform apply successful.")
        output_process = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True, check=True, env=env)
        try:
            outputs = json.loads(output_process.stdout)
            logger.info("Terraform outputs extracted successfully.")
            bucket_name = outputs.get("s3_bucket_name", {}).get("value")
            if not bucket_name:
                logger.error("Failed to extract S3 bucket name from Terraform output.")
                pause()
                execute_terraform_destroy(env)
                sys.exit(1)
            logger.info(f"Extracted S3 bucket name: {bucket_name}")
            account_state(bucket_name)
            time.sleep(10)
            self_destroy(env)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            time.sleep(3)
            execute_terraform_destroy(env)
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        logger.error(f"Process {e.cmd} failed to execute.")
        time.sleep(3)
        sys.exit(1)
        
def account_state(bucket_name):
    print(f"Using bucket name for S3 operations: {bucket_name}")
    s3 = boto3.client('s3')
    all_logs = []
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.json'):  # Adjust this condition as needed
                log_file = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                log_contents = log_file['Body'].read().decode('utf-8')
                all_logs.append(json.loads(log_contents))
    except Exception as e:
        logger.error(f"Error retrieving logs from S3: {e}")
        return None

    if all_logs:
        # Save to a JSON file
        with open('cloudtrail_logs.json', 'w') as outfile:
            json.dump(all_logs, outfile, indent=4)
    else:
        print("No logs found.")
        time.sleep(2)

    return all_logs
                
def self_destroy(env):
    termination = 60
    logger.warning("Auto-destroy sequence initiated...")
    while termination > 0:
        print(f"\rSelf-destroying in {termination} seconds...", end="", flush=True)
        time.sleep(1)  # Adjust as needed for timing
        termination -= 1
        if termination == 0:
            execute_terraform_destroy(env)
    
def execute_terraform_destroy(env):
    try:
        print("\n")
        logger.info("Executing terraform destroy -auto-approve. ")
        subprocess.run(["terraform", "destroy", "-auto-approve"], check=True, env=env)
        logger.info("Terraform IaC template destroyed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to destroy Terraform template initially: {e}")
        retry_destroy_with_backoff(env)
    finally:
        try_again()

def retry_destroy_with_backoff(env):
    max_retries = 5
    time.sleep(3)  # Initial delay before starting retries
    for attempt in range(max_retries):
        logger.info(f"Attempting to destroy Terraform template (Attempt {attempt + 1}/{max_retries})...")
        try:
            subprocess.run(["terraform", "destroy", "-auto-approve"], check=True, env=env)
            logger.info("Terraform IaC template destroyed successfully on retry.")
            return  # Exit the retry function upon success
        except subprocess.CalledProcessError as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:  # No need to sleep after the last attempt
                sleep_time = 60 * (attempt + 1)
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

    logger.error("Exceeded maximum retry attempts for Terraform destroy.")
    sys.exit(1)
    
def try_again():
    retry = None
    while not retry:
        try:
            retry = input("Would you like to try again? (yes/no): ").strip().lower()
            if retry == 'yes':
                clear_terminal()
                main_tf_file()
            else:
                print("Exiting...")
                time.sleep(1)
                sys.exit(1)
        except ValueError:
            print("ERROR - Incorrect input, enter yes or no.")
            pause()
            
def main():
    os_type = check_os()
    if os_type not in check_os():
        print("\nERROR - Unsupported OS.  ")
        pause()
        sys.exit(1)
    
    aws_credentials()
    main_tf_file()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user, exiting... ")
        time.sleep(1)
        sys.exit()