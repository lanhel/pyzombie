########
pyzombie
########

.. toctree::
    :hidden:

    install
    modules
    changelog
    glossary

pyzombie is an HTTP RESTful server that will allow arbitrary code to
be executed on a remote host. The principle purpose is to allow
test code to be loaded and executed remotely on hosts for systems
that have no direct network presence.

.. WARNING::
    Executing pyzombie on any machine will open it up to all attacks
    by anyone or anything that has access to the internet (TCP/IP)
    address and port. There is no security within pyzombie to prevent
    unauthorized access.

