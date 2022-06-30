
variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "db_name" {
  default = "Covid19DataETL"
}

variable "db_user" {
  default = "postgres"
}

variable "s3_bucket" {
  default = "Covid19"
}

variable "country_code" {
  default = "US"
}

variable "file_path_nyt" {
  default = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv"
}

variable "file_path_jh" {
  default = "https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv"
}

variable "file_path_google" {
  default = "https://storage.googleapis.com/covid19-open-data/v3/epidemiology.csv"
}