**To register instances with a stack**

The following examples show a variety of ways to register instances with a stack that were created outside of AWS Opsworks.
You can run ``register`` from the instance to be registered, or from a separate workstation.
For more information, see `Registering Amazon EC2 and On-premises Instances`_ in the *AWS OpsWorks User Guide*.

.. _`Registering Amazon EC2 and On-premises Instances`: http://docs.aws.amazon.com/opsworks/latest/userguide/registered-instances-register-registering.html


**Note**: For brevity, the examples omit the ``region`` argument.

*To register an Amazon EC2 instance*

To indicate that you are registering an EC2 instance, set the ``--infrastructure-class`` argument
to ``ec2``.

The following example registers an EC2 instance with the specified stack from a separate workstation.
The instance is identified by its EC2 ID, ``i-12345678``. The example uses the workstation's default SSH username and attempts
to log in to the instance using authentication techniques that do not require a password,
such as a default private SSH key. If that fails, ``register`` queries for the password. ::

  aws opsworks register --infrastructure-class=ec2 --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb i-12345678

The following example registers an EC2 instance with the specifed stack from a separate workstation.
It uses the ``--ssh-username`` and ``--ssh-private-key`` arguments to explicitly
specify the SSH username and private key file that the command uses to log into the instance.
``ec2-user`` is the standard username for Amazon Linux instances. Use ``ubuntu`` for Ubuntu instances. ::

  aws opsworks register --infrastructure-class=ec2 --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --ssh-username ec2-user --ssh-private-key ssh_private_key i-12345678

The following example registers the EC2 instance that is running the ``register`` command.
Log in to the instance with SSH and run ``register`` with the ``--local`` argument instead of an instance ID or hostname. ::

  aws opsworks register --infrastructure-class ec2 --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --local

*To register an on-premises instance*

To indicate that you are registering an on-premises instance, set the ``--infrastructure-class`` argument
to ``on-premises``.

The following example registers an existing on-premises instance with a specified stack from a separate workstation.
The instance is identified by its IP address, ``192.0.2.3``. The example uses the workstation's default SSH username and attempts
to log in to the instance using authentication techniques that do not require a password,
such as a default private SSH key. If that fails, ``register`` queries for the password. ::

  aws opsworks register --infrastructure-class on-premises --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb 192.0.2.3

The following example registers an on-premises instance with a specified stack from a separate workstation.
The instance is identified by its hostname, ``host1``. The ``--override-...`` arguments direct AWS OpsWorks
to display ``webserver1`` as the host name and ``192.0.2.3`` and ``10.0.0.2`` as the instance's public and
private IP addresses, respectively. ::

  aws opsworks register --infrastructure-class on-premises --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --override-hostname webserver1 --override-public-ip 192.0.2.3 --override-private-ip 10.0.0.2 host1

The following example registers an on-premises instance with a specified stack from a separate workstation.
The instance is identified by its IP address. ``register`` logs into the instance using the specified SSH username and private key file. ::

  aws opsworks register --infrastructure-class on-premises --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --ssh-username admin --ssh-private-key ssh_private_key 192.0.2.3

The following example registers an existing on-premises instance with a specified stack from a separate workstation.
The command logs into the instance using a custom SSH command string that specifies
the SSH password and the instance's IP address. ::

  aws opsworks register --infrastructure-class on-premises --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --override-ssh "sshpass -p 'mypassword' ssh your-user@192.0.2.3" 

The following example registers the on-premises instance that is running the ``register`` command.
Log in to the instance with SSH and run ``register`` with the ``--local`` argument instead of an instance ID or hostname. ::

  aws opsworks register --infrastructure-class on-premises --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --local
  
*Output*: The following is typical output for registering an EC2 instance.

::

  Warning: Permanently added '52.11.41.206' (ECDSA) to the list of known hosts.
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  100 6403k  100 6403k    0     0  2121k      0  0:00:03  0:00:03 --:--:-- 2121k
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Initializing AWS OpsWorks environment
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Running on Ubuntu
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Checking if OS is supported
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Running on supported OS
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Setup motd
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Executing: ln -sf --backup /etc/motd.opsworks-static /etc/motd
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Enabling multiverse repositories
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Customizing APT environment
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Installing system packages
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Executing: dpkg --configure -a
  [Tue, 24 Feb 2015 20:48:37 +0000] opsworks-init: Executing with retry: apt-get update
  [Tue, 24 Feb 2015 20:49:13 +0000] opsworks-init: Executing: apt-get install -y ruby ruby-dev libicu-dev libssl-dev libxslt-dev libxml2-dev libyaml-dev monit
  [Tue, 24 Feb 2015 20:50:13 +0000] opsworks-init: Using assets bucket from environment: 'opsworks-instance-assets-us-east-1.s3.amazonaws.com'.
  [Tue, 24 Feb 2015 20:50:13 +0000] opsworks-init: Installing Ruby for the agent
  [Tue, 24 Feb 2015 20:50:13 +0000] opsworks-init: Executing: /tmp/opsworks-agent-installer.YgGq8wF3UUre6yDy/opsworks-agent-installer/opsworks-agent/bin/installer_wrapper.sh -r -R opsworks-instance-assets-us-east-1.s3.amazonaws.com
  [Tue, 24 Feb 2015 20:50:44 +0000] opsworks-init: Starting the installer
  Instance successfully registered. Instance ID: 4d6d1710-ded9-42a1-b08e-b043ad7af1e2
  Connection to 52.11.41.206 closed.

**More Information**

For more information, see `Registering an Instance with an AWS OpsWorks Stack`_ in the *AWS OpsWorks User Guide*.

.. _`Registering an Instance with an AWS OpsWorks Stack`: http://docs.aws.amazon.com/opsworks/latest/userguide/registered-instances-register.html



