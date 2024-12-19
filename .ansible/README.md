# Deployment via Ansible

This has been tested for Ubuntu 24.04.

## Prerequisites

1. Install Ansible

```
sudo apt install ansible-core
```

2. Adjust the hosts file (currently configured to run on localhost)

## Usage

1. `cd` into .ansible directory

```
cd .ansible
```

2. Start the playbook

```
ansible-playbook main.yaml -i hosts
```
