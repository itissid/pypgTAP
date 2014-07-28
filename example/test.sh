#!/bin/bash
# TODO: Change the relative_testkit_path to '../rsTAP/test_kit/' when using it in your
# project.
psql -Xf test/ddl/test_example_ddl.sql -v project_root=`pwd` -v relative_testkit_path='../test_kit/'
