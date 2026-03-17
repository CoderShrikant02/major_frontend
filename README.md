# Jenkins Pipeline: Terraform + EC2 Deployment

This README explains the Jenkins declarative pipeline provided in the request. The pipeline provisions AWS infrastructure with Terraform, deploys the application to an EC2 instance, and verifies the deployment over SSH.

**What This Pipeline Does**
1. Checks out the repository from GitHub.
2. Generates a Terraform variables file from Jenkins environment values.
3. Runs a Trivy security scan on the Terraform config.
4. Initializes Terraform.
5. Applies Terraform to create/update infrastructure.
6. Connects to the EC2 instance, waits for cloud-init, and validates Docker services and health checks.
7. Cleans up the generated Terraform variables file.

**Key Environment Variables**
These values are configured in the `environment { ... }` block and are written to `generated.tfvars` for Terraform:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`: AWS credentials and region.
- `ADMIN_CIDR`: CIDR block allowed to access admin endpoints (should be your IP, not `0.0.0.0/0`).
- `APP_PORT`: Application port exposed on the instance.
- `SSH_KEY_NAME`: AWS EC2 key pair name.
- `GITHUB_REPO_URL`, `GITHUB_BRANCH`: Repository and branch for deployment.
- `APP_SECRET_KEY`: Application secret key.
- `DB_NAME`, `DB_ROOT_PASSWORD`: Database configuration.
- `INSTANCE_TYPE`: EC2 instance type.
- `TF_VARS_FILE`: Path to the generated Terraform variables file.

**Pipeline Stages**
1. **Checkout**
   - Clones the GitHub repo using Jenkins credentials `github-token-2`.

2. **Generate Terraform Vars**
   - Writes `generated.tfvars` from Jenkins env values:
     - `admin_cidr`, `app_port`, `instance_type`
     - `github_repo_url`, `github_branch`
     - `ssh_key_name`
     - `app_secret_key`
     - `db_name`, `db_root_password`

3. **Security Scan (Trivy)**
   - Runs `trivy config .` to scan Terraform and config files.
   - The `|| true` ensures the pipeline continues even if Trivy finds issues.

4. **Terraform Init**
   - Runs `terraform init` inside the `terraform/` directory.

5. **Terraform Apply**
   - Removes any existing `terraform.tfvars` in `terraform/`.
   - Applies Terraform using the generated variables file:
     - `terraform apply -auto-approve -var-file="${TF_VARS_FILE}"`

6. **Verify On EC2**
   - Uses Jenkins credentials `ec2-ssh-key` to SSH into the instance.
   - Finds the public IP from Terraform state:
     - `terraform state show aws_instance.tomato_server`
   - Waits for SSH to be available.
   - Polls `cloud-init` until `done` or `error`.
   - Verifies services and app health:
     - `systemctl is-active docker`
     - `docker ps -a`
     - `docker-compose ... ps`
     - `docker-compose ... logs --tail 100`
     - `curl -fsS http://localhost:80/health`
     - `ss -tulpn | grep ':80'`

**Post Actions**
- Always removes the generated Terraform vars file:
  - `rm -f "${TF_VARS_FILE}" || true`

**Notes and Recommendations**
- Replace `ADMIN_CIDR = 0.0.0.0/0` with your actual IP to avoid public exposure.
- Ensure Jenkins has these credentials configured:
  - `aws-access-key-id`
  - `aws-secret-access-key`
  - `github-token-2`
  - `ec2-ssh-key`
- The pipeline assumes the Terraform module defines `aws_instance.tomato_server`.
- The app is expected to expose a health endpoint at `http://localhost:80/health` on the EC2 instance.
