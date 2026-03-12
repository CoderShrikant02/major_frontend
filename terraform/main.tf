provider "aws" {
  region = "ap-south-1"
}

resource "aws_security_group" "insecure_sg" {
  name        = "insecure-security-group"
  description = "Allow SSH from anywhere (intentional vulnerability)"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # ⚠️ Intentional vulnerability
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "tomato_server" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.insecure_sg.id]

  tags = {
    Name = "tomato-ai-server"
  }
}