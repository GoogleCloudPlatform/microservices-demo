// Copyright 2022 Skyramp, Inc.
//
//	Licensed under the Apache License, Version 2.0 (the "License");
//	you may not use this file except in compliance with the License.
//	You may obtain a copy of the License at
//
//	http://www.apache.org/licenses/LICENSE-2.0
//
//	Unless required by applicable law or agreed to in writing, software
//	distributed under the License is distributed on an "AS IS" BASIS,
//	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//	See the License for the specific language governing permissions and
//	limitations under the License.
package main

import (
	"os"

	"github.com/sirupsen/logrus"
)

type Items struct {
	ProductId string `json:"product_id" yaml:"product_id"`
	Quantity  int    `json:"quantity" yaml:"quantity"`
}
type Cart struct {
	UserId string  `json:"user_id" yaml:"user_name"`
	Items  []Items `json:"items" yaml:"items"`
}

const (
	serverCrt         = "server.crt"
	serverKey         = "server.key"
	defaultThriftPort = "50000"
	defaultRestPort   = "60000"
)

func init() {
	log = logrus.New()
	log.Level = logrus.DebugLevel
	log.Out = os.Stdout
}

func main() {
	var (
		port  string
		found bool
	)
	port, found = os.LookupEnv("REST_PORT")
	if !found {
		port = defaultRestPort
		log.Infof("env REST_PORT is not se, using default %s", defaultRestPort)
	}
	runGrpc()
	runRest(port)
	port, found = os.LookupEnv("THRIFT_PORT")
	if !found {
		port = defaultThriftPort
		log.Infof("env THRIFT_PORT is not set, using default %s", defaultThriftPort)
	}
	runThrift(port)
	select {}
}
