[Making postgres SDLC saner and fun](https://github.com/itissid/pypgTAP#pypgtap)
=====
For testing Stored Procedures and SQL queries you need to:
- Set up postgres environment.
- A Test server needs to be created. 
- Test environment needs to be setup.
- All your Test Suites need to be tested and Rollbacked (critical).
- Test data needs to be added. *YAAAAAWNNN!*
- CI integration, Docker. *YAAAAAAAAWNNNN!*

Thats a lot of work! Luckily pypgTAP solves a lot of these issues.
- *Oh And did we mention its in* **python** *?*


How does it do it?
=====
- It launches a throwaway postgres server, executes your tests, and discards the server and its files.
- pypgTAP can be executed to run multiple test suites over your Postgres codebase in an isolated manner.
- Virtualenv python support: The industry standard for using python is virtualenv and tox and its a pain to use pgTAP
 with python.
   *Remember plpython procedures execute on the postgres server and it cannot find python procedures executed by a
client like psql* Example:

```
CREATE OR REPLACE FUNCTION somefunction(arg1 varchar, arg2 varcha...)
RETURNS varchar
AS $$
   print 'Hello World'
   import myutility -- import error if myutility is not found in global site-packages

$$ LANGUAGE plpythonu strict;
```
 - The virtualenv sharing also facilitates reuse of existing python code base, *And hey we all just want an excuse to write in pure python :)*
 - It also makes it easy for people to do SDLC in pure python when its necessary and just use it seamlessly from within postgres's plpythonu.
 - You can refer to resources within your project root in your unit tests and pypgtap will find them for you.
 - You can test standalone SQL code (Like for Postgres Derivatives like redshift that don't support stored procedures) or test stored procedures.

Future Features
=====
I will be adding a Docker file for launching postgres and running unit tests for this project soon. You can copy paste that and run it by just changing a few variables. This should be easy, its just that I have not gotten to it yet.

Setting things up
=====
- First you need to install postgres on your favorite OS. [Postgres](http://www.postgresql.org/download/macosx/)
***You Must install it with python support***
- Once installed make sure the postgres server isn't started. Postgres starts by default on Debian-like systems
due to init.d configuration that is built into its packaging (Idiotic over configuration by package managers IMHO).

How to use in your project(example)
=====
Assuming you have python project:
```
pip install https://github.com/itissid/pypgTAP#pypgtap
```
This will give you access to two scripts in your bin/directory
`start_harness` and `run_all_tests` and `stop_harness`

##### Create a test file
```
mkdir -p /tmp/example_project/tests/

echo 'BEGIN;
-- Plan the tests.
SELECT plan(1);

-- Run the tests.
SELECT pass( 'My test passed, w00t!' );

-- Finish the tests and clean up.
SELECT * FROM finish();
ROLLBACK;' > /tmp/example_project/tests/test_hello_world.sql
```

Its just 3 easy steps now.

##### First start the server (note my virtualenv is active)

```
(nofailbowl)sid$ start_harness
The files belonging to this database system will be owned by user "sid".
This user must also own the server process.
....
creating subdirectories ... ok
...

Success. You can now start the database server using:
...
/usr/local/Cellar/postgresql/9.3.5_1/bin/postgres -D /var/folders/s7/.../T/__rs_tap_process_flags
or
    /usr/local/Cellar/postgresql/9.3.5_1/bin/pg_ctl -D /var/folders/s7/.../T/__rs_tap_process_flags -l logfile start
...
server started
```
##### Second run the tests

```
(nofailbowl)sid$ run_all_tests -w /tmp/example_project/
/tmp/example_project/  project test summary:

1..1
ok 1 - My test passed, w00t!

```

##### Last stop the harness!
```f
(failbowl)$ stop_harness
pg_ctl: server is running (PID: 8867)
/usr/local/Cellar/postgresql/9.3.5_1/bin/postgres "-D" "/var/folders/s7/.../T/__rs_tap_process_flags" "-h" "localhost" "-k" "/tmp"
waiting for server to shut down....LOG:  received smart shutdown request
LOG:  autovacuum launcher shutting down
LOG:  shutting down
LOG:  database system is shut down
 done
server stopped
```

Fin!

