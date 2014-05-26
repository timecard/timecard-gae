timecard-gae
============

It is re-implement the Timecard (http://timecard-rails.herokuapp.com/) by Google App Engine / Python.
Only implements API via Google Cloud Endpoints.

Set up
------

    $ git clone https://github.com/MiCHiLU/timecard-gae.git
    $ cd timecard-gae
    $ bundle install
    $ npm install
    $ mkvirtualenv --python=`which ptyhon2.7` timecard-gae
    (timecard-gae)$ pip install -r packages.txt
    (timecard-gae)$ pip install -r packages-gae.txt

Build and Test
--------------

    (timecard-gae)$ make

Run development server
----------------------

    (timecard-gae)$ make runserver

then access to:

* admin server: http://localhost:8000
* instance server: http://localhost:8080/

Deploy
------

    (timecard-gae)$ make deploy

Dependencies
------------

* Bundler
* GNU Make
* Google App Engine SDK
* Python 2.7
* npm
