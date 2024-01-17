package loadgen

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
	flag.Parse()

	fmt.Printf("Starting load generator with %d users targeting %s\n", *userCount, *baseURL)

	rand.Seed(time.Now().UnixNano())
	config := config.ReadConfig()

	userBehavior := &behavior.UserBehavior{}
	behaviorExecutor := behavior.NewBehaviorExecutor(userBehavior)

	for i := 0; i < *userCount; i++ {
		go func() {
			for {
				err := behaviorExecutor.ExecuteRandomTask()
				if err != nil {
					logrus.Errorf("Error executing task: %s", err.Error())
				}

				// Wait for some time before the next action
				time.Sleep(time.Duration(rand.Intn(config.MaxWaitTime)) * time.Second)
			}
		}()
	}

	select {}
}
