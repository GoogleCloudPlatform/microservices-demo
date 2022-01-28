package main

import (
	"net/http"
	"os"
	"sync"

	"cloud.google.com/go/compute/metadata"
	"github.com/sirupsen/logrus"
)

const (
	DetailsAreNotLoaded = 0
	DetailsAreLoading   = 1
	DetailsAreLoaded    = 2
)

var deploymentDetailsMap = make(map[string]string)
var detailsLoadingStatus = DetailsAreNotLoaded
var detailsLoadingStatusMutex sync.Mutex // Ensures only 1 HTTP request loads deployment details.

func loadDeploymentDetails(httpRequest *http.Request) map[string]string {
	var metaServerClient = metadata.NewClient(&http.Client{})

	// The use of httpRequest here lets us to see HTTP request info in the logs.
	var log = httpRequest.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)

	podHostname, err := os.Hostname()
	if err != nil {
		log.Error("Failed to fetch the hostname for the Pod", err)
	}

	podCluster, err := metaServerClient.InstanceAttributeValue("cluster-name")
	if err != nil {
		log.Error("Failed to fetch the name of the cluster in which the pod is running", err)
	}

	podZone, err := metaServerClient.Zone()
	if err != nil {
		log.Error("Failed to fetch the Zone of the node where the pod is scheduled", err)
	}

	deploymentDetailsMap["HOSTNAME"] = podHostname
	deploymentDetailsMap["CLUSTERNAME"] = podCluster
	deploymentDetailsMap["ZONE"] = podZone

	log.WithFields(logrus.Fields{
		"cluster":  podCluster,
		"zone":     podZone,
		"hostname": podHostname,
	}).Debug("Loaded deployment details")

	detailsLoadingStatus = DetailsAreLoaded

	return deploymentDetailsMap
}

func getDeploymentDetailsIfLoaded(httpRequest *http.Request) map[string]string {
	detailsLoadingStatusMutex.Lock()
	defer detailsLoadingStatusMutex.Unlock()
	if detailsLoadingStatus == DetailsAreNotLoaded {
		detailsLoadingStatus = DetailsAreLoading
		go loadDeploymentDetails(httpRequest)
		return nil
	}
	return deploymentDetailsMap
}
