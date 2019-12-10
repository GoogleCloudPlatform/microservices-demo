/**
 * Copyright (c) 2019, SAP SE, All rights reserved.
 */
package com.sap.tamagotchi.model;

import java.util.Collection;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import com.sap.tamagotchi.service.TamagotchiService;

public class Owner {

    private TamagotchiService tamagotchiService;

    private Collection<Device> devices;

    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    @Autowired
    public Owner(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
        // start();
    }

    @Scheduled(fixedDelay = 5000)
    public void setData() {
        for (Device d : tamagotchiService.getDevices()) {
            double random = Math.random();

            if (random <= 0.5) {
                Care care = new Care();
                care.setFeed(-(int) (random * 10));
                tamagotchiService.takeCare(d.getDeviceId(), new Care());
            } else {
                Care care = new Care();
                care.setFeed((int) (random * 10));
                tamagotchiService.takeCare(d.getDeviceId(), new Care());
            }

        }

    }



    public void start() {
        // Update device map
        final ScheduledFuture<?> handleGetMap = scheduler.scheduleAtFixedRate(getMapRunner, 0, 1, TimeUnit.MINUTES);
        scheduler.schedule(new Runnable() {
            @Override
            public void run() {
                handleGetMap.cancel(true);
            }
        }, 60, TimeUnit.MINUTES);

        // Add userType and doAction
        final ScheduledFuture<?> handleAction = scheduler.scheduleAtFixedRate(getMapRunner, 0, 5, TimeUnit.MINUTES);
        scheduler.schedule(new Runnable() {
            @Override
            public void run() {
                handleAction.cancel(true);
            }
        }, 60, TimeUnit.MINUTES);
    }

    Runnable getMapRunner = new Runnable() {
        @Override
        public void run() {
            getMap();
        }
    };

    Runnable actionRunner = new Runnable() {
        @Override
        public void run() {
            addUserType();
            addAction();
        }
    };

    public void getMap() {
        Collection<Device> currentDevices = tamagotchiService.getDevices();

    }

    public void addUserType() {

    }

    public void addAction() {

    }
}
