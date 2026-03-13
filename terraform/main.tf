provider "aws" {
  region = "ap-south-1"
}

resource "aws_security_group" "secure_sg" {
  name        = "secure-security-group"
  description = "Secure EC2 access"

  # SSH only from your IP
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"

    cidr_blocks = ["182.76.246.162/32"]
  }

  # Flask access only from your IP
  ingress {
    description = "Flask access"
    from_port   = 5000
    to_port     = 5000
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

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

  user_data = <<-EOF
#!/bin/bash
exec > /var/log/user-data.log 2>&1

apt-get update -y
apt-get install -y git python3-pip

cd /home/ubuntu

git clone https://github.com/CoderShrikant02/major_frontend.git

cd major_frontend

pip3 install -r requirements.txt

nohup python3 app.py --host 0.0.0.0 --port 5000 > flask.log 2>&1 &
EOF

  tags = {
    Name = "tomato-ai-server"
  }
}