# script to compile python protos
#
# requires gRPC tools:
#   python -m pip install grpcio-tools googleapis-common-protos

python -m grpc_tools.protoc -I../../pb --python_out=. --grpc_python_out=. ../../pb/demo.proto
