// Copyright 2023 Google LLC
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
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

/*
As part of an optional Google Cloud demo, you can run an additional "packaging" microservice (HTTP server).
This file contains code related to the frontend and the "packaging" microservice.
*/

var (
	packagingServiceUrl string
)

type PackagingInfo struct {
	Weight float32 `json:"weight"`
	Width  float32 `json:"width"`
	Height float32 `json:"height"`
	Depth  float32 `json:"depth"`
}

// init() is a special function in Golang that will run when this package is imported.
func init() {
	packagingServiceUrl = os.Getenv("PACKAGING_SERVICE_URL")
}

func isPackagingServiceConfigured() bool {
	return packagingServiceUrl != ""
}

func httpGetPackagingInfo(productId string) (*PackagingInfo, error) {
	// Make the GET request
	url := packagingServiceUrl + "/" + productId
	fmt.Println("Requesting packaging info from URL: ", url)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	// Check the response status code
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("Unexpected status code: %d", resp.StatusCode)
	}

	// Read the JSON response body
	responseBody, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	// Decode the JSON response into a PackagingInfo struct
	var packagingInfo PackagingInfo
	err = json.Unmarshal(responseBody, &packagingInfo)
	if err != nil {
		return nil, err
	}

	return &packagingInfo, nil
}
