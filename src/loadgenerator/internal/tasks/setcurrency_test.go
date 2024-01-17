package tasks

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSetCurrency_Perform_Success(t *testing.T) {
	setCurrency := &SetCurrency{
		CurrencyCode: "USD",
	}
	err := setCurrency.Perform()

	assert.Nil(t, err)
}
