package com.shoppingassistantservice.core;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan("com.shoppingassistantservice.controller")
public class ShoppingAssistantApplication {

	public static void main(String[] args) {
		SpringApplication.run(ShoppingAssistantApplication.class, args);
	}

}
