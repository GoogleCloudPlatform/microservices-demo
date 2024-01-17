package tasks

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBrowseProduct_Perform_Success(t *testing.T) {
	browseProduct := &BrowseProduct{}
	err := browseProduct.Perform()

	assert.Nil(t, err)
}
