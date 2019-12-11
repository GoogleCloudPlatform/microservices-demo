package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

public class DefunctNotification implements IoTMessage {

    @JsonProperty("message")
    private final String message;

    public DefunctNotification(String message) {
        this.message = message;
    }

    @JsonIgnore
    @Override
    public String getTopic() {
        return "tamagotchi-defunct";
    }

    public String getMessage() {
        return message;
    }

}
