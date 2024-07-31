resource "aws_ecr_repository" "repo" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }

  force_delete = true
}


# Replace this block with the commented below to run this on Windows machine

resource "null_resource" "ecr_image" {
   triggers = {
     python_file = md5(file(var.lambda_function_local_path))
     docker_file = md5(file(var.docker_image_local_path))
   }

   provisioner "local-exec" {
     command = <<EOF
             aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${var.account_id}.dkr.ecr.${var.region}.amazonaws.com
             cd ../
             docker build -t ${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag} .
             docker push ${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag}
         EOF
   }
}

# resource "null_resource" "ecr_image" {
#    triggers = {
#      python_file = md5(file(var.lambda_function_local_path))
#      docker_file = md5(file(var.docker_image_local_path))
#    }

#    provisioner "local-exec" {
#      command = <<EOT
#              echo "Starting ECR login process"
#              aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${var.account_id}.dkr.ecr.${var.region}.amazonaws.com
#              echo "Logged in to ECR"
#              cd ..
#              docker build -t ${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag} -f deployment/streaming/Dockerfile .
#              echo "Docker build completed"
#              docker push ${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag}
#              echo "Docker push completed"
#              echo "Sleep completed, proceeding with Terraform"
#          EOT
#     interpreter = ["PowerShell", "-Command"]
#    }
# }

data "aws_ecr_image" "lambda_image" {
  depends_on = [
    null_resource.ecr_image
  ]
  repository_name = var.ecr_repo_name
  image_tag       = var.ecr_image_tag
}

output "image_uri" {
  value     = "${aws_ecr_repository.repo.repository_url}:${data.aws_ecr_image.lambda_image.image_tag}"
}
