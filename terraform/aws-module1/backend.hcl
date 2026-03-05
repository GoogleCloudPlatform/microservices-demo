# Remplace ce bucket par celui cree dans bootstrap-state.
bucket         = "blackfriday-terraform-state-mt5team01"
key            = "module1/terraform.tfstate"
region         = "eu-west-3"
dynamodb_table = "blackfriday-terraform-locks"
encrypt        = true
