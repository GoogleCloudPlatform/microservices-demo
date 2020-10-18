# How to Generate Golang Code with This

```
go get google.golang.org/protobuf/cmd/protoc-gen-go google.golang.org/grpc/cmd/protoc-gen-go-grpc

# make sure link to the Go binaries obtained from above command is included in your PATH
protoc --go_out=. --go_opt=paths=source_relative     --go-grpc_out=. --go-grpc_opt=paths=source_relative     demo.proto
```
