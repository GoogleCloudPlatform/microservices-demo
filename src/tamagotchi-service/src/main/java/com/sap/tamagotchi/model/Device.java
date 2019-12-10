package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Device {

    @JsonProperty("id")
    private final String getDeviceId = UUID.randomUUID().toString();
    @JsonProperty("owner")
    private final String owner;
    @JsonProperty("color")
    private final Color color;
    @JsonProperty("born")
    private final Instant born = Instant.now();
    private final Queue<IoTMessage> messages = new ConcurrentLinkedQueue<>();

    public Device(String owner, Color color) {
        this.owner = owner;
        this.color = color;
    }

    @JsonProperty("id")
    public String getDeviceId() {
        return getDeviceId;
    }

    @JsonProperty("owner")
    public String getOwner() {
        return owner;
    }

    @JsonProperty("color")
    public Color getColor() {
        return color;
    }

    @JsonProperty("born")
    public Instant getBorn() {
        return born;
    }

    @JsonIgnore
    public boolean hasMessages() {
        return !messages.isEmpty();
    }

    @JsonIgnore
    public Collection<IoTMessage> getMessages() {
        ArrayList<IoTMessage> m = new ArrayList<>();
        while (!messages.isEmpty()) {
            m.add(messages.poll());
        }
        return m;
    }
}
