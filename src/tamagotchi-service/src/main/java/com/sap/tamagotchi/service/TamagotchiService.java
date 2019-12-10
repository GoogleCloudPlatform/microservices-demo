package com.sap.tamagotchi.service;

import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.publisher.PublisherService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

@Service
public class TamagotchiService {

    private final PublisherService publisherService;

    private final Map<String, Device> deviceRegistry = new HashMap<>();

    @Autowired
    public TamagotchiService(PublisherService publisherService) {
        this.publisherService = publisherService;
    }

    public Device getDevice(String deviceId) {
        return deviceRegistry.get(deviceId);
    }

    public Collection<Device> getDevices() {
        return deviceRegistry.values();
    }
}
