#  Terraform does not create this resource, but instead "adopts" it into management
resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}

# Create a security group that allows inbound connections on port 5432
resource "aws_security_group" "sgPostgreSQL" {
  vpc_id = aws_default_vpc.default.id
  name = "sgPostgreSQL"

  ingress {
    protocol  = "tcp"
    self      = true
    from_port = 5432
    to_port   = 5432
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sgPostgreSQL"
  }
}

# Setup random password for DB
resource "random_password" "db_password" {
  length  = 16
  special = false
}

# Provision AWS PostgreSQL Database
resource "aws_db_instance" "dbCovid19" {
  identifier             = "db-covid19-etl"
  allocated_storage      = 10
  max_allocated_storage  = 100
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "13.4"
  instance_class         = "db.t3.micro"
  name                   = var.db_name
  username               = var.db_user
  password               = random_password.db_password.result
  vpc_security_group_ids = [aws_security_group.sgPostgreSQL.id]
  multi_az               = false # Outside of scope of free tier
  publicly_accessible    = true
  skip_final_snapshot    = true
  apply_immediately      = true # If this is false, changes won't take effect until next maintenance window
  enabled_cloudwatch_logs_exports = ["postgresql"]
}