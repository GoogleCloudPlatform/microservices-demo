package behavior

import (
	"errors"
	"math/rand"

	"github.com/sirupsen/logrus"
)

type BehaviorExecutor struct {
	Behavior Behavior
}

func NewBehaviorExecutor(behavior Behavior) *BehaviorExecutor {
	return &BehaviorExecutor{Behavior: behavior}
}

// ExecuteRandomTask selects a random task based on the weights defined in the behavior and executes it.
// It returns the name of the executed task and any error encountered during task execution.
func (be *BehaviorExecutor) ExecuteRandomTask() (string, error) {
	weightedTasks := be.Behavior.GetWeightedTasks()
	totalWeight := 0
	for _, wt := range weightedTasks {
		totalWeight += wt.Weight
	}

	choice := rand.Intn(totalWeight)
	for _, wt := range weightedTasks {
		choice -= wt.Weight
		if choice < 0 {
			logrus.Debugf("Executing task: %s", wt.Name)
			err := wt.Task.Perform()
			if err != nil {
				return "", err
			}
			return wt.Name, nil
		}
	}
	return "", errors.New("no task executed")
}
