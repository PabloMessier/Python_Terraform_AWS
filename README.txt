# Project Title: AWS Account State Review with Terraform, Python, and AWS CloudTrail

## Project Overview
This project demonstrates an automated approach to deploy, manage, and destroy AWS resources using Terraform and Python. 
The primary goal is to showcase automation capabilities, integrating Python, Terraform, Git for version control, and AWS services. 
This proof-of-concept project automates the deployment of an AWS CloudTrail setup to monitor and log account activity, with an emphasis on billing and cost management data.

## Concept
The Python script acts as a wrapper to launch Terraform templates, which then create an AWS CloudTrail trail and an S3 bucket for logs storage. 
The script also includes functionality to automatically destroy the resources created, showcasing a full lifecycle management from creation to teardown. 
This project was developed to demonstrate not just the technical implementation of AWS services but also best practices in automation, version control, and infrastructure as code (IaC).

## Technologies Used
- Python for scripting
- Terraform for infrastructure as code
- AWS CloudTrail and S3 for logging and storage
- Git for version control

## How to Use
To use this project, you'll need to have Python, Terraform, and AWS CLI installed and configured on your system. Follow these steps:

1. **Clone the Repository**: `git clone [repository URL]`
2. **Install Dependencies**: Make sure Python and Terraform are installed. Use `pip` to install any required Python libraries listed in `requirements.txt`.
3. **AWS Credentials**: Ensure your AWS credentials are set up. This can be done via environment variables, AWS credentials file, or the AWS CLI.
4. **Terraform Initialization**: Navigate to the Terraform directory and run `terraform init` to initialize Terraform.
5. **Launch the Script**: Execute the main Python script to start the process. Follow on-screen instructions for any inputs required.

## Important Files and Directories
- `main.tf`: Terraform configuration file to set up AWS resources.
- `app.py`: The main Python script that orchestrates the Terraform deployment and destruction.
- `.env`: Contains environment variables for AWS access (not tracked by Git).

## Files Ignored by .gitignore
To recreate this project and achieve similar results, be aware that the following files are excluded from the repository for security and privacy reasons and need to be created manually:

- `credentials.json`: Contains AWS access key and secret key for programmatic access.
- `terraform.tfstate`: Terraform state file, contains state of resources managed by Terraform.
- `.env`: Environment variables file, stores AWS credentials and other environment-specific variables.
- `terraform.tfvars`: Contains variables for Terraform configurations, such as AWS region and bucket name.

Ensure these files are properly configured according to your AWS account and environment specifics before running the project.

## Conclusion
This project serves as a proof of concept for automating infrastructure deployment and management on AWS using Terraform and Python. 
It demonstrates the practical application of coding, cloud infrastructure management, and automation skills.

For any questions or contributions, please feel free to reach out or submit a pull request.