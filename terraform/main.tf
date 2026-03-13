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

  # Flask access only from your IP
  ingress {
    description = "Flask from my IP"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["182.76.246.162/32"]
  }

  # outbound restricted to your IP instead of internet
  egress {
    description = "Restricted outbound HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["182.76.246.162/32"]
  }

  tags = {
    Name = "secure-sg"
  }
}

resource "aws_instance" "tomato_server" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.secure_sg.id]

  # enforce IMDSv2
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # encrypted root disk
  root_block_device {
    encrypted = true
    volume_size = 20
  }

  # disable public IP to reduce attack surface
  associate_public_ip_address = false

  tags = {
    Name = "tomato-ai-server"
  }
}