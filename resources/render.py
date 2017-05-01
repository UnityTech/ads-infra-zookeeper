#!/usr/bin/python

import os
import json

from jinja2 import Environment, FileSystemLoader, Template


if __name__ == '__main__':

    #
    # - retrieve the input json payload from $INPUT
    #
    cfg = json.loads(os.environ['INPUT'])
    templates = Environment(loader=FileSystemLoader('.'))

    #
    # - grab the key for this broker
    # - set the current entry in zoo.cfg as 0.0.0.0:2888:3888
    #
    key = cfg['key']
    cfg['brokers'][key] = '0.0.0.0'

    #
    # - first set our server index
    # - this index is equal to the pod sequence index
    #
    template = Template('{{index}}')
    with open('/var/lib/zookeeper-3.4.9/myid', 'wb') as fd:
        fd.write(template.render(index=key))

    #
    # - render the zk config template with our peer bindings
    # - /opt/pod/distro is where the zookeeper archive is untar'ed
    # - the startup script in under /bin
    #
    template = templates.get_template('zoo.cfg')
    with open('/opt/zookeeper-3.4.9/conf/zoo.cfg', 'wb') as fd:
        fd.write(template.render(peers=cfg['brokers']))
