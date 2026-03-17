# 🚀 Jenkins CI/CD Pipeline for AWS Deployment

This project contains a **Jenkins Pipeline that automatically deploys an application to an AWS EC2 instance using Terraform and Docker**.

The pipeline performs the following tasks automatically:

- Clones the GitHub repository
- Generates Terraform variables dynamically
- Runs security scans
- Creates infrastructure on AWS
- Deploys the application using Docker
- Verifies the deployment on EC2

---

# 🏗 Project Architecture

Jenkins → GitHub → Terraform → AWS EC2 → Docker → Application

1. **Jenkins** runs the pipeline.
2. **GitHub** stores the application source code.
3. **Terraform** provisions AWS infrastructure.
4. **AWS EC2** hosts the application.
5. **Docker & Docker Compose** run the application containers.

---

# ⚙️ Technologies Used

- Jenkins (CI/CD automation)
- Terraform (Infrastructure as Code)
- AWS EC2
- Docker
- Docker Compose
- Trivy (Security scanning)
- GitHub

---

# 📂 Pipeline Stages

## 1. Checkout

The pipeline fetches the application code from GitHub.

Repository used:
