provider "aws" {
  region = "ap-south-1"
}

data "aws_vpc" "default" {
  default = true
}

variable "admin_cidr" {
  description = "Trusted CIDR for SSH and app access"
  type        = string
  default     = "182.76.246.162/32"
}

variable "app_port" {
  description = "Application port exposed by the container"
  type        = number
  default     = 5000
}

variable "github_repo_url" {
  description = "HTTPS Git repository URL"
  type        = string
  default     = "https://github.com/CoderShrikant02/major_frontend.git"
}

variable "github_branch" {
  description = "Branch to deploy"
  type        = string
  default     = "main"
}

variable "app_secret_key" {
  description = "Flask SECRET_KEY passed to the container"
  type        = string
  sensitive   = true
}

variable "db_host" {
  description = "Database host passed to the container"
  type        = string
}

variable "db_user" {
  description = "Database user passed to the container"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password passed to the container"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name passed to the container"
  type        = string
}

variable "github_egress_cidrs" {
  description = "GitHub IPv4 CIDRs used for restricted HTTPS egress"
  type        = list(string)
  default = [
    "140.82.112.0/20",
    "192.30.252.0/22",
    "185.199.108.0/22",
  ]
}

variable "ubuntu_repo_egress_cidrs" {
  description = "Ubuntu repository IPv4 CIDRs used for restricted HTTPS egress"
  type        = list(string)
  default = [
    "185.125.190.0/23",
    "185.125.188.0/22",
    "91.189.88.0/21",
  ]
}

locals {
  restricted_https_cidrs = distinct(concat(var.github_egress_cidrs, var.ubuntu_repo_egress_cidrs))
}

resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "Secure EC2 access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  ingress {
    description = "Flask access"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  egress {
    description = "Restricted HTTPS egress for GitHub and Ubuntu repos"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = local.restricted_https_cidrs
  }

  tags = {
    Name = "secure-sg"
  }
}

resource "aws_instance" "tomato_server" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t3.micro"

  vpc_security_group_ids      = [aws_security_group.secure_sg.id]
  associate_public_ip_address = true
  user_data_replace_on_change = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted             = true
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data = <<-EOF
#!/bin/bash
set -euxo pipefail

exec > >(tee -a /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

export DEBIAN_FRONTEND=noninteractive
APP_DIR="/opt/major_frontend"
REPO_URL="${var.github_repo_url}"
REPO_BRANCH="${var.github_branch}"
IMAGE_NAME="tomato-ai"
CONTAINER_NAME="tomato-ai"
APP_PORT="${var.app_port}"
APP_ENV_FILE="/opt/tomato-ai.env"

retry() {
  local attempts="$1"
  shift
  local n=1
  until "$@"; do
    if [ "$n" -ge "$attempts" ]; then
      return 1
    fi
    n=$((n + 1))
    sleep 10
  done
}

echo "Configuring HTTPS-only Ubuntu repositories"
UBUNTU_CODENAME="$(
  . /etc/os-release
  echo "$${VERSION_CODENAME}"
)"

cat >/etc/apt/sources.list <<APT
deb https://archive.ubuntu.com/ubuntu $${UBUNTU_CODENAME} main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu $${UBUNTU_CODENAME}-updates main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu $${UBUNTU_CODENAME}-backports main restricted universe multiverse
deb https://security.ubuntu.com/ubuntu $${UBUNTU_CODENAME}-security main restricted universe multiverse
APT

retry 5 apt-get update -y
retry 5 apt-get install -y --no-install-recommends ca-certificates git docker.io

systemctl enable --now docker
usermod -aG docker ubuntu || true

mkdir -p "$${APP_DIR}"
chown ubuntu:ubuntu "$${APP_DIR}"

cat >"$${APP_ENV_FILE}" <<ENVVARS
SECRET_KEY=${var.app_secret_key}
DB_HOST=${var.db_host}
DB_USER=${var.db_user}
DB_PASSWORD=${var.db_password}
DB_NAME=${var.db_name}
ENVVARS

chmod 600 "$${APP_ENV_FILE}"

if [ -d "$${APP_DIR}/.git" ]; then
  git -C "$${APP_DIR}" fetch --all --prune
  git -C "$${APP_DIR}" checkout "$${REPO_BRANCH}"
  git -C "$${APP_DIR}" reset --hard "origin/$${REPO_BRANCH}"
else
  git clone --branch "$${REPO_BRANCH}" --depth 1 "$${REPO_URL}" "$${APP_DIR}"
fi

cd "$${APP_DIR}"
docker build -t "$${IMAGE_NAME}" .

if docker ps -aq --filter "name=^$${CONTAINER_NAME}$" | grep -q .; then
  docker rm -f "$${CONTAINER_NAME}"
fi

docker run -d \
  --name "$${CONTAINER_NAME}" \
  --restart unless-stopped \
  --env-file "$${APP_ENV_FILE}" \
  -p "$${APP_PORT}:$${APP_PORT}" \
  "$${IMAGE_NAME}"

sleep 15
docker ps --filter "name=^$${CONTAINER_NAME}$"
docker logs "$${CONTAINER_NAME}" --tail 50 || true

echo "Deployment finished successfully"
EOF

  tags = {
    Name = "tomato-ai-server"
  }
}
