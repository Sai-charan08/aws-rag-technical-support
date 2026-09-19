# AWS Identity and Access Management (IAM) Security & Policy Guide

## 1. Overview of AWS IAM
AWS Identity and Access Management (IAM) is a web service that helps you securely control access to AWS resources. IAM enables central management of permissions that control which AWS resources users can access, as well as who can be authenticated (signed in) and authorized (have permissions) to use resources.

## 2. Core IAM Entities
- **IAM Users**: An entity created in AWS to represent a person or application that interacts with AWS resources.
- **IAM Groups**: A collection of IAM users. Groups let you specify permissions for multiple users at once.
- **IAM Roles**: An IAM identity that you can create in your account that has specific permissions. Unlike a user, a role is not uniquely associated with one person; it can be assumed by anyone or any service (e.g., EC2 instance, Lambda function) that needs it.
- **IAM Policies**: JSON documents that formally define permissions. Policies specify what actions are allowed or denied, on which resources, under what conditions.

## 3. Principle of Least Privilege
The **Principle of Least Privilege** is a fundamental security best practice. It states that users and applications should be granted only the minimum permissions necessary to perform their assigned tasks, and no more.

### Bad Practice (Over-permissioned):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

### Good Practice (Least Privilege Scoped):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadSpecificS3BucketOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::app-production-logs",
        "arn:aws:s3:::app-production-logs/*"
      ]
    }
  ]
}
```

## 4. Policy Evaluation Logic
When an AWS API request is made, IAM evaluates policies according to strict rules:
1. By default, all requests are **implicitly denied**.
2. An **explicit allow** in any policy overrides the default implicit deny.
3. An **explicit deny** in ANY policy overrides ALL allows.

## 5. IAM Roles vs IAM Access Keys
- **IAM Access Keys (Access Key ID & Secret Access Key)**: Long-term credentials assigned to IAM users. Hardcoding access keys in applications or git repositories creates severe security vulnerabilities.
- **IAM Roles**: Provide short-term temporary security credentials (via AWS STS). EC2 instances, ECS tasks, and Lambda functions should always use IAM Roles instead of hardcoded access keys.

## 6. Troubleshooting Common IAM Errors

### Error: `User: arn:aws:iam::123:user/dev is not authorized to perform: ec2:RunInstances`
**Causes & Resolutions:**
1. Lacks required permission in attached IAM policies. Attach an inline policy or managed policy granting `ec2:RunInstances`.
2. Explicit Deny in Service Control Policy (SCP) or Permission Boundary. Check AWS Organizations SCPs if working in an enterprise multi-account environment.
3. Resource ARNs restriction: The policy limits `ec2:RunInstances` to specific subnet or AMI ARNs.

### Error: `sts:AssumeRole` Failed / AccessDenied
**Causes & Resolutions:**
1. **Trust Policy Misconfiguration**: The target IAM role's Trust Policy (Principal) must explicitly grant permission to the calling entity to assume it:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
2. Calling user/service lacks `sts:AssumeRole` permissions in its own identity policy.

## Security Warnings & Reminders
- Never commit AWS Access Keys (`AKIA...`) or Secret Keys to public code repositories like GitHub!
- Enable Multi-Factor Authentication (MFA) on all IAM User accounts and Root credentials.
- Rotate access keys every 90 days if temporary IAM Roles cannot be used.
