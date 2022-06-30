resource "aws_ssm_parameter" "db_endpoint" {
  name        = "/${var.db_name}/database/endpoint"
  description = "Endpoint to connect to the ${var.db_name} database"
  type        = "String"
  value       = aws_db_instance.dbCovid19.address
}

resource "aws_ssm_parameter" "db_user" {
  name        = "/${var.db_name}/database/user"
  description = "Name of the ${var.db_name} database"
  type        = "String"
  value       = var.db_user
}

resource "aws_ssm_parameter" "db_password" {
  name        = "/${var.db_name}/database/password"
  description = "Password to the ${var.db_name} database"
  type        = "SecureString"
  value       = random_password.db_password.result
}

resource "aws_ssm_parameter" "db_name" {
  name        = "/${var.db_name}/database/name"
  description = "Name of the ${var.db_name} database"
  type        = "String"
  value       = var.db_name
}

resource "aws_ssm_parameter" "country_code" {
  name        = "/${var.db_name}/country/name"
  description = "Country code for data to filter"
  type        = "String"
  value       = var.country_code
}

resource "aws_ssm_parameter" "nyt_data" {
  name        = "/${var.db_name}/file/nyt"
  description = "URL for Covid19 data supplied by New York Times"
  type        = "String"
  value       = var.file_path_nyt
}

resource "aws_ssm_parameter" "jh_data" {
  name        = "/${var.db_name}/file/jh"
  description = "URL for Covid19 data supplied by John Hopkins University"
  type        = "String"
  value       = var.file_path_jh
}

resource "aws_ssm_parameter" "google_data" {
  name        = "/${var.db_name}/file/google"
  description = "URL for Covid19 data supplied by Google"
  type        = "String"
  value       = var.file_path_google
}