provider "aws" {
  region = "ap-south-1"
}

resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "Secure security group for EC2"

  ingress {
    description = "SSH access from my IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"

    cidr_blocks = ["182.76.246.162/32"]   # your public IP
  }

  egress {
    description = "Allow HTTPS outbound only"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"

    cidr_blocks = ["182.76.246.162/32"]   # restricted outbound
  }

  tags = {
    Name = "secure-sg"
  }
}

resource "aws_instance" "tomato_server" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.secure_sg.id]

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

  tags = {
    Name = "tomato-ai-server"
  }
}