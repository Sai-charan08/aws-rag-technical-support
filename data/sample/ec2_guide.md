# AWS Amazon EC2 (Elastic Compute Cloud) Technical Reference Guide

## 1. Overview of Amazon EC2
Amazon Elastic Compute Cloud (Amazon EC2) provides scalable computing capacity in the AWS Cloud. Using Amazon EC2 eliminates the need to invest in hardware upfront, enabling applications to build and deploy faster. You can use Amazon EC2 to launch as many or as few virtual servers as needed, configure security and networking, and manage storage.

## 2. EC2 Instance Types and Naming Conventions
Amazon EC2 provides a wide selection of instance types optimized to fit different use cases:
- **General Purpose (t3, t4g, m5, m6i)**: Balanced compute, memory, and networking resources. Ideal for web servers, small databases, and dev environments.
- **Compute Optimized (c5, c6i, c7g)**: High-performance processors. Ideal for high-performance web servers, scientific modeling, batch processing, and machine learning inference.
- **Memory Optimized (r5, r6i, x2gd)**: Designed to deliver fast performance for workloads that process large data sets in memory (e.g., open-source databases, in-memory caches like Redis).
- **Storage Optimized (i3, i4i, d3)**: Optimized for workloads requiring high, sequential read/write access to large data sets on local storage (e.g., NoSQL databases, data warehousing).

### Instance Naming Syntax
Instance names follow the pattern `[family][generation][attributes].[size]`, for example `t3.micro`:
- `t`: Instance family (General purpose burstable)
- `3`: 3rd generation technology
- `micro`: Instance size (defines vCPU count and RAM allocation)

## 3. Launching and Configuring an EC2 Instance
To launch an EC2 instance:
1. Open the Amazon EC2 console and click **Launch Instance**.
2. Select an Amazon Machine Image (AMI), such as Amazon Linux 2023 or Ubuntu 22.04 LTS.
3. Choose an Instance Type (e.g., `t3.micro` for testing).
4. Configure Instance Details: Select VPC, Subnet, and assign an IAM Role if your application requires AWS API access.
5. Add Storage: Specify EBS volume size (e.g., 8 GB General Purpose SSD gp3).
6. Configure Security Group: Add inbound rules to allow necessary traffic (e.g., SSH on port 22, HTTP on port 80).
7. Select or create an SSH Key Pair (`.pem` or `.ppk`) and launch.

## 4. Connecting to an EC2 Instance via SSH
To connect to a Linux EC2 instance using OpenSSH:

```bash
# 1. Set key permissions (Linux/macOS)
chmod 400 my-key-pair.pem

# 2. Connect using public IP address
ssh -i "my-key-pair.pem" ec2-user@ec2-198-51-100-1.compute-1.amazonaws.com
```

Default usernames vary by operating system:
- Amazon Linux 2023 / AL2: `ec2-user`
- Ubuntu: `ubuntu`
- RHEL: `ec2-user` or `root`
- CentOS: `centos`
- Debian: `admin`

## 5. Troubleshooting Common EC2 Connection Errors

### Error: "Permission denied (publickey)"
**Causes & Resolutions:**
1. **Wrong Username**: Verify you are using the correct default user (e.g., `ubuntu` vs `ec2-user`).
2. **Incorrect Key File**: Ensure you specified the private key file (`.pem`) matching the public key registered during instance launch.
3. **Insecure Key Permissions**: If SSH complains about unprotected private key file permissions (`0644`), execute `chmod 400 my-key-pair.pem`.
4. **Modified authorized_keys**: If someone removed public keys from `~/.ssh/authorized_keys` inside the instance, use EC2 Serial Console or EC2 Instance Connect to restore access.

### Error: "Connection timed out"
**Causes & Resolutions:**
1. **Security Group Inbound Rules**: Check the instance Security Group. Ensure port 22 (SSH) is open for your current public IP address (`0.0.0.0/0` or specific `/32` CIDR).
2. **Network ACLs / Route Tables**: Verify the instance is in a Public Subnet attached to an Internet Gateway (IGW), with a route `0.0.0.0/0 -> igw-xxxxxx` in the subnet route table.
3. **Instance State**: Ensure the instance is in `running` state and passed 2/2 status checks.

### Security Note
Never share or upload private key files (`.pem`) to public repositories. Always scope SSH Security Group rules to your specific IP address (`/32`) rather than opening port 22 globally (`0.0.0.0/0`).
