package com.sap.tamagotchi.model;

import java.time.Instant;
import java.util.Collection;
import java.util.Collections;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;

public class Device extends Thread {

    private final String getDeviceId = UUID.randomUUID().toString();
    private final String owner;
    private final Color color;
    private final Instant born = Instant.now();
    private final Queue<String> messages = new ConcurrentLinkedQueue<String>();

    public Device(String owner, Color color) {
        this.owner = owner;
        this.color = color;
    }

    public String getDeviceId() {
        return getDeviceId;
    }

    public String getOwner() {
        return owner;
    }

    public Color getColor() {
        return color;
    }

    public Instant getBorn() {
        return born;
    }

    public boolean hasMessages() {
        return !messages.isEmpty();
    }

    public Collection<IoTMessage> getMessages() {
        return Collections.emptyList();
    }
}
