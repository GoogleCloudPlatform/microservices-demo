module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  availability_zones = var.availability_zones
}

module "security" {
  source = "./modules/security"

  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
}

module "ec2" {
  source = "./modules/ec2"

  project_name      = var.project_name
  ami_id            = var.ami_id
  instance_type     = var.instance_type
  subnet_id         = module.vpc.public_subnet_ids[0]
  security_group_id = module.security.ec2_sg_id
  key_name          = var.key_name
}

module "rds" {
  source = "./modules/rds"

  project_name      = var.project_name
  ami_id            = var.ami_id
  instance_type     = var.instance_type
  subnet_id         = module.vpc.public_subnet_ids[1]
  security_group_id = module.security.rds_sg_id
  key_name          = var.key_name
  db_username       = var.db_username
  db_password       = var.db_password
}

module "alb" {
  source = "./modules/alb"

  project_name      = var.project_name
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.public_subnet_ids
  security_group_id = module.security.alb_sg_id
  instance_id       = module.ec2.instance_id
}

# Modules securite

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
}

module "waf" {
  source = "./modules/waf"

  project_name = var.project_name
  alb_arn      = module.alb.alb_arn
}

module "secrets" {
  source = "./modules/secrets"

  project_name = var.project_name
}
