I ran a Trivy security scan on my Terraform AWS infrastructure.

The following vulnerabilities were found:

1. Security group allows ingress from 0.0.0.0/0 on port 22
2. Security group allows unrestricted egress
3. Root block device is not encrypted
4. IMDSv2 is not required

Please generate a secure Terraform configuration that fixes these issues while still allowing my EC2 instance to run.
