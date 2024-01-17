package tasks

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestViewCart_Perform_Success(t *testing.T) {
	viewCart := &ViewCart{}
	err := viewCart.Perform()

	assert.Nil(t, err)
}
