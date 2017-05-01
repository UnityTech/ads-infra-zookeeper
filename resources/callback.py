#!/usr/bin/python

import os
import sys
import json
import requests
    
"""
Kontrol callback managing an Apache Zookeeper ensemble.
"""

if __name__ == '__main__':

    def _http(pod, cmd, extra={}):
        try:
            url = 'http://%s:8000/script' % pod['ip']
            js = {'cmd': cmd}
            js.update(extra)
            reply = requests.put(url, data=json.dumps(js), headers={'Content-Type':'application/json'})
            reply.raise_for_status()
            return reply.text
            
        except Exception:
            return None

    #
    # - fetch the current pod snapshot ($POD) and user data attached to this
    #   cluster ($STATE), both being serialized to json
    # - 
    #
    pods = json.loads(os.environ['PODS'])
    brokers = {str(pod['seq']): pod['ip'] for pod in pods}
    print >> sys.stderr, "ensemble with %d brokers" % len(brokers)
    for pod in pods:
        print >> sys.stderr, ' - pod #%d -> %s' % (pod['seq'], pod['payload'])

    #
    # - fetch the previous state details from $STATE
    # - if $STATE is not there that's a brand new cluster
    #
    state = json.loads(os.environ['STATE']) if 'STATE' in os.environ else \
    {
        'brokers': {}
    }

    prev = state['brokers']
    if sorted(brokers) != sorted(prev):
        
        #
        # - turn all the brokers off in order
        # - switch the local state machines to the 'stop' state
        #
        delta = len(brokers) - len(prev)
        print >> sys.stderr, 'ensemble change detected (%+d brokers)' % delta
        replies = [_http(pod, 'echo WAIT stop | socat -t 60 - /tmp/sock') for pod in pods]
        assert all(reply == 'OK' for reply in replies)
        
        #
        # - start each broker one by one
        # - switch the local state-machine to the 'start' state
        # - they get confired with their own index and peer map
        # - the index is simply our pod sequence counter
        #
        for pod in pods:

            js = \
            {
                'key': str(pod['seq']),
                'brokers': brokers
            }

            reply = _http(pod, "echo WAIT start '%s' | socat -t 60 - /tmp/sock" % json.dumps(js))
            assert reply == 'OK'

    #
    # - serialize our state to stdout
    # - it will be written back to etcd and passed to $STATE upon the next
    #   invokation
    #
    state['brokers'] = brokers
    print json.dumps(state)