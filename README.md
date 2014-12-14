pypgTAP
=====
https://github.com/itissid/pypgTAP#pypgtap

*Bringing python closer to postgres.* [pgTAP](pgtap.org)

What issue does this framework solve?
=====
- pgTAP can be executed to run tests over your Postgres codebase, but to test the code base
on local and CI environments was particularly hard. Postgres needs to be set up and a postgres
test server needs to be instantiated. Next you want to instantiate your test environment with
stored procedures and run the tests. You want to have some test data to load its many lines...
This is a lot of work! Enter pypgTAP.
- This is a thin python layer over pgTAP that provides teh following:
 - An integrated utility to start and stop postgres test servers to run pgTAP tests.
 - Virtualenv python support: The industry standard for using python is vritualen and tox and its a pain to use pgTAP
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
 - The above facilitates reuse of existing python code base, *And hey we don't need an excuse to write in pure python :)*
 - It also makes it easy for people to do SDLC in pure python when its necessary and just use it seamlessly from within
postgres's plpythonu
 - You can test standalone SQL code(Like for Postgres Derivatives like redshift) or test stored procedures

Added Feature(s)
=====
- Currently you can start and stop a postgres server using my python utilities. Its very easy. Install the lastest Postgres(I think its 9.3). Although older versions may work but I haven't tested it yet.

Upcoming feature(s):
=====
- Will be adding virtualenv support shortly along with lots of examples.

A taste of things.
=====
- First you need to install postgres on your favorite OS. [Postgres](http://www.postgresql.org/download/macosx/)
***You Must install it with python support***
- Once installed make sure the postgres server isn't started. Postgres starts by default due to init.d configuration
that is built into its packaging (Idiotic over configuration IMHO).

How to use in your project
=====
Assuming you have python project:
```
pip install https://github.com/itissid/pypgTAP#pypgtap
```
This will give you access to two scripts in your bin/directory
`start_harness` and `stop_harness`

You can follow the examples to write tests in the test/ folder.
