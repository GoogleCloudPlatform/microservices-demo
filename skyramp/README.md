# Skyramp

[Skyramp](https://skyramp.dev) makes cloud-native testing easy; both in the inner dev loop and in your testing pipeline. 

We are currently working hard to make Skyramp available to everyone. To get early access or learn more, contact us at info@skyramp.dev.

## Installation

Skyramp works on the following operating systems and requires a container run-time:

### Operating Systems

|       | Min Version |
| :---    |    :----:   |
| Mac OS X |   11.0     |
| Ubuntu | 18.04 |
| CentOS      |   8.04     |
| Fedora   |  36.0       |
| Windows Subsystem for Linux (WSL)   |    1    |

### Container run-time

Today, Skyramp supports Docker as the container run-time. 

You can either install [Docker Desktop](https://docs.docker.com/desktop/) (which comes prepackaged with everything you need) or just the [Docker Engine](https://docs.docker.com/engine/install/ ).

> **Note**:  The minimum supported version of Docker Engine is 20.10.0.
Support for Podman is coming soon. 

### Installation script

Run the following command to install Skyramp. 

``` bash
bash -c "$(curl -fsSL <paste url from Skyramp support email here>)"
```

Follow the step-by-step instructions in the terminal to complete installation.

> **Note**: Windows Subsytem for Linux (WSL) occassionally has an issue where there appears to be no internet connectivity despite the host
machine being connected. You can verify this by pinging google.com from WSL. Restarting the host machine usually fixes connectivity issues in WSL.

## Check Installation

Check your installation of Skyramp by running the following command:

```bash
skyramp version
```

## Uninstallation

If for any reason you want to uninstall skyramp, run the following command:

```bash
/bin/bash -c "$(curl -fsSL <paste url from Skyramp support email here>)"
```


# Documentation
To learn how to use Skyramp, check out our [documentation](https://skyramp.dev/docs).
