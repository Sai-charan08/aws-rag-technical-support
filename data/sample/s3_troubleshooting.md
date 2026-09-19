# AWS Amazon S3 (Simple Storage Service) Troubleshooting & Configuration Guide

## 1. Overview of Amazon S3
Amazon Simple Storage Service (Amazon S3) is an object storage service offering industry-leading scalability, data availability, security, and performance. Data is stored as objects within resources called "buckets." Each object consists of data, key (name), metadata, and tags.

## 2. Core S3 Architecture Concepts
- **Buckets**: Top-level containers for objects. S3 bucket names are globally unique across all AWS accounts worldwide and must follow DNS naming conventions (3-63 characters, lowercase, no underscores).
- **Objects**: Entities stored in S3, ranging from 0 bytes up to 5 TB in size.
- **Keys**: The unique identifier for an object within a bucket (e.g., `photos/2026/vacation.jpg`).
- **S3 Block Public Access**: Account-level and bucket-level security controls that prevent public access to S3 resources regardless of ACLs or bucket policies.

## 3. Troubleshooting Common S3 Errors

### Error: `NoSuchBucket` (Status Code: 404 Not Found)
**Causes & Resolutions:**
1. **Misspelled Bucket Name**: Double-check the exact bucket name string in your code or CLI command.
2. **Incorrect AWS Region Endpoint**: S3 buckets reside in a specific AWS Region. If using SDK/CLI without explicit region setting, the API call may default to `us-east-1` while your bucket is in `eu-west-1`. Specify `--region` in AWS CLI or set client region in SDK code:
   ```bash
   aws s3 ls s3://my-app-data-bucket --region us-west-2
   ```
3. **Bucket Deleted or Not Created**: Verify the bucket actually exists using the AWS Management Console or `aws s3api list-buckets`.

### Error: `AccessDenied` (Status Code: 403 Forbidden)
**Causes & Resolutions:**
1. **IAM Policy Restrictions**: The calling IAM User/Role lacks `s3:GetObject` or `s3:PutObject` permission on the target resource `arn:aws:s3:::my-bucket/*`.
2. **S3 Block Public Access Enabled**: If attempting to download an object via public HTTP URL, verify whether Block Public Access is overriding your object ACLs or bucket policy.
3. **KMS Key Encryption Permissions**: If the S3 object is encrypted with AWS KMS (`aws:kms`), the caller must also have `kms:Decrypt` permission on the KMS key policy.
4. **Bucket Policy Deny Statements**: Check if the bucket policy has explicit `Deny` rules overriding `Allow` statements.

## 4. S3 Bucket Policy Examples

### Allowing Read-Only Access to Specific IAM Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppRoleRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/MyApplicationRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-company-data-bucket",
        "arn:aws:s3:::my-company-data-bucket/*"
      ]
    }
  ]
}
```

## 5. S3 Lifecycle Management Policies
S3 Lifecycle configurations manage object storage cost-effectively throughout their lifecycle:
- **Transition Actions**: Move objects between storage classes (e.g., S3 Standard -> S3 Standard-IA after 30 days -> S3 Glacier Flexible Retrieval after 90 days).
- **Expiration Actions**: Automatically delete objects after a specified number of days or expire non-current versions in version-enabled buckets.

```json
{
  "Rules": [
    {
      "ID": "ArchiveOldLogs",
      "Status": "Enabled",
      "Filter": { "Prefix": "logs/" },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

### Security Best Practices
- Keep **S3 Block Public Access** ON for all production buckets unless public hosting is explicitly intended.
- Use IAM roles and bucket policies instead of legacy ACLs.
- Enable Server-Side Encryption (SSE-S3 or SSE-KMS) for all buckets.
