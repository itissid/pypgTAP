rsTAP
=====
https://github.com/itissid/rsTAP#rstap

*AWS Redshift ETL testing and validation framework.*

What issue does this framework solve?
=====
-  Redshift is a clone of pg 8. But it is severly restricted for testing with extant
frameworks. This framework provides some boiler plate over the extant framework.
-  ETL queries that are not one off and part of production jobs are genrally chained
and several steps long.
-  Its not easy to test and QA rigorously certain aspects of large ETL projects

How does it work?
=====
So we reuse a bulk of the code from an extant library called pgTAP. I only added missing
features:
-  Like for example loading of data from a JSON via a JSONPath file
-  Executing a script that is in a file in the file system by reading it as a string
and passing it to a procedure.

Upcoming feature(s):
=====
-  Scaffolding for adding python hooks. If you are not familiar with plSQL and want to
do something fancy, NP. Add a hooks/ directory to your project root and add python modules there.


How to use.
=====
-  First you need to install postgres on your favorite OS. [Postgres](http://www.postgresql.org/download/macosx/)

-  Once installed fire up a postgresql instance using something like:

` postgres --config-file=/usr/local/var/postgres/postgresql.conf `
YOU CAN TRANSPLANT YOUR .conf FILE LOCATION ABOVE IF YOU ARE ON A DIFFERENT PLATFORM.

- go to the example directory to see some examples of things in action.
```
        ./test.sh
```
