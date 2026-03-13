provider "aws" {
  region = "ap-south-1"
}

# -----------------------------
# Security Group
# -----------------------------
resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "Secure access for EC2 instance"

  ingress {
    description = "SSH access from my IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"

    cidr_blocks = ["182.76.246.162/32"]
  }

  ingress {
    description = "Flask App Access"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"

    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "secure-sg"
  }
}

# -----------------------------
# EC2 Instance
# -----------------------------
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

  # Auto Deploy App
  user_data = <<-EOF
              #!/bin/bash

              apt update -y
              apt install -y python3-pip git

              cd /home/ubuntu

              git clone https://github.com/CoderShrikant02/major_frontend.git

              cd major_frontend

              pip3 install -r requirements.txt

              nohup python3 app.py --host 0.0.0.0 --port 5000 > app.log 2>&1 &

              EOF

  tags = {
    Name = "tomato-ai-server"
  }
}