#!/bin/bash
set -e

# script to compile python protos
#
# requires gRPC tools:
#   pip install -r requirements.txt

python -m grpc_tools.protoc -I../../pb --python_out=. --grpc_python_out=. ../../pb/demo.proto
