timecard-gae
============

Set up
------

    $ git clone https://github.com/mindia/timecard-gae.git
    $ cd timecard-gae
    $ bundle install
    $ npm install
    $ mkvirtualenv --python=`which ptyhon2.7` timecard-gae
    (timecard-gae)$ pip install -r packages.txt

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
* Python 2.7
* npm
