from __future__ import print_function
#! /usr/bin/python
# -*- coding: UTF-8 -*-

import alsaseq, alsamidi, sys

def main(dest_cliente, ruta, display=False):
    seq = alsamidi.Seq()
    seq.read( ruta )
    eventos = alsamidi.merge( seq.tracks )
    seq.info()

    print(len( eventos ), 'eventos')
    alsaseq.client( 'Reproductor', 0, 1, 1 )
    alsaseq.connectto( 0, dest_cliente, 0 )

    for channel in range( 16 ):
        alsaseq.output( alsamidi.pgmchangeevent( channel, 0 ) )

    alsaseq.start()

    #eventos = alsamidi.modifyevents( eventos, source = ( 20, 0 ) )
    for evento in eventos:
        if display: print(evento)
        alsaseq.output( evento )

    alsaseq.syncoutput()
    # time.sleep( delay )

if __name__ == '__main__':
    dest_cliente = int( sys.argv[1] )
    ruta = sys.argv[2]
    if len(sys.argv) > 3:
        display = sys.argv[3]
    else:
        display = ''
    main(dest_cliente, ruta, display)
