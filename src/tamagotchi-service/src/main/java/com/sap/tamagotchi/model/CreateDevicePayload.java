package com.sap.tamagotchi.model;

public class CreateDevicePayload {
    private final String owner;
    private final Color color;

    public CreateDevicePayload(String owner, Color color) {
        this.owner = owner;
        this.color = color;
    }

    public String getOwner() {
        return owner;
    }

    public Color getColor() {
        return color;
    }
}
