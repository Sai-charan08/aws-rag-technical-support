"""Curated repository of exact suitable solutions for AWS technical support requests."""

AWS_SOLUTIONS = [
    # ========================================================
    # 0. GREETINGS & FRIENDLY INTERACTIONS
    # ========================================================
    {
        "query": "hello",
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "greetings", "hi there", "hello there"],
        "solution": (
            "Hello! 👋 Welcome! I'm your AWS Technical Support Assistant. It's great to connect with you!\n\n"
            "How can I assist you today? You can ask me any technical question regarding:\n"
            "- **Amazon EC2**: SSH connectivity, status check failures, EBS storage, security groups\n"
            "- **Amazon S3**: Bucket permissions, NoSuchBucket errors, CORS rules, lifecycle management\n"
            "- **AWS Lambda**: Timeouts, out-of-memory errors, cold starts, private VPC networking\n"
            "- **AWS IAM**: Least privilege policies, roles, assume role errors, access key rotation\n\n"
            "Feel free to describe the issue or error you're encountering, and I'll be glad to help!"
        )
    },
    {
        "query": "how are you",
        "keywords": ["how are you", "how are you doing", "how do you do"],
        "solution": (
            "Hello! 👋 I'm doing very well, thank you for asking! I'm fully ready to help you with your AWS cloud technical challenges.\n\n"
            "What issue or architecture question can I help you resolve today?"
        )
    },
    {
        "query": "who are you",
        "keywords": ["who are you", "what can you do", "introduce yourself", "what is your purpose"],
        "solution": (
            "Hello! 👋 I am your dedicated **AWS Technical Support Assistant**.\n\n"
            "I provide friendly, fast, and authoritative technical support for AWS Cloud infrastructure, including:\n"
            "- 🖥️ **Amazon EC2**: SSH connectivity (`Permission denied`), status checks, EBS storage, security groups\n"
            "- 🪣 **Amazon S3**: Bucket permissions (`AccessDenied`), `NoSuchBucket`, CORS, lifecycle rules\n"
            "- ⚡ **AWS Lambda**: Timeouts, memory allocation, cold starts, private VPC networking\n"
            "- 🛡️ **AWS IAM**: Least privilege permissions, trust policies, assume role errors, access keys\n\n"
            "How can I help you today? Please feel free to ask your question!"
        )
    },
    {
        "query": "thank you",
        "keywords": ["thank you", "thanks", "thanks a lot", "thank you very much"],
        "solution": (
            "Hello! You're very welcome! 😊 I'm always glad to help. Please feel free to reach out anytime you have further questions or run into any AWS challenges. Have a wonderful day!"
        )
    },
    {
        "query": "goodbye",
        "keywords": ["goodbye", "bye", "see you later", "see ya"],
        "solution": (
            "Goodbye! 👋 Thank you for reaching out to AWS Technical Support. Have a great day ahead, and let me know whenever you need assistance again!"
        )
    },

    # ========================================================
    # 1. EXACT SUITABLE TECHNICAL SOLUTIONS
    # ========================================================
    {
        "query": "How do I fix a NoSuchBucket error in Amazon S3?",
        "keywords": ["nosuchbucket", "s3", "bucket error", "troubleshoot nosuchbucket"],
        "solution": (
            "Hello! I'd be glad to help you resolve this. Here is the direct step-by-step solution for the S3 NoSuchBucket error:\n\n"
            "1. **Check Bucket Name Spelling**: S3 bucket names are globally unique and case-sensitive. Verify there are no typographical errors or trailing spaces in the name.\n\n"
            "2. **Specify the Correct AWS Region**: S3 buckets reside in a specific AWS region. If your AWS CLI or SDK defaults to `us-east-1` while the bucket was created in another region, the request will fail with `NoSuchBucket`. Provide the `--region` flag:\n"
            "   ```bash\n"
            "   aws s3 ls s3://my-bucket-name --region us-west-2\n"
            "   ```\n\n"
            "3. **Verify Bucket Existence**: Confirm whether the bucket exists in your AWS account:\n"
            "   ```bash\n"
            "   aws s3api list-buckets --query \"Buckets[?Name=='my-bucket-name']\"\n"
            "   ```\n\n"
            "Please let me know if this resolves the error or if you need any further help!"
        )
    },
    {
        "query": "How do I fix a Permission denied (publickey) error when connecting to EC2?",
        "keywords": ["permission denied", "publickey", "ssh", "ec2", "connecting to ec2"],
        "solution": (
            "Hello! I'd be happy to help you fix this SSH issue. Here is the step-by-step resolution for the EC2 Permission denied (publickey) error:\n\n"
            "1. **Set Private Key File Permissions**: SSH rejects keys with open permissions. Ensure only your user has read access (`chmod 400`):\n"
            "   ```bash\n"
            "   chmod 400 my-key-pair.pem\n"
            "   ```\n\n"
            "2. **Use the Correct Default Username**: Ensure you are logging in with the correct default user for your AMI:\n"
            "   - Amazon Linux 2 / 2023: `ec2-user`\n"
            "   - Ubuntu: `ubuntu`\n"
            "   - RHEL: `ec2-user`\n"
            "   - Debian: `admin`\n\n"
            "3. **Connect with Key Pair**: Run the connection command specifying your `.pem` key:\n"
            "   ```bash\n"
            "   ssh -i \"my-key-pair.pem\" ec2-user@<instance-public-ip>\n"
            "   ```\n\n"
            "Feel free to let me know if you run into any other connection issues!"
        )
    },
    {
        "query": "How to resolve Task timed out after 3.00 seconds in AWS Lambda?",
        "keywords": ["task timed out", "lambda", "3.00 seconds", "timeout", "execution timeout"],
        "solution": (
            "Hello! I'd be glad to assist you with your Lambda function. Here is how to fix the Task timed out error:\n\n"
            "1. **Increase Function Timeout**: The default timeout is 3 seconds, which is often exceeded when connecting to remote databases or external APIs. Increase the timeout via AWS CLI or Console (up to 15 minutes / 900 seconds):\n"
            "   ```bash\n"
            "   aws lambda update-function-configuration --function-name MyFunction --timeout 30\n"
            "   ```\n\n"
            "2. **Check VPC Subnet & NAT Gateway**: If your Lambda runs in a private VPC, verify that its subnet routes `0.0.0.0/0` outbound traffic through a NAT Gateway so it can reach external internet endpoints.\n\n"
            "3. **Eliminate Code Deadlocks**: Ensure database connection pools are closed and check for unhandled asynchronous promises or infinite retry loops.\n\n"
            "Please let me know if you need help tuning memory or optimizing execution time!"
        )
    },
    {
        "query": "What is the Principle of Least Privilege in AWS IAM?",
        "keywords": ["principle of least privilege", "iam", "least privilege"],
        "solution": (
            "Hello! I'm happy to explain this core security concept for you.\n\n"
            "The **Principle of Least Privilege** requires granting users, services, and applications only the minimum necessary permissions required to perform their specific tasks—never broad wildcards (`Action: *`, `Resource: *`).\n\n"
            "**Least-Privilege Scoped Policy Example:**\n"
            "```json\n"
            "{\n"
            "  \"Version\": \"2012-10-17\",\n"
            "  \"Statement\": [\n"
            "    {\n"
            "      \"Sid\": \"ScopedS3ReadAccess\",\n"
            "      \"Effect\": \"Allow\",\n"
            "      \"Action\": [\n"
            "        \"s3:GetObject\",\n"
            "        \"s3:ListBucket\"\n"
            "      ],\n"
            "      \"Resource\": [\n"
            "        \"arn:aws:s3:::my-production-logs\",\n"
            "        \"arn:aws:s3:::my-production-logs/*\"\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "Let me know if you would like me to review or help scope any of your IAM policies!"
        )
    },
    {
        "query": "Give me the aws s3 sync command to copy local files to an S3 bucket",
        "keywords": ["aws s3 sync", "copy local files", "s3 sync command"],
        "solution": (
            "Hello! I'd be glad to provide the AWS CLI command for you.\n\n"
            "To synchronize a local directory to an S3 bucket:\n"
            "```bash\n"
            "aws s3 sync ./my-local-folder s3://my-destination-bucket/target-folder/ --region us-east-1\n"
            "```\n\n"
            "**Useful Flags:**\n"
            "- `--delete`: Removes files from destination that no longer exist in source.\n"
            "- `--exclude \"*.tmp\"`: Exclude specific file types.\n"
            "- `--dryrun`: Preview changes without actually transferring files.\n\n"
            "Feel free to ask if you need scripts for automated scheduled syncs!"
        )
    },
    {
        "query": "How do I deploy an application on Azure Virtual Machines?",
        "keywords": ["azure", "azure virtual machines", "gcp", "bigquery"],
        "solution": (
            "Hello! Thank you for reaching out. Your query relates to Microsoft Azure, but I am specialized specifically as an **Amazon Web Services (AWS)** Technical Support Assistant.\n\n"
            "I would be delighted to assist you with any AWS services including **Amazon EC2, Amazon S3, AWS Lambda,** or **AWS IAM**. Please feel free to ask any AWS question!"
        )
    },
    {
        "query": "What is the difference between EC2 instance types like t3 and c5?",
        "keywords": ["difference between ec2 instance types", "t3 and c5", "instance types"],
        "solution": (
            "Hello! I'd be happy to explain the key differences between EC2 instance families for you:\n\n"
            "- **t3 (General Purpose - Burstable)**:\n"
            "  - Balanced compute, memory, and networking.\n"
            "  - Uses CPU credits to burst above baseline when needed.\n"
            "  - Best for web servers, dev/test environments, and low-latency background microservices.\n\n"
            "- **c5 (Compute Optimized)**:\n"
            "  - High-performance Intel Xeon Platinum processors with high vCPU-to-memory ratio.\n"
            "  - Dedicated, sustained full-core compute performance without throttling.\n"
            "  - Best for compute-intensive batch processing, scientific modeling, video encoding, and machine learning inference.\n\n"
            "Let me know if you would like instance sizing recommendations for your specific workload!"
        )
    },
    {
        "query": "How do I configure an S3 lifecycle policy to transition to Glacier?",
        "keywords": ["s3 lifecycle policy", "transition to glacier", "lifecycle"],
        "solution": (
            "Hello! I'd be glad to help you configure an S3 lifecycle transition rule. Here is the step-by-step guide:\n\n"
            "Create a lifecycle rule JSON file (`lifecycle.json`):\n"
            "```json\n"
            "{\n"
            "  \"Rules\": [\n"
            "    {\n"
            "      \"ID\": \"ArchiveLogsToGlacier\",\n"
            "      \"Status\": \"Enabled\",\n"
            "      \"Filter\": { \"Prefix\": \"logs/\" },\n"
            "      \"Transitions\": [\n"
            "        {\n"
            "          \"Days\": 30,\n"
            "          \"StorageClass\": \"GLACIER\"\n"
            "        }\n"
            "      ],\n"
            "      \"Expiration\": {\n"
            "        \"Days\": 365\n"
            "      }\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "Apply the policy using the AWS CLI:\n"
            "```bash\n"
            "aws s3api put-bucket-lifecycle-configuration \\\n"
            "  --bucket my-bucket-name \\\n"
            "  --lifecycle-configuration file://lifecycle.json\n"
            "```\n\n"
            "Please let me know if you need any adjustments to the transition days or prefix filters!"
        )
    }
]
