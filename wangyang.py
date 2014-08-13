#!/usr/bin/env python
#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2013 INRIA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Lucia Guevgeozian <lucia.guevgeozian_odizzio@inria.fr>

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState

import os
#wangyang,define function to create node than return a gid,represent a unique entity
def create_node(ec, username, pl_user, pl_password, hostname=None, country=None,
                operatingSystem=None, minBandwidth=None, minCpu=None,critical=False):
    #wangyang,registter a node,type is PlanetlabNode,node = gid
    node = ec.register_resource("PlanetlabNode")

    if username:
        ec.set(node, "username", username)
    if pl_user:
        ec.set(node, "pluser", pl_user)
    if pl_password:
        ec.set(node, "plpassword", pl_password)

    if hostname:
        ec.set(node, "hostname", hostname)
    if country:
        ec.set(node, "country", country)
    if operatingSystem:
        ec.set(node, "operatingSystem", operatingSystem)
    if minBandwidth:
        ec.set(node, "minBandwidth", minBandwidth)
    if minCpu:
        ec.set(node, "minCpu", minCpu)
    ec.set(node, "critical", critical)
    ec.set(node, "cleanHome", True)
    ec.set(node, "cleanProcesses", True)
    
    return node

#wangyang,define function to create app then return a gid,represent a unique entity
def add_app(ec, command, node, sudo=None, video=None, depends=None, forward_x11=None, \
        env=None):
    app = ec.register_resource("LinuxApplication")
    if sudo is not None:
        ec.set(app, "sudo", sudo)
    if video is not None:
        ec.set(app, "sources", video)
    if depends is not None:
        ec.set(app, "depends", depends)
    if forward_x11 is not None:
        ec.set(app, "forwardX11", forward_x11)
    if env is not None:
        ec.set(app, "env", env)
    ec.set(app, "command", command)
    #wangyang,connect app to a node,means map a app gid to a node gid
    ec.register_connection(app, node)

    return app
#wangyang,defind experimen id 
exp_id = "wangyangtest"

# Create the entity Experiment Controller,return gid:
ec = ExperimentController(exp_id)

# Register the nodes resources:

# The username in this case is the slice name, the one to use for login in 
# via ssh into PlanetLab nodes. Replace with your own slice name.
username = "ict_111"

# The pluser and plpassword are the ones used to login in the PlanetLab web 
# site. Replace with your own user and password account information.
pl_user = "wangyang2013@ict.ac.cn"
pl_password =  "myplcmyslice"
hostnames1 = ['node1.njupt.edu.cn']
apps = []
nodes = []
#wangyang,if hostname in first group,here we define 'node1.njupt.edu.cn' as a server
for hostname in hostnames1:
    #wangyang,create a node,this is server
    node = create_node(ec, username, pl_user, pl_password, hostname=hostname)
    #first_set_nodes.append(node)
    #wangyang,define command than will be executed on the server node
    command = "wget -O server.out ftp://159.226.40.196/server.out && echo \"$HOSTNAME is OK.\"               >report && chmod 777 server.out && ./server.out"
    #wangyang,create an app that will execute the command above,this function connect app and node and return a gid representing this connection
    app_getserver = add_app(ec,command,node)
#wangyang,other nodes in this slice,if there are 2 nodes,i from 0-1
i = 0    
for i in range(3) :
    node = create_node(ec, username, pl_user, pl_password)
    #second_set_nodes.append(node)
    command = "wget -O ~/client.out ftp://159.226.40.196/client.out && echo \"$HOSTNAME is OK.\" > ~/report"
    app_getclient = add_app(ec,command,node)
    apps.append(app_getclient)
    command = "chmod 777 ~/client.out && cd ~ && ./client.out 202.119.236.130"
    app_startclient = add_app(ec,command,node)
    apps.append(app_startclient)
    #wangyang,startclient must execute after getclient and startserver
    ec.register_condition(app_startclient, ResourceAction.START, app_getclient, ResourceState. STOPPED)
    ec.register_condition(app_startclient, ResourceAction.START, app_getserver, ResourceState. STARTED)

    
# Deploy the experiment:
#wangyang,run all apps 
ec.deploy()


# Wait until the applications are finish to retrive the traces:
ec.wait_finished(apps)
#wangyang,retrive the trace in the server node named report,then save this record into local machine
for trace in ec.get_traces(app_getserver):
    trace_stream = ec.trace(app_getserver, 'report')
    f = open("./report.txt", "w")
    f.write(trace_stream)
    f.close()

ec.shutdown()

# END
