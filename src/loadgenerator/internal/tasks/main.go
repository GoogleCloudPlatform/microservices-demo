package tasks

// Task defines the interface for a task that can be performed.
type Task interface {
	Perform() error
}

// WeightedTask is a replacement for TaskSet
type WeightedTask struct {
	Task   Task
	Name   string
	Weight int
}
