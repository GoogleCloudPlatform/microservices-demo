package behavior

import (
	"errors"
	"math/rand"
)

type BehaviorExecutor struct {
	Behavior Behavior
}

func NewBehaviorExecutor(behavior Behavior) *BehaviorExecutor {
	return &BehaviorExecutor{Behavior: behavior}
}

func (be *BehaviorExecutor) ExecuteRandomTask() error {
	weightedTasks := be.Behavior.GetWeightedTasks()
	totalWeight := 0
	for _, wt := range weightedTasks {
		totalWeight += wt.Weight
	}

	choice := rand.Intn(totalWeight)
	for _, wt := range weightedTasks {
		choice -= wt.Weight
		if choice < 0 {
			return wt.Task.Perform()
		}
	}
	return errors.New("no task executed")
}
