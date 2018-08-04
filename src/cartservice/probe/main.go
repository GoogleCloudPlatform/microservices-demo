// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"context"
	"log"
	"os"
	"time"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/cartservice/probe/genproto"

	"google.golang.org/grpc"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		log.Fatal("probe is executed without PORT env var")
	}
	log.Printf("probe executing on port %q", port)

	conn, err := grpc.DialContext(context.TODO(),
		"127.0.0.1:"+port,
		grpc.WithBlock(),
		grpc.WithTimeout(time.Second*3),
		grpc.WithInsecure(),
	)
	if err != nil {
		log.Fatalf("probe failed: failed to connect: %+v", err)
	}
	defer conn.Close()

	if _, err := pb.NewCartServiceClient(conn).GetCart(context.TODO(),
		&pb.GetCartRequest{UserId: "exec-probe-nonexistinguser"}); err != nil {
		log.Fatalf("probe failed: failed to query: %+v", err)
	}
	log.Println("probe successful")
}
