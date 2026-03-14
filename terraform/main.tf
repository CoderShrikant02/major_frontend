provider "aws" {
  region = "ap-south-1"
}

data "aws_vpc" "default" {
  default = true
}

variable "admin_cidr" {
  description = "Trusted CIDR for SSH access"
  type        = string
  default     = "182.76.246.162/32"
}

variable "app_port" {
  description = "HTTP port exposed by the demo page"
  type        = number
  default     = 80
}

variable "project_title" {
  description = "Title shown on the demo page"
  type        = string
  default     = "Tomato Leaf Disease Detection"
}

resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "Demo EC2 access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  ingress {
    description = "Public HTTP demo page"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
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

exec > /var/log/user-data.log 2>&1

export DEBIAN_FRONTEND=noninteractive

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

retry 5 apt-get update -y
retry 5 apt-get install -y --no-install-recommends python3 curl

mkdir -p /opt/tomato-demo

PUBLIC_IP="$$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "Unavailable")"

cat >/opt/tomato-demo/index.html <<HTML
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${var.project_title}</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f1e8;
      --panel: #fffdf8;
      --text: #18230f;
      --accent: #5d8736;
      --muted: #5f6f52;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top, rgba(93,135,54,0.16), transparent 32%),
        linear-gradient(135deg, var(--bg), #efe3d0);
      color: var(--text);
    }
    .card {
      width: min(720px, calc(100vw - 32px));
      padding: 40px;
      background: var(--panel);
      border: 1px solid rgba(24,35,15,0.12);
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(24,35,15,0.12);
    }
    h1 {
      margin: 0 0 20px;
      font-size: clamp(2rem, 5vw, 3.5rem);
      line-height: 1.05;
    }
    p {
      margin: 12px 0;
      font-size: 1.15rem;
      color: var(--muted);
    }
    strong {
      color: var(--accent);
    }
  </style>
</head>
<body>
  <main class="card">
    <h1>${var.project_title}</h1>
    <p><strong>Public IP:</strong> $${PUBLIC_IP}</p>
    <p><strong>Status:</strong> Running on AWS EC2</p>
    <p><strong>Deployment:</strong> Terraform + Jenkins</p>
  </main>
</body>
</html>
HTML

cd /opt/tomato-demo
nohup python3 -m http.server ${var.app_port} --bind 0.0.0.0 >/var/log/tomato-demo.log 2>&1 &
EOF

  tags = {
    Name = "tomato-ai-server"
  }
}
