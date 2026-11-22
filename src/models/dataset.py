"""Curated technical dataset covering all possibilities for AWS Technical Support query classification."""

TRAINING_DATA = [
    # ========================================================
    # 1. TROUBLESHOOTING (Amazon EC2)
    # ========================================================
    {"query": "How do I fix a Permission denied (publickey) error when connecting to EC2?", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "HIGH"},
    {"query": "EC2 instance is unreachable via SSH port 22 connection timed out", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "HIGH"},
    {"query": "My EC2 instance 2/2 status checks failed system status check error", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "CRITICAL"},
    {"query": "Troubleshoot EC2 instance reboot loop after kernel update", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "CRITICAL"},
    {"query": "How to resolve Host key verification failed when connecting to EC2", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "MEDIUM"},
    {"query": "EC2 instance stuck in stopping state how do I force terminate it", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "HIGH"},
    {"query": "Fix EC2 insufficient instance capacity error when launching in availability zone", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "HIGH"},
    {"query": "EC2 CPU utilization 100 percent how do I diagnose runaway processes", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "CRITICAL"},
    {"query": "EC2 EBS root volume is full disk space 100 percent how to resize filesystem", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "HIGH"},
    {"query": "Connection refused on port 80 nginx web server running on EC2", "intent": "TROUBLESHOOTING", "service": "Amazon EC2", "urgency": "HIGH"},

    # ========================================================
    # 2. TROUBLESHOOTING (Amazon S3)
    # ========================================================
    {"query": "How do I troubleshoot a NoSuchBucket error in Amazon S3?", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "HIGH"},
    {"query": "S3 403 AccessDenied error when downloading object with aws s3 cp", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "HIGH"},
    {"query": "Fix The specified key does not exist NoSuchKey error in S3", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "MEDIUM"},
    {"query": "Amazon S3 SlowDown 503 Please reduce your request rate 503 error", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "HIGH"},
    {"query": "S3 multipart upload failed with EntityTooLarge exception", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "MEDIUM"},
    {"query": "CORS error No Access-Control-Allow-Origin header present on S3 bucket", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "HIGH"},
    {"query": "S3 bucket delete fails because bucket is not empty how to purge all versions", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "MEDIUM"},
    {"query": "SignatureDoesNotMatch error when generating presigned URL in S3", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "HIGH"},
    {"query": "S3 replication failing between source and destination buckets", "intent": "TROUBLESHOOTING", "service": "Amazon S3", "urgency": "HIGH"},

    # ========================================================
    # 3. TROUBLESHOOTING (AWS Lambda)
    # ========================================================
    {"query": "How to resolve Task timed out after 3.00 seconds in AWS Lambda?", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "CRITICAL"},
    {"query": "AWS Lambda runtime error Process exited before completing request", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "CRITICAL"},
    {"query": "Lambda Out of Memory error Runtime.OutOfMemory error 128MB exceeded", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "CRITICAL"},
    {"query": "Troubleshoot Lambda ENI creation failure inside private VPC subnet", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "HIGH"},
    {"query": "AWS Lambda cold start latency is too high how to optimize execution time", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "MEDIUM"},
    {"query": "Fix Lambda Cannot find module index.js in deployment package", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "HIGH"},
    {"query": "Lambda concurrency limit reached 429 TooManyRequestsException throttling", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "CRITICAL"},
    {"query": "Lambda function not getting triggered by S3 bucket ObjectCreated event", "intent": "TROUBLESHOOTING", "service": "AWS Lambda", "urgency": "HIGH"},

    # ========================================================
    # 4. TROUBLESHOOTING (AWS IAM)
    # ========================================================
    {"query": "Fix is not authorized to perform sts:AssumeRole on resource in IAM", "intent": "TROUBLESHOOTING", "service": "AWS IAM", "urgency": "CRITICAL"},
    {"query": "IAM user getting AccessDenied on s3:PutObject despite having policy attached", "intent": "TROUBLESHOOTING", "service": "AWS IAM", "urgency": "HIGH"},
    {"query": "Explicit deny in SCP overrides IAM permission boundary how to resolve", "intent": "TROUBLESHOOTING", "service": "AWS IAM", "urgency": "CRITICAL"},
    {"query": "Cannot delete IAM role because instance profile is still attached", "intent": "TROUBLESHOOTING", "service": "AWS IAM", "urgency": "MEDIUM"},
    {"query": "IAM Access key inactive or deleted error when running aws configure", "intent": "TROUBLESHOOTING", "service": "AWS IAM", "urgency": "HIGH"},
    {"query": "Fix MalformedPolicyDocument statement missing Effect or Action parameter", "intent": "TROUBLESHOOTING", "service": "AWS IAM", "urgency": "HIGH"},

    # ========================================================
    # 5. CONFIGURATION & SETUP
    # ========================================================
    {"query": "How do I configure an S3 lifecycle policy to transition to Glacier?", "intent": "CONFIGURATION_SETUP", "service": "Amazon S3", "urgency": "MEDIUM"},
    {"query": "Step-by-step guide to attach an IAM role to an EC2 instance", "intent": "CONFIGURATION_SETUP", "service": "Amazon EC2", "urgency": "MEDIUM"},
    {"query": "How to configure a Lambda function to access resources in private VPC", "intent": "CONFIGURATION_SETUP", "service": "AWS Lambda", "urgency": "HIGH"},
    {"query": "How to set up S3 Cross-Origin Resource Sharing (CORS) rule JSON", "intent": "CONFIGURATION_SETUP", "service": "Amazon S3", "urgency": "MEDIUM"},
    {"query": "Configure EC2 security group rules for inbound HTTP 80 and HTTPS 443", "intent": "CONFIGURATION_SETUP", "service": "Amazon EC2", "urgency": "MEDIUM"},
    {"query": "How to set up provisioned concurrency for AWS Lambda function", "intent": "CONFIGURATION_SETUP", "service": "AWS Lambda", "urgency": "MEDIUM"},
    {"query": "How to configure IAM password policy requiring uppercase and special symbols", "intent": "CONFIGURATION_SETUP", "service": "AWS IAM", "urgency": "LOW"},
    {"query": "Set up S3 static website hosting with custom index.html and error.html", "intent": "CONFIGURATION_SETUP", "service": "Amazon S3", "urgency": "LOW"},
    {"query": "Configure EC2 user data bash script to automatically install docker", "intent": "CONFIGURATION_SETUP", "service": "Amazon EC2", "urgency": "MEDIUM"},
    {"query": "How to attach an IAM policy to an IAM user group in AWS console", "intent": "CONFIGURATION_SETUP", "service": "AWS IAM", "urgency": "LOW"},

    # ========================================================
    # 6. CLI & SCRIPT GENERATION
    # ========================================================
    {"query": "Give me the aws s3 sync command to copy local files to an S3 bucket", "intent": "CLI_SCRIPT_GENERATION", "service": "Amazon S3", "urgency": "MEDIUM"},
    {"query": "Show me aws ec2 describe-instances command filtered by running state", "intent": "CLI_SCRIPT_GENERATION", "service": "Amazon EC2", "urgency": "MEDIUM"},
    {"query": "CLI command to invoke a Lambda function asynchronously and save output", "intent": "CLI_SCRIPT_GENERATION", "service": "AWS Lambda", "urgency": "MEDIUM"},
    {"query": "Give me aws iam create-role command with assume role trust policy JSON", "intent": "CLI_SCRIPT_GENERATION", "service": "AWS IAM", "urgency": "MEDIUM"},
    {"query": "How to upload a file to S3 using Python boto3 upload_file snippet", "intent": "CLI_SCRIPT_GENERATION", "service": "Amazon S3", "urgency": "LOW"},
    {"query": "Bash script using AWS CLI to stop all EC2 instances with tag Environment=Dev", "intent": "CLI_SCRIPT_GENERATION", "service": "Amazon EC2", "urgency": "MEDIUM"},
    {"query": "AWS CLI command to create an S3 bucket in us-west-2 region", "intent": "CLI_SCRIPT_GENERATION", "service": "Amazon S3", "urgency": "LOW"},
    {"query": "Show me aws iam list-attached-user-policies CLI syntax", "intent": "CLI_SCRIPT_GENERATION", "service": "AWS IAM", "urgency": "LOW"},
    {"query": "Command to update AWS Lambda function code from local zip file", "intent": "CLI_SCRIPT_GENERATION", "service": "AWS Lambda", "urgency": "MEDIUM"},

    # ========================================================
    # 7. SECURITY & BEST PRACTICE
    # ========================================================
    {"query": "What is the Principle of Least Privilege in AWS IAM?", "intent": "SECURITY_BEST_PRACTICE", "service": "AWS IAM", "urgency": "HIGH"},
    {"query": "How to enforce S3 Block Public Access across an entire AWS account?", "intent": "SECURITY_BEST_PRACTICE", "service": "Amazon S3", "urgency": "CRITICAL"},
    {"query": "Best practices for managing and rotating IAM access keys", "intent": "SECURITY_BEST_PRACTICE", "service": "AWS IAM", "urgency": "HIGH"},
    {"query": "How to enforce Multi-Factor Authentication (MFA) via IAM policy condition", "intent": "SECURITY_BEST_PRACTICE", "service": "AWS IAM", "urgency": "HIGH"},
    {"query": "EC2 security best practices avoiding open 0.0.0.0/0 SSH rules", "intent": "SECURITY_BEST_PRACTICE", "service": "Amazon EC2", "urgency": "HIGH"},
    {"query": "How to enable default server-side encryption SSE-KMS for an S3 bucket", "intent": "SECURITY_BEST_PRACTICE", "service": "Amazon S3", "urgency": "HIGH"},
    {"query": "Security guidelines for storing database credentials in Lambda environment variables", "intent": "SECURITY_BEST_PRACTICE", "service": "AWS Lambda", "urgency": "CRITICAL"},

    # ========================================================
    # 8. CONCEPTUAL EXPLANATION
    # ========================================================
    {"query": "What is the difference between General Purpose and Compute Optimized EC2 instances?", "intent": "CONCEPTUAL_EXPLANATION", "service": "Amazon EC2", "urgency": "LOW"},
    {"query": "Explain AWS Lambda execution environment lifecycle and cold starts", "intent": "CONCEPTUAL_EXPLANATION", "service": "AWS Lambda", "urgency": "LOW"},
    {"query": "What is the difference between an IAM user, an IAM group, and an IAM role?", "intent": "CONCEPTUAL_EXPLANATION", "service": "AWS IAM", "urgency": "LOW"},
    {"query": "Explain difference between S3 Standard, Standard-IA, and Glacier Flexible Archive", "intent": "CONCEPTUAL_EXPLANATION", "service": "Amazon S3", "urgency": "LOW"},
    {"query": "What is the difference between an IAM identity-based policy and resource-based policy?", "intent": "CONCEPTUAL_EXPLANATION", "service": "AWS IAM", "urgency": "LOW"},
    {"query": "What is the difference between EC2 instance store and EBS persistent storage?", "intent": "CONCEPTUAL_EXPLANATION", "service": "Amazon EC2", "urgency": "LOW"},

    # ========================================================
    # 9. OUT OF SCOPE / UNRELATED QUERIES
    # ========================================================
    {"query": "How do I deploy an application on Azure Virtual Machines?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "What is Google Cloud BigQuery pricing and architecture?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "Can you give me a recipe for chocolate chip banana bread?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "Who won the FIFA World Cup final in 2022?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "Explain quantum computing qubit superposition and entanglement", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "How do I fix a blue screen of death DRIVER_IRQL_NOT_LESS_OR_EQUAL on Windows?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "Write a poem about the autumn leaves falling in the forest", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "What is the capital city of Australia?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},
    {"query": "How to create a React frontend with Redux Toolkit and Tailwind CSS?", "intent": "OUT_OF_SCOPE", "service": "Out-of-Scope", "urgency": "LOW"},

    # ========================================================
    # 10. GREETINGS & FRIENDLY CONVERSATION
    # ========================================================
    {"query": "hello", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "hi", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "hey", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "hello there", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "hi there", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "good morning", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "good afternoon", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "good evening", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "how are you", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "how are you doing today", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "who are you", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "what can you do", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "can you help me with aws", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "hi I need some technical assistance", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "thank you for your help", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "thanks a lot", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "goodbye", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"},
    {"query": "bye see you later", "intent": "GREETING", "service": "General AWS", "urgency": "LOW"}
]

