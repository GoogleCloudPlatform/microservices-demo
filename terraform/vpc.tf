resource "aws_vpc" "project-vpc" {
  cidr_block = "10.0.0.0/16"

  tags = tomap({
    "Name" = "tsp-eks-node",
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}
data "aws_availability_zones" "available" {
  state = "available"
}
resource "aws_subnet" "project-vpc" {
  count = 2

  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.project-vpc.id

  tags = tomap({
    "Name" = "tsp-eks-node",
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_internet_gateway" "project-vpc" {
  vpc_id = aws_vpc.project-vpc.id

  tags = {
    Name = "eks-vpc"
  }
}

resource "aws_route_table" "project-vpc" {
  vpc_id = aws_vpc.project-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.project-vpc.id
  }
}

resource "aws_route_table_association" "project-vpc" {
  count = 2

  subnet_id      = aws_subnet.project-vpc.*.id[count.index]
  route_table_id = aws_route_table.project-vpc.id
}
