import json
import os

def pause():
    os.system("pause" if os.name == "nt" else "read -n 1 -s")

def aws_credentials(json_file_path="credentials.json"):
    try:
        with open(json_file_path, 'r') as json_file:
            credentials = json.load(json_file)
            os.environ['AWS_ACCESS_KEY_ID'] = credentials['AWS_ACCESS_KEY_ID']
            os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['AWS_SECRET_ACCESS_KEY']
    except Exception as e:
        print(f"Error loading AWS credentials: {e}")
        pause()
        sys.exit(1)
    except FileNotFoundError:
        logger.error("AWS Credentials not found in credentials.json ")
        pause()
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in credentials.json")
        pause()
        sys.exit(1)
    except KeyError:
        logger.error("Missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY in credentials.json")
        pause()
        sys.exit(1)
    except PermissionError:
        logger.error("You do not have permission to access the credentials.json file.")
        pause()
        sys.exit(1)