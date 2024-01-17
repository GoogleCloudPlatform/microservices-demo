package random

import (
	"testing"
)

func TestChoiceString(t *testing.T) {
	testSlice := []string{"apple", "banana", "cherry"}
	result, err := ChoiceString(testSlice)
	if err != nil {
		t.Errorf("ChoiceString returned an error: %s", err)
	}
	if !containsString(testSlice, result) {
		t.Errorf("ChoiceString returned a string not in the slice: got %v", result)
	}
}

func TestChoiceInt(t *testing.T) {
	testSlice := []int{1, 2, 3, 4, 5}
	result, err := ChoiceInt(testSlice)
	if err != nil {
		t.Errorf("ChoiceInt returned an error: %s", err)
	}
	if !containsInt(testSlice, result) {
		t.Errorf("ChoiceInt returned an int not in the slice: got %v", result)
	}
}

// containsString checks if a string slice contains a specific string.
func containsString(slice []string, str string) bool {
	for _, item := range slice {
		if item == str {
			return true
		}
	}
	return false
}

// containsInt checks if an int slice contains a specific int.
func containsInt(slice []int, num int) bool {
	for _, item := range slice {
		if item == num {
			return true
		}
	}
	return false
}
