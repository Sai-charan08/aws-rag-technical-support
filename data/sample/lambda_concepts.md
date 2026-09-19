# AWS Lambda Serverless Computing Technical Guide

## 1. Overview of AWS Lambda
AWS Lambda is a serverless, event-driven compute service that lets you run code for virtually any type of application or backend service without provisioning or managing servers. Lambda automatically scales execution from a few requests per day to hundreds of thousands per second.

## 2. Key Architecture & Execution Concepts
- **Function**: The code and runtime configuration that executes your logic.
- **Handler**: The entry point in your code that AWS Lambda calls when execution begins (e.g., `lambda_function.lambda_handler` in Python or `index.handler` in Node.js).
- **Execution Role**: An IAM role that Lambda assumes when invoking the function, granting permissions to access AWS services (e.g., S3, DynamoDB, CloudWatch Logs).
- **Environment Variables**: Key-value pairs used to pass operational settings to function code without modifying source code.
- **Cold Starts**: The initialization latency when a function is invoked after period of inactivity while AWS provisions container infrastructure.

## 3. Creating and Invoking a Lambda Function

### Example Python Handler Code (`lambda_function.py`)
```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    name = event.get("name", "Cloud Developer")
    message = f"Hello, {name}! Lambda execution successful."
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message})
    }
```

### AWS CLI Invocation Command
```bash
aws lambda invoke \
  --function-name MyPythonFunction \
  --payload '{"name": "Alice"}' \
  --cli-binary-format raw-in-base64-out \
  response.json
```

## 4. Troubleshooting Common Lambda Errors

### Error: `Task timed out after 3.00 seconds`
**Causes & Resolutions:**
1. **Default Timeout Too Low**: Default Lambda timeout is 3 seconds. If your code connects to remote databases or external APIs, increase the timeout setting (up to 15 minutes / 900 seconds) in the Lambda Console under Configuration -> General Configuration.
2. **Unreachable Database / Subnet Blocking**: If Lambda is deployed inside a VPC, ensure Security Groups and Route Tables allow outbound network access (via NAT Gateway) to reach internet endpoints or RDS instances.
3. **Infinite Loops or Blocking Calls**: Check code for synchronous network requests or deadlocks.

### Error: `Runtime.ImportModuleError: Unable to import module 'lambda_function'`
**Causes & Resolutions:**
1. **Filename Mismatch**: Handler configuration expects file `lambda_function.py`, but your deployed file is named `main.py` or `index.py`. Match handler setting to `filename.handler_function`.
2. **Missing Dependencies**: Third-party packages (e.g., `pandas`, `requests`) were not bundled in the deployment deployment package or included in a Lambda Layer.
3. **Architecture Mismatch**: C-extensions compiled on macOS/Windows (`x86_64` or `arm64`) deployed to Linux Lambda environment. Compile dependencies on Amazon Linux 2 or use Docker build containers.

### Error: `Memory Size Exceeded` / Out of Memory
**Causes & Resolutions:**
1. Default memory allocation is 128 MB. Heavy workloads (PDF processing, image resizing, data science libraries) require adjusting memory up to 10,240 MB (10 GB).
2. Note that allocating more memory also proportionally increases vCPU compute power and network throughput.

## 5. Security & Best Practices
- Assign **Least Privilege IAM Roles**: Never attach `AdministratorAccess` to Lambda functions. Attach minimum AWS managed policies like `AWSLambdaBasicExecutionRole`.
- Store secrets and credentials in **AWS Secrets Manager** or **Systems Manager Parameter Store**, never hardcoded in function files.
- Enable CloudWatch Logs to capture stdout/stderr for rapid debugging.
