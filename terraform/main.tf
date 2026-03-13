provider "aws" {
  region = "ap-south-1"
}

resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "Secure EC2 access"

  # SSH access only from your IP
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["182.76.246.162/32"]
  }

  # Flask app access
  ingress {
    description = "Flask access"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["182.76.246.162/32"]
  }

  # Restricted outbound HTTPS access
  egress {
    description = "Allow GitHub and Ubuntu repo"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"

    cidr_blocks = [
      "140.82.112.0/20",   # GitHub
      "185.199.108.0/22",  # GitHub CDN
      "91.189.88.0/21"     # Ubuntu repositories
    ]
  }

  tags = {
    Name = "secure-sg"
  }
}

resource "aws_instance" "tomato_server" {

  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.secure_sg.id]

  associate_public_ip_address = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted   = true
    volume_size = 20
  }

  user_data = <<-EOF
#!/bin/bash

exec > /var/log/user-data.log 2>&1

echo "Starting EC2 setup..."

apt-get update -y
apt-get install -y git docker.io

systemctl start docker
systemctl enable docker

cd /home/ubuntu

echo "Cloning repository..."
git clone https://github.com/CoderShrikant02/major_frontend.git

cd major_frontend

echo "Building docker image..."
docker build -t tomato-ai .

echo "Running container..."
docker run -d -p 5000:5000 tomato-ai

echo "Deployment finished"
EOF

  tags = {
    Name = "tomato-ai-server"
  }
}