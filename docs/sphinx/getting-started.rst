
.. _getting-started:

Getting started with lvmscp
============================

Introduction
-------------

In this section we provide a qiuck introduction to the lvmscp actor. We assume that you are comfortable with asynchronous programming and 'asyncio' API. SCP stands for 'Spectrograph Control Package' and lvmscp is the actor that controls the lower level actors which are controlling devices inside the spectrograph. lvmscp is composed of the code based on the sdss software framework CLU. Among them, ‘sdss-clu’ is applied to create an actor that controls each hardware and executes communication.

In 'CLU', We''' define what an *actor* is: and actor is a piece of software that performs a well defined task (control a CCD camera, interface with a database) and is a *server* that receives *commands* and replies with a series of *keywords*. If you are not familiar with those concepts, the `CLU's documentation <https://clu.readthedocs.io/en/latest/index.html>`_ is a good reference place.

We will expand on these concepts in following sections.



Hardware Component
--------------------------
    
Here is the Hardware and Software Component Architecture diagram in spectrograph.

.. image:: _static/HW__conf_20210506_LCO.png
    :align: center



.. _running-lvmscp:

Running lvmscp
----------------

SCP can be started by simply 'lvmscp start' command ::

    lvmscp start

This will start lvmscp actor but will not able to interface with the actor. For that you need to activate the ''clu'' CLI(Command Line Interface). ::

    clu

which will be responsible for implementing the protocol. Clu creates an actor and the actor processes pre-defined tasks.
lvmscp is composed of lvmieb actor, lvmnps actor, and archon actor. Each actor controls and manages hardware connected with Controller.

You can learn more about the archon `here <https://sdss-archon.readthedocs.io/en/latest/>`_.

Actors
--------

archon Actor

lvmieb Actor

lvmnps Actor



Configuration files
------------------------

