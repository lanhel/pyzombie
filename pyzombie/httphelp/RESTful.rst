==========================
pyzombie RESTful Resources
==========================


:Author:    Lance Finn Helsten (helsten@acm.org)
:Version:   0.0
:Copyright: © 2010 Lance Finn Helsten, All Rights Reserved.
:License:   GNU Affero General Public License version 3



Resources
--------------------
The following is a list of REST Resources URLs available in the pyzombie
RESTful server.

Any resource that responds to a GET shall respond to a HEAD method. All REST
resources shall respond to the OPTIONS method which shall return other available
methods and a URL to reference documentation for that method on that REST
resource.


URL Variable Components:
^^^^^^^^^^^^^^^^^^^^^^^^
    myserver
        This is the domain host name that has the pyzombie server.
    8008
        This is the default port of the pyzombie server.
    myexec
        This is the pyzombie generated unique executable name.
    myinstance
        This is the pyzombie generated unique executable instance name.


URL
^^^^^^^^^^^^^^^^^^^^^^^^

\http://myserver:8008/
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return the set of executables available on this server.
        
        **Representation:**
            ``Content-Type``
                * ``application/yaml``
                * ``text/html``
                * ``application/xhtml+xml``
        
    POST
        Add a new executable to the set of available executables.
        
        **Request**
            ``Content-Type``
                This should be a recognized internet media type that will
                allow proper execution of the uploaded file. If this is not
                given then ``application/octet-stream`` will be used and may
                result in execution failre.
        
        **Response**
            ``Location``: executable URL


\http://myserver:8008/add
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return an HTML form to allow a new executable image to be uploaded
        to this server.

        **Representation:**
            ``Content-Type``
                * ``text/html``
                * ``application/xhtml+xml``

        
    POST
        Add a new executable to the set of available executables.
        
        **Request**
            ``Content-Type``
                * ``multipart/form-data`` for executables uploaded from a form.
        
        **Response**
            ``Location``: executable information page


\http://myserver:8008/myexec
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return the executable image.

        **Representation:**
            ``Content-Type``
                * ``text/plain`` for interpreted executables (should have '#!')
                * ``application/octet-stream`` for compiled executables.

    PUT
        Change the executable image.

        **Request**
            ``Content-Type``
                This must be a recognized internet media type that is the
                same as the original executable: i.e. changing file types
                from Python to Perl is not allowed. If this is not given
                then ``application/octet-stream`` will be used as a default.
        
        **Status**
        
        1. ``200 (OK)`` if no instances of the executable are active.
        
        2. ``202 (Accepted)`` if an instance of the executable is active.
        

    DELETE
        Remove the named executable from the set of available executables, and
        remove any associated data.
        
        **Status**
        
        1. ``200 (OK)`` if no instances of the executable are active.
        
        2. ``202 (Accepted)`` if an instance of the executable is active.


\http://myserver:8008/myexec/start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return an HTML form to allow environment and argument definition
        from a browser to start an instance of an executable when the form
        is submitted.
        
        **Representation:**
            ``Content-Type``
                * ``text/html``
                * ``application/xhtml+xml``


\http://myserver:8008/myexec/instances/
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return the set of instances available for this executable.
        
        **Representation:**
            ``Content-Type``
                * ``application/yaml``
                * ``text/html``
                * ``application/xhtml+xml``
        
    POST
        Create a new executable instance. The content must contain the
        environment and the command line arguments to be used in creating
        the instance.
        
        **Representation:**
            ``Content-Type``
                * ``application/yaml``

        **Response**
            ``Location``: executable instance URL


\http://myserver:8008/myexec/instances/myinstance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return a representation of the instance which will contain the
        runtime environment, the command line arguments, the current
        state of the executable instance, the timeout for the instance,
        and the removal date of the instance.
        
        **Representation:**
            ``Content-Type``
                * ``application/yaml``

        
    DELETE
        Remove the instance and reclaim resources used in tracking the
        instance.


\http://myserver:8008/myexec/instances/myinstance/stdin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Return an HTML form that will allow text to be sent to the executable
        instance.
        
        **Representation:**
            ``Content-Type``
                * ``text/html``
                * ``application/xhtml+xml``

    POST
        Add data to the standard input stream being read by the executable
        instance.

        **Request**
            ``Content-Type``
                * ``text/plain`` with UTF-8 encoding


\http://myserver:8008/myexec/instances/myinstance/stdout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Read data from the instance standard output stream. If the instance
        is currently executing then this will use chunked transfer encoding,
        otherwise it will send the entire file.
        
        **Representation:** ``text/plain`` with UTF-8 encoding


\http://myserver:8008/myexec/instances/myinstance/stderr
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    GET
        Read data from the instnace standard error stream. If the instance
        is currently executing then this will use chunked transfer encoding,
        otherwise it will send the entire file.

        **Representation:** ``text/plain`` with UTF-8 encoding






Representations
--------------------

YAML
^^^^^^^^^^^^^^^^^^^^
The following schemata is written in Rx_ which has validators for Perl,
JavaScript, Ruby, Python, and PHP.

**Content-Type**:  ``application/yaml``.

* Create Executable Instance::

    ---- # Executable Instance Creation
    type:               //rec
    required:
    optional:
        environment:
            type:       //map
            values:     //str
        arguments:
            type:       //arr
            contents:   {type: //str}
            length:     {min: 1}


* Executable Instance Representation::

    ---- # Executable Instance
    type:               //rec
    required:
        self:           //str   # URL to this representation
        executable:     //str   # URL to the executable representation
        status:         //one
            # Integer is the exit code when instance has terminated
            # String is the ISO 8601 datetime when instance shall be forced to terminate
        remove:         //str   # ISO 8601 datetime the instance is removed
        environment:
            type:       //map
            values:     //str
        arguments:
            type:       //arr
            contents:   {type: //str}
            length:     {min: 1}
    optional:
        
            



HTML
^^^^^^^^^^^^^^^^^^^^
HTML shall only be used in response content. It is available to allow access
to the server from a normal browser.

**Content-Type**: ``text/html``, ``application/xhtml+xml``






.. Hyperlinks
.. _Rx: http://rx.codesimply.com/
.. _Python: http://www.python.org/

