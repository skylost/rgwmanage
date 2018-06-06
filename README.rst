**Rgwmanage**
============
Client library for Ceph rados gateway

QuickStart
----------

.. code:: bash

    # Rgwmanage installation:
    git clone https://github.com/skylost/rgwmanage
    cd rgwmanage && sudo pip install .
    sudo python setup.py install

    # Play with it! :
    rgwm
    (rgwm) user-list


CLI Usage
---------

.. code:: raw

    Commands:
      user-list      List all users.
      user-show      Shows user details.
      user-update    Updates user metadata.
