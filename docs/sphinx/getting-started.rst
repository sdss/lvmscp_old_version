
.. _getting-started:

Getting started with SCP
============================

Introduction
-------------

In this section we provide a qiuck introduction to SCP. We assume that you are comfortable with aynchronous programming and 'asyncio'. SCP (Spectrograph Control Package) is a software that controls the spectrograph in SDSS-V LVMi project. SCP is composed of code based on sdss software framework. Among them, ‘sdss-clu’ is applied to create an actor that controls each hardware and executes communication.

In 'CLU', We''' define what an *actor* is: and actor is a piece of software that performs a well defined task (control a CCD camera, interface with a database) and is a *server* that receives *commands* and replies with a series of *keywords*. If you are not familiar with those concepts, the `CLU's documentation <https://clu.readthedocs.io/en/latest/index.html>`_ is a good reference place.

We will expand on these concepts in following sections.



Hardware Component
--------------------------
    
Here is the Hardware and Software Component Architecture diagram in spectrograph.

.. image:: _static/HW__conf_20210506_LCO.png
    :align: center



.. _running-SCP:

Running an SCP
----------------

SCP can be started by simply 'SCP start' command ::

    lvmscp start

This will start SCP but will not start the porting. For that you need to use ''clu'' command. ::

    clu

which will be responsible for implementing the protocol. Clu creates an actor and the actor processes pre-defined tasks.
SCP is composed of OSU actor, NPS actor, and Archon actor. Each actor controls and manages hardware connected with Controller.

You can learn more about the archon `here <https://sdss-archon.readthedocs.io/en/latest/>`_.

Actor
--------

Archon Actor

lvmieb Actor

lvmnps Actor



Configuration files
------------------------

