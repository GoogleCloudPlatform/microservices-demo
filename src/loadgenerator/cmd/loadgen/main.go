package main

import (
	"flag"
	"fmt"
	"math/rand"
	"time"

	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/internal/behavior"
	"github.com/sirupsen/logrus"
)

func main() {
	userCount := flag.Int("users", 10, "Number of concurrent users")
	baseURL := flag.String("url", "http://localhost:8080", "Base URL of the target application")
	verbose := flag.Bool("v", false, "Enable verbose logging (debug level)")

	flag.Parse()

	if *verbose {
		logrus.SetLevel(logrus.DebugLevel)
		logrus.Debug("Verbose logging enabled")
	}

	fmt.Printf("Starting load generator with %d users targeting %s\n", *userCount, *baseURL)

	rand.Seed(time.Now().UnixNano())
	config := config.SetConfig(*baseURL)

	// More behavior types can be added here + internal/behavior/XYZ.go
	userBehavior := &behavior.UserBehavior{}
	behaviorExecutor := behavior.NewBehaviorExecutor(userBehavior)

	// This loop starts a goroutine for each user, which will run forever
	for i := 0; i < *userCount; i++ {
		go func(userNo int) {
			for {
				name, err := behaviorExecutor.ExecuteRandomTask()
				if err != nil {
					logrus.Errorf("Error executing task: %s", err.Error())
				}
				logrus.Infof("User #%d performed task %s", userNo, name)

				// Wait for some time before the next action
				time.Sleep(time.Duration(rand.Intn(config.MaxWaitTime)) * time.Second)
			}
		}(i)
	}

	select {}
}
