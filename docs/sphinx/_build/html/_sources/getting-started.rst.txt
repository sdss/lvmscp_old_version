
.. _getting-started:

Getting started
============================


Introduction
-------------

 We assume that you are comfortable with asynchronous programming and 'asyncio' API. SCP stands for 'Spectrograph Control Package' and lvmscp is the actor that controls the lower level actors which are controlling devices inside the spectrograph. lvmscp is composed of the code based on the sdss software framework CLU. Among them, ‘sdss-clu’ is applied to create an actor that controls each hardware and executes communication.

In 'CLU', We''' define what an *actor* is: and actor is a piece of software that performs a well defined task (control a CCD camera, interface with a database) and is a *server* that receives *commands* and replies with a series of *keywords*. If you are not familiar with those concepts, the `CLU's documentation <https://clu.readthedocs.io/en/latest/index.html>`_ is a good reference place.

We will expand on these concepts in following sections.

Installation
-------------

.. include:: ../../README.rst
  :start-line: 2

Hardware Components
--------------------------
    
Here is the Hardware and Software Component Architecture diagram in spectrograph.

.. image:: _static/HW__conf_20210506_LCO.png
    :align: center



