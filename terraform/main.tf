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
  description = "Application port exposed publicly"
  type        = number
  default     = 80
}

variable "instance_type" {
  description = "EC2 instance type (t3.micro may be too small to build/run TensorFlow)"
  type        = string
  default     = "t3.small"
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

variable "ssh_key_name" {
  description = "EC2 Key Pair name to attach to the instance (must match the PEM used by Jenkins Verify stage)"
  type        = string
}

variable "app_secret_key" {
  description = "Flask secret key"
  type        = string
  default     = "tomato-ai-demo-secret-key"
}

variable "db_name" {
  description = "MySQL database name"
  type        = string
  default     = "tomato_disease_db"
}

variable "db_user" {
  description = "MySQL application user"
  type        = string
  default     = "tomato_user"
}

variable "db_password" {
  description = "MySQL application password"
  type        = string
  default     = "tomato_password"
}

variable "db_root_password" {
  description = "MySQL root password"
  type        = string
  default     = "rootpassword"
}

resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "EC2 access for the full Tomato AI project"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  ingress {
    description = "App access"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "secure-sg"
  }
}

resource "aws_instance" "tomato_server" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = var.instance_type

  vpc_security_group_ids      = [aws_security_group.secure_sg.id]
  associate_public_ip_address = true
  user_data_replace_on_change = true
  key_name                    = var.ssh_key_name

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted             = true
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }

  user_data = <<-EOF
#!/bin/bash
set -euxo pipefail

exec > /var/log/user-data.log 2>&1

export DEBIAN_FRONTEND=noninteractive
APP_DIR="/opt/major_frontend"

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

# Add swap to reduce OOM risk during Docker build (TensorFlow is heavy).
if ! swapon --show | grep -q .; then
  (fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048)
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

retry 5 apt-get update -y
# Use Ubuntu repo packages for reliability.
retry 5 apt-get install -y --no-install-recommends ca-certificates curl git git-lfs docker.io docker-compose

systemctl enable --now docker
usermod -aG docker ubuntu || true

mkdir -p "$${APP_DIR}"

if [ -d "$${APP_DIR}/.git" ]; then
  git -C "$${APP_DIR}" fetch --all --prune
  git -C "$${APP_DIR}" checkout "${var.github_branch}"
  git -C "$${APP_DIR}" reset --hard "origin/${var.github_branch}"
else
  git clone --branch "${var.github_branch}" --depth 1 "${var.github_repo_url}" "$${APP_DIR}"
fi

# Pull large model artifacts stored in Git LFS.
git lfs install --system
git -C "$${APP_DIR}" lfs pull

git -C "$${APP_DIR}" rev-parse HEAD || true
ls -lh "$${APP_DIR}/tomato_leaf_hybrid_eff_final_disease" || true

cat >"$${APP_DIR}/.env" <<ENVFILE
APP_HOST_PORT=${var.app_port}
SECRET_KEY=${var.app_secret_key}
DB_HOST=db
DB_USER=root
DB_PASSWORD=${var.db_root_password}
DB_NAME=${var.db_name}
MYSQL_ROOT_PASSWORD=${var.db_root_password}
MYSQL_DATABASE=${var.db_name}
ENVFILE

cd "$${APP_DIR}"
docker-compose down || true
docker-compose up -d --build

sleep 20
docker-compose ps
docker-compose logs --tail 50 || true
EOF

  tags = {
    Name = "tomato-ai-server"
  }
}
