rsTAP
=====
https://github.com/itissid/rsTAP#rstap

*AWS Redshift ETL testing and validation framework.*

What issue does this framework solve?
=====
-  Redshift is a clone of pg 8. But it is severly restricted for testing with extant
frameworks. This framework provides some boiler plate over the extant [pgTAP](pgtap.org) framework.
-  ETL queries that are not one off and part of production jobs are genrally chained
and several steps long while tranforming data.
-  Its not easy to test and QA rigorously certain important aspects of larg ETL projects.

How does it work?
=====
So we reuse a bulk of the code from an extant library called pgTAP. I only added missing
features to work for redshift ETL scripts:
-  Like for example loading of data from a JSON via a JSONPath file
-  Executing a script that is in a file in the file system by reading it as a string
and passing it to a procedure.

Upcoming feature(s):
=====
-  Scaffolding for adding python hooks. If you are not familiar with plSQL and want to
do something fancy, NP. Add a hooks/ directory to your project root and add python modules there.
- Adding chef recipes to deploy on CI frameworks like jenkins for end to end integration.


A taste of things.
=====
-  First you need to install postgres on your favorite OS. [Postgres](http://www.postgresql.org/download/macosx/)

-  Once installed fire up a postgresql instance using something like:

``` postgres --config-file=/usr/local/var/postgres/postgresql.conf ```

YOU CAN TRANSPLANT YOUR .conf FILE LOCATION ABOVE IF YOU ARE ON A DIFFERENT PLATFORM.

- go to the example directory to see some examples of things in action.
```
        ./test.sh
```

How to use in your project
=====
Add a submodule to your project root:

```
git submodule add git@github.com:itissid/rsTAP.git rsTAP/
```
Now when you create your scripts. Come back to this project and modify the
relative path of the test kit in `test.st` accordingly. We will be removing this
anomaly soon so everything works right out of the box!
