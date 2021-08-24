.. _Examples:

Examples with lvmscp
=====================

Starting the Actor
----------------------

lvmscp actor provides the control system to manage the spectrograph.
First you have to start the actor by the terminal command line in the python virtual environment that you installed the lvmscp package. ::

  $ lvmscp start

If you want to start with debugging mode, you can start like this.
In this case, you can finish the software by putting ctrl + c ::

  $ lvmscp start --debug

Also you can check the status of the actor is running by this command ::

  $ lvmscp status

After your work is done, you can finish the actor by this command ::

  $ lvmscp stop

Finally, you can restart(stop -> start) the actor when the actor is running by this command ::

  $ lvmscp restart


Running the Actor
----------------------

If you started the actor by the *lvmscp start* command, you can interface with the actor by the clu CLI(Command Line Interface) ::

  $ clu

If you want to ignore the status message from other actors, you can use this command ::

  $ clu -b

Then you will enter to the clu CLI. 
You can check if the actor is running by the ping-pong commands.