package tasks

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestIndex_Perform_Success(t *testing.T) {
	index := &Index{}
	err := index.Perform()

	assert.Nil(t, err)
}
