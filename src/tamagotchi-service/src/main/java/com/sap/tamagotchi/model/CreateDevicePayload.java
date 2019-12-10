package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class CreateDevicePayload {
    private final String owner;
    private final Color color;

    @JsonCreator
    public CreateDevicePayload(@JsonProperty("owner") String owner, @JsonProperty("color") Color color) {
        this.owner = owner;
        this.color = color;
    }

    @JsonProperty("owner")
    public String getOwner() {
        return owner;
    }

    @JsonProperty("color")
    public Color getColor() {
        return color;
    }
}
