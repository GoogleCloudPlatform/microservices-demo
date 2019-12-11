package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Device {

    @JsonProperty("id")
    private final String id = UUID.randomUUID().toString();
    @JsonProperty("productId")
    private final String productId;
    @JsonProperty("owner")
    private final String owner;
    @JsonProperty("color")
    private final Color color;
    @JsonProperty("born")
    private final Instant born = Instant.now();
    @JsonProperty("healthScore")
    private int healthScore = 100;
    private final Queue<IoTMessage> messages = new ConcurrentLinkedQueue<>();

    public Device(String productId, String owner, Color color) {
        this.productId = productId;
        this.owner = owner;
        this.color = color;
    }

    @JsonProperty("id")
    public String getId() {
        return id;
    }

    @JsonProperty("productId")
    public String getProductId() {
        return productId;
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
    public String getBorn() {
        return born.toString();
    }

    @JsonProperty("healthScore")
    public int getHealthScore() {
        return healthScore;
    }

    @JsonProperty("isAlive")
    public boolean isAlive() {
        return healthScore > 1;
    }

    @JsonIgnore
    public void changeHealthScore(int delta) {
        int oldScore = healthScore;
        if (healthScore >= 1) {
            healthScore += delta;
            if (healthScore > 150)
                healthScore /= 10;
        }

        if (healthScore < 1) {
            healthScore = 0;
            messages.add(new DeviceEvent(id, productId, owner, color, born, healthScore, oldScore, Instant.now()));
        } else
            messages.add(new DeviceEvent(id, productId, owner, color, born, healthScore, null, Instant.now()));
    }

    @JsonIgnore
    public boolean hasMessages() {
        return !messages.isEmpty();
    }

    @JsonIgnore
    public Queue<IoTMessage> getMessages() {
        return messages;
    }
}
