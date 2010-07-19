

Internal states
===============

Internally there are five internal states, one of which the the application is
in at any given time during execution:

.. image:: states.png

INIT
  Application is initialised.

IDLE (default)
  The application is doing nothing.

DISCONNECTED
  No connection to the server can be established. In regular intervals, which
  are not as frequent as in IDLE, the state will be changed back to IDLE to
  check for recovered connectivity.

ALERT
  A change to the state of one or more games has been found of which the user 
  will be notified.

ERROR
  A non-recoverable error has occurred. User intervation is necessary.

State changes
-------------

The rules for progressing from one state to the other are as follows:

INIT |arrow| IDLE:
  application is initialised

IDLE |arrow| DISCONNECTED:
  no connection to service

IDLE |arrow| ALERT:
  a change in one (or several) of the user's games was found that requires
  action from the user

IDLE |arrow| ERROR:
  non-recoverable error which requires user intervation

  Examples:

  * authentication error
  * IOError while traing to read/write config

ALERT |arrow| IDLE:
  1. user has reacted to notification
  2. games' states changed in the mean-time making user interaction unnecessary

DISCONNECTED |arrow| IDLE:
  serice is responsive again

ERROR |arrow| IDLE:
  (all) existing errors have been solved

.. |arrow| unicode:: U+02192 .. RIGHTWARDS ARROW

