#!/usr/bin/env python3
import os
import shutil
import subprocess

data_directory = "data/postgres"

# Stop the PostgreSQL server
subprocess.run(["pg_ctl", "-D", data_directory, "stop"])

# Remove the data directory
shutil.rmtree(data_directory)

