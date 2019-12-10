package com.sap.tamagotchi.service;

import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.model.IoTMessage;
import com.sap.tamagotchi.publisher.PublisherService;

@Service
public class TamagotchiService {

    private final PublisherService publisherService;

    private final Map<String, Device> deviceRegistry = Collections.synchronizedMap(new HashMap<>());

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

    public Set<String> getDeviceIds() {
        return deviceRegistry.keySet();
    }

    public void createDevice(Device device) {
        deviceRegistry.put(device.getDeviceId(), device);
    }

    private void processDeviceEvents() {
        deviceRegistry
                .values()
                .parallelStream()
                .filter(d -> d.hasMessages())
                .forEach(d -> {
                    Collection<IoTMessage> messages = d.getMessages();

                });
    }
}
