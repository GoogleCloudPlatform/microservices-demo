/**
 * Copyright (c) 2019, SAP SE, All rights reserved.
 */
package com.sap.tamagotchi.model;

import static com.sap.tamagotchi.service.TamagotchiService.DEVICE_EVENT_PROCESSOR_SCHEDULE;
import java.util.Collection;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import com.sap.tamagotchi.service.TamagotchiService;

@Service
@EnableScheduling
public class Owner {

    private TamagotchiService tamagotchiService;

    @Autowired
    public Owner(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
    }

    @Scheduled(fixedDelay = DEVICE_EVENT_PROCESSOR_SCHEDULE)
    public void setData() {
        for (Device d : tamagotchiService.getDevices()) {

            String userName = d.getOwner().substring(0, d.getOwner().indexOf("@")).toUpperCase();

            int careAboutThePet = 0;

            for (int i = 0; i < userName.length(); i++) {
                if (d.getColor().toString().indexOf(userName.charAt(i)) != -1) {
                    careAboutThePet++;
                }
            }

            Care care = new Care();

            if (careAboutThePet == 0) {
                care.setFeed(-5);
            } else {
                care.setFeed(5);
            }
            tamagotchiService.takeCare(d.getId(), care);
        }
    }

    public void killRendomDevice() {

        Collection<Device> devices = tamagotchiService.getDevices();

        if (devices != null) {
            Device first = devices.iterator().next();
            Care care = new Care();
            care.setFeed(-1000);
            tamagotchiService.takeCare(first.getId(), care);
        }
    }
}
