#!/usr/bin/python

import os
import sys
import json
import zerorpc
    
"""
Kontrol callback managing an Apache Zookeeper ensemble and performing a rolling reconfiguration
upon any topology change.
"""

if __name__ == '__main__':

    assert 'KONTROL_PORT' in os.environ, '$KONTROL_PORT undefined (bug ?)'
    port = int(os.environ['KONTROL_PORT'])

    def _rpc(pod, cmd):
        
        try:

            #
            # - use zerorpc to request a script invokation against a given pod
            # - default on returning None upon failure
            #
            client = zerorpc.Client()
            client.connect('tcp://%s:%d' % (pod['ip'], port))
            return client.invoke(json.dumps({'cmd': cmd}))
            
        except Exception:
            return None

    #
    # - fetch the current pod snapshot ($POD) and user data attached to this
    #   cluster ($STATE), both being serialized to json
    # - if $STATE is not there that's a brand new cluster (e.g default it)
    #
    pods = json.loads(os.environ['PODS'])
    brokers = {str(pod['seq']): pod['ip'] for pod in pods}
    state = json.loads(os.environ['STATE']) if 'STATE' in os.environ else \
    {
        'brokers': {}
    }

    print >> sys.stderr, "ensemble with %d brokers" % len(brokers)
    for pod in pods:
        print >> sys.stderr, ' - pod #%d -> %s' % (pod['seq'], pod['payload'])

    #
    # - compare with the last known state
    # - if there is any broker change (e.g any new reported broker and any
    #   broker that is not responding anymore) trigger a re-configuration
    #
    prev = state['brokers']
    if sorted(brokers) != sorted(prev):
        
        #
        # - turn all the brokers off in order
        # - switch the local state machines to the 'stop' state
        #
        delta = len(brokers) - len(prev)
        print >> sys.stderr, 'change detected (%+d brokers)' % delta
        replies = [_rpc(pod, 'echo WAIT stop | socat -t 60 - /tmp/sock') for pod in pods]
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

            reply = _rpc(pod, "echo WAIT start '%s' | socat -t 60 - /tmp/sock" % json.dumps(js))
            assert reply == 'OK'

    #
    # - serialize our state to stdout
    # - it will be written back to etcd and passed to $STATE upon the next
    #   invokation
    #
    state['brokers'] = brokers
    print json.dumps(state)