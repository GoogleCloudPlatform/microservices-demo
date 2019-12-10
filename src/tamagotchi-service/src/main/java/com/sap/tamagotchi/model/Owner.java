/**
 * Copyright (c) 2019, SAP SE, All rights reserved.
 */
package com.sap.tamagotchi.model;

import com.sap.tamagotchi.service.TamagotchiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class Owner {

    private TamagotchiService tamagotchiService;

    @Autowired
    public Owner(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
    }

    @Scheduled(fixedDelay = 5000)
    public void setData() {
        for (Device d : tamagotchiService.getDevices()) {
            double random = Math.random();
            Care care = new Care();

            if (random <= 0.5) {
                care.setFeed(-(int) (random * 10));
            } else {
                care.setFeed((int) (random * 10));
            }
            tamagotchiService.takeCare(d.getId(), care);
        }
    }
}
