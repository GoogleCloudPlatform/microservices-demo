**Example 1: To deploy apps and run stack commands**

The following examples show how to use the ``create-deployment`` command to deploy apps and run stack commands.  Notice that the quote (``"``) characters in the JSON object that specifies the command are all preceded by escape characters (\\). Without the escape characters, the command might return an invalid JSON error.

The following ``create-deployment`` example deploys an app to a specified stack. ::

    aws opsworks create-deployment \
        --stack-id cfb7e082-ad1d-4599-8e81-de1c39ab45bf \
        --app-id 307be5c8-d55d-47b5-bd6e-7bd417c6c7eb 
        --command "{\"Name\":\"deploy\"}"

Output::

    {
        "DeploymentId": "5746c781-df7f-4c87-84a7-65a119880560"
    }

**Example 2: To deploy a Rails App and Migrate the Database**

The following ``create-deployment`` command deploys a Ruby on Rails app to a specified stack and migrates the database. ::

    aws opsworks create-deployment \
        --stack-id cfb7e082-ad1d-4599-8e81-de1c39ab45bf \
        --app-id 307be5c8-d55d-47b5-bd6e-7bd417c6c7eb \
        --command "{\"Name\":\"deploy\", \"Args\":{\"migrate\":[\"true\"]}}"

Output::

    {
        "DeploymentId": "5746c781-df7f-4c87-84a7-65a119880560"
    }

For more information on deployment, see `Deploying Apps <https://docs.aws.amazon.com/opsworks/latest/userguide/workingapps-deploying.html>`__ in the *AWS OpsWorks User Guide*.

**Example 3: Run a Recipe**

The following ``create-deployment`` command runs a custom recipe, ``phpapp::appsetup``, on the instances in a specified stack. ::

    aws opsworks create-deployment \
        --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb \
        --command "{\"Name\":\"execute_recipes\", \"Args\":{\"recipes\":[\"phpapp::appsetup\"]}}"

Output::

    {
        "DeploymentId": "5cbaa7b9-4e09-4e53-aa1b-314fbd106038"
    }

For more information, see `Run Stack Commands <https://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks-commands.html>`__ in the *AWS OpsWorks User Guide*.

**Example 4: Install Dependencies**

The following ``create-deployment`` command installs dependencies, such as packages or Ruby gems, on the instances in a
specified stack. ::

    aws opsworks create-deployment \
        --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb \
        --command "{\"Name\":\"install_dependencies\"}"

Output::

    {
        "DeploymentId": "aef5b255-8604-4928-81b3-9b0187f962ff"
    }

For more information, see `Run Stack Commands <https://docs.aws.amazon.com/opsworks/latest/userguide/workingstacks-commands.html>`__ in the *AWS OpsWorks User Guide*.
