from __future__ import print_function
#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import alsaseq
import alsamidi


def main(dest_client, file_name, display=False):
    seq = alsamidi.Seq()
    seq.read(file_name)
    events = alsamidi.merge(seq.tracks)
    seq.info()

    print(len(events), 'events')
    alsaseq.client('aseqplay', 0, 1, 1)
    alsaseq.connectto(0, dest_client, 0)

    for channel in range(16):
        alsaseq.output(alsamidi.pgmchangeevent(channel, 0))

    alsaseq.start()

    #events = alsamidi.modifyevents( events, source = ( 20, 0 ) )
    for event in events:
        if display:
            print(event)
        alsaseq.output(event)

    alsaseq.syncoutput()
    # time.sleep( delay )

if __name__ == '__main__':
    dest_client = int(sys.argv[1])
    file_name = sys.argv[2]
    if len(sys.argv) > 3:
        display = sys.argv[3]
    else:
        display = ''
    main(dest_client, file_name, display)
