package behavior

import "github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/internal/tasks"

// Behavior interface defines the interface for a different behaviors think UserBehavior, AdminBehavior, etc.
type Behavior interface {
	GetWeightedTasks() []tasks.WeightedTask
}
