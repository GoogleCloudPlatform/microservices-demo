package tasks

import (
	"testing"

	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/config"
	"github.com/MahmoudMahfouz/microservices-demo/src/loadgenerator/pkg/utils/random"
	"github.com/stretchr/testify/assert"
)

func TestAddToCart_Perform_Success(t *testing.T) {
	quantity, err := random.ChoiceInt(config.GetConfig().Quantity)
	if err != nil {
		assert.Nil(t, err)
	}

	product, err := random.ChoiceString(config.GetConfig().ProductIDs)
	if err != nil {
		assert.Nil(t, err)
	}
	addToCart := &AddToCart{
		ProductID: product,
		Quantity:  quantity,
	}
	err = addToCart.Perform()

	assert.Nil(t, err)
}
