# Meet and eat - Registration system

This is the registration system for a event called 
"[meet&eat](http://www.exmatrikulationsamt.de/meetandeat)".

## Install

This is a python Flask application and a set of helper tools
for retrieving and transforming the data. The easiest way to
get it running is to use a `virtualenv` and install all the
requirements frim the `requirements.txt` file:

    $ git clone https://github.com/janLo/meet-and-eat-registration-system.git
    $ mkdir -p ~/.virtualenvs
    $ virtualenv ~/.virtualenvs/meet-and-eat-registration-system
    $ . ~/.virtualenvs/meet-and-eat-registration-system/bin/activate
    $ pip install -r meet-and-eat-registration-system/requirements.txt


## Debug

Then you can chdir into the `src` directory and start the
debug webserver or call the helper scripts:

    $ . ~/.virtualenvs/meet-and-eat-registration-system/bin/activate
    $ cd meet-and-eat-registration-system/src
    $ ./debug_webapp.py

## Configuration

You need a configuration to run the application and many of the
helpers. A example config is provided. Simply copy the file
`src/webapp/cfg/config_example.py` to `src/webapp/cfg/config.py`
and change the values you need.

NOTE: You should at least set the password, SECRET_KEY and the
MAPQUEST_KEY. The mapquest stuff is needed to get the distances
between the locations. You can register your own app key at
http://developer.mapquest.com/web/products/open 


## Run

To deploy this you can use the uwsgi that is installed in the
virtualenv and put it behind a reverse proxy. The deployment
at "[meet&eat](http://www.exmatrikulationsamt.de/meetandeat)"
for example have a uwsg.ini:

    [uwsgi]
    http-socket = 127.0.0.1:5000
    spooler = ./spool
    import  = webapp.tasks
    pythonpath = src
    module = webapp:app
    workers = 4
    threads = 3
    harakiri = 30
    master = true
    static-map = /static=src/webapp/static
    touch-reload = uwsgi.ini

And a apache config:

    ProxyPass               /meetandeat/register http://localhost:5000/register
    <Location /meetandeat/register>
            ProxyPassReverse        http://localhost:5000/register
            RequestHeader           set X_SCRIPT_NAME /meetandeat
    </Location>

