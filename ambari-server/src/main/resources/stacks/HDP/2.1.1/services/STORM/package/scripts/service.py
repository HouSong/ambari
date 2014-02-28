#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""


from resource_management import *
from resource_management.core.shell import call
import subprocess


def service(
    name,
    action='start'):
  import params
  import status_params

  pid_file = status_params.pid_files[name]
  no_op_test = format("ls {pid_file} >/dev/null 2>&1 && ps `cat {pid_file}` >/dev/null 2>&1")

  if name == 'ui':
    process_cmd = "^java.+backtype.storm.ui.core$"
  elif name == "rest_api":
    process_cmd = format("java -jar {rest_lib_dir}/`ls {rest_lib_dir} | grep -wE storm-rest-[0-9.-]+\.jar` server")
  else:
    process_cmd = format("^java.+backtype.storm.daemon.{name}$")

  crt_pid_cmd = format("pgrep -f \"{process_cmd}\" > {pid_file}")

  if action == "start":
    if name == "rest_api":
      cmd = format("env PATH=$PATH:{java64_home}/bin {process_cmd} {rest_api_conf_file} > {log_dir}/restapi.log")
    else:
      cmd = format("env JAVA_HOME={java64_home} PATH=$PATH:{java64_home}/bin /usr/bin/storm {name}")

    Execute(cmd,
           not_if=no_op_test,
           user=params.storm_user,
           wait_for_finish=False
    )
    Execute(crt_pid_cmd,
            user=params.storm_user,
            logoutput=True,
            tries=6,
            try_sleep=10
    )

  elif action == "stop":
    process_dont_exist = format("! ({no_op_test})")
    cmd = format("kill `cat {pid_file}` >/dev/null 2>&1")
    Execute(cmd,
            not_if=process_dont_exist
    )

    Execute(process_dont_exist,
            tries=5,
            try_sleep=3
    )
    Execute(format("rm -f {pid_file}"))
