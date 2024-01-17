package random

import (
	"errors"
	"math/rand"

	logs "github.com/sirupsen/logrus"
)

// ChoiceString selects a random element from a slice of strings.
//
//	@param slice
//	@return string
//	@return error
func ChoiceString(slice []string) (string, error) {
	if len(slice) == 0 {
		return "", errors.New("empty string slice")
	}
	index := rand.Intn(len(slice))
	logs.WithFields(logs.Fields{
		"type":  "string",
		"index": index,
	}).Trace("Random choice made from string slice")
	return slice[index], nil
}

// ChoiceInt selects a random element from a slice of integers.
//
//	@param slice
//	@return int
//	@return error
func ChoiceInt(slice []int) (int, error) {
	if len(slice) == 0 {
		return 0, errors.New("empty integer slice")
	}
	index := rand.Intn(len(slice))
	logs.WithFields(logs.Fields{
		"type":  "integer",
		"index": index,
	}).Trace("Random choice made from integer slice")
	return slice[index], nil
}
