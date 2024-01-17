package behavior

import "github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/internal/tasks"

type UserBehavior struct {
}

// GetWeightedTasks returns a slice of tasks.WeightedTask representing the weighted tasks for user behavior.
func (ub *UserBehavior) GetWeightedTasks() []tasks.WeightedTask {
	return []tasks.WeightedTask{
		{Task: &tasks.Index{}, Weight: 1, Name: "Index"},
		{Task: &tasks.SetCurrency{}, Weight: 2, Name: "SetCurrency"},
		{Task: &tasks.BrowseProduct{}, Weight: 10, Name: "BrowseProduct"},
		{Task: &tasks.AddToCart{}, Weight: 2, Name: "AddToCart"},
		{Task: &tasks.ViewCart{}, Weight: 3, Name: "ViewCart"},
		{Task: &tasks.Checkout{}, Weight: 1, Name: "Checkout"},
	}
}
