package behavior

import "github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/internal/tasks"

type UserBehavior struct {
}

func (ub *UserBehavior) GetWeightedTasks() []tasks.WeightedTask {
	return []tasks.WeightedTask{
		{Task: &tasks.Index{}, Weight: 1},
		{Task: &tasks.SetCurrency{}, Weight: 2},
		{Task: &tasks.BrowseProduct{}, Weight: 10},
		{Task: &tasks.AddToCart{}, Weight: 2},
		{Task: &tasks.ViewCart{}, Weight: 3},
		{Task: &tasks.Checkout{}, Weight: 1},
	}
}
