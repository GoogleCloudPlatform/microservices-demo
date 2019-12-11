package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class CreateDevicePayload {
    private final String userId;
    private final String productId;

    @JsonCreator
    public CreateDevicePayload(@JsonProperty("userId") String userId, @JsonProperty("productId") String productId) {
        this.userId = userId;
        this.productId = productId;
    }

    @JsonProperty("userId")
    public String getOwner() {
        return userId;
    }

    @JsonProperty("productId")
    public String getProductId() {
        return productId;
    }
}
