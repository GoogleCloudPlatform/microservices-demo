package com.sap.tamagotchi.controller;

import java.util.concurrent.atomic.AtomicLong;

import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.publisher.PublisherService;
import com.sap.tamagotchi.service.TamagotchiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DeviceController {

    private static final String template = "Hello, %s!";
    private final AtomicLong counter = new AtomicLong();
    private final TamagotchiService tamagotchiService;

    @Autowired
    public DeviceController(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
    }

    @RequestMapping("devices/{deviceId}")
    public Device getDevice(String deviceId) {
        return tamagotchiService.getDevice(deviceId);
    }
}
