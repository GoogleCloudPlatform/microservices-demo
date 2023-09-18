package com.example;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
@CucumberOptions(
        features = "src/test/resources",
        glue = "com.example", // Correct package name
        plugin = {"json:target/cucumber.json"},
        publish = true
)

public class TestRunner {}
