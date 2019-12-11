package com.sap.tamagotchi.controller;

import static com.sap.tamagotchi.model.Color.RED;
import static com.sap.tamagotchi.model.Color.YELLOW;
import static org.springframework.http.ResponseEntity.ok;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import com.sap.tamagotchi.model.Color;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sap.tamagotchi.model.CreateDevicePayload;
import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.service.TamagotchiService;

@RestController
public class DeviceController {

    private final TamagotchiService tamagotchiService;

    @Autowired
    public DeviceController(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
    }

    private static Color mapColor(String productId) {
        switch (productId) {
            case "66VCHSJNUP":
                return RED;
            default:
                return YELLOW;
        }
    }

    @RequestMapping("/devices/{deviceId}")
    public Device getDevice(String deviceId) {
        return tamagotchiService.getDevice(deviceId);
    }

    @RequestMapping("/devices")
    public Collection<Device> getDevices() {
        return tamagotchiService.getDevices();
    }

    @PostMapping("/devices")
    public ResponseEntity createDevice(@RequestBody Collection<CreateDevicePayload> payload) {
        List<Device> devices = new ArrayList<>();
        for (CreateDevicePayload p : payload) {
            devices.add(tamagotchiService.createDevice(new Device(p.getOwner(), mapColor(p.getProductId()))));
        }
        return ok(devices);
    }

    @RequestMapping("/_ah/warmup")
    public String warmup() {
        return "warming up";
    }
}
