# -*- coding: UTF-8 -*-

from __future__ import print_function
import sys
import time
import traceback
import threading
import select

import alsaseq
import alsamidi
import pista


waitingforsplit = 0; split = 0
source_cliente = int( sys.argv[1] )
dest_cliente = int( sys.argv[2] )
voz1 = int( sys.argv[3] )
voz2 = int( sys.argv[4] )
split = int( sys.argv[5] )
ruta = sys.argv[6]

outgoing = []
incoming = []
ritmos = []
nritmo = 0; tempo = 80; compases = 1
playing = False
letra = ''


def merge( lists ):
    'Join each list in list in to one list.'
    listagral = []
    for lista in lists:
        listagral.extend( lista )
    listagral.sort(key=lambda e: e[4]) # order by timestamp
    return listagral


def supplyoutput():
    'Supply events to the sequencer.'
    global outgoing
    event_tmpl = 'events: {:3} in the ALSA sequencer queue, {:3} outgoing, {:3} may be sent, {:3} sent'
    enfila_old = 0
    while vivo:
        enfila = alsaseq.status()[2]
        if enfila < 250 and outgoing:
            nenviar = 500 - enfila - nlibres
            if len(outgoing) > nlibres:
                for evento in outgoing[ :nlibres ]:
                    alsaseq.output( evento )
                print(event_tmpl.format(enfila, len(outgoing), 500 - enfila, nlibres))
                outgoing = outgoing[ nlibres : ]
            else:
                print(event_tmpl.format(enfila, len(outgoing), 500 - enfila, len(outgoing)))
                for evento in outgoing:
                    alsaseq.output( evento )
                    outgoing = []
        elif enfila != enfila_old:
            print(event_tmpl.format(enfila, len(outgoing), 500 - enfila, 0))
        enfila_old = enfila
        time.sleep( 0.5 )
    print('Ending supplyoutput()')


def retrieveinput():
    'Retrieve received events.'
    global incoming, waitingforsplit, split
    p = select.poll()
    p.register( fd, select.POLLIN )
    while vivo:
      p.poll( 5000 )
      while alsaseq.inputpending():
        entrante = alsaseq.input()
        nota = entrante[7][1]
        type = entrante[0]
        if type in rechazados:
            continue # discard obnoxious Clavinova events
        elif type == alsaseq.SND_SEQ_EVENT_ECHO:
            drums( ritmos[ nritmo ], tempo, compases )
            continue
        ev = alsamidi.modifyevent( entrante, ch=1 )
        if waitingforsplit:
            split = nota
            waitingforsplit = 0
            print(nota)
            continue  # discard note
        if not split:
            alsaseq.output( entrante )
            alsaseq.output( ev )
            incoming.append( ev )
            incoming.append( entrante )
        elif nota > split:
            alsaseq.output( entrante )
            incoming.append( entrante )
        else:
            alsaseq.output( ev )
            incoming.append( ev )
        print(len( incoming ), 'incoming')

    print('Ending retrieveinput()')


def playback():
    'Start playing events.'
    global playing, outgoing, incoming
    playing = True
    incoming = []
    outgoing = merge(seq.tracks)
    alsaseq.start()
    print('playing')
    print(seq.info())


def stop():
    'Stop playing of events.'
    global playing, incoming
    playing = False
    alsaseq.stop()
    if incoming:
        incoming.insert( 0, pgmchangevoz1 )
        if voz2:
            incoming.insert( 0, pgmchangevoz2 )
        seq.tracks.append( incoming )
        incoming = []
    print('stopped')
    print(len(seq.tracks), 'tracks')


def drums( ritmo, tempo, compases ):
    'Output one measure to queue.'
    global incoming
    tiempoms = alsamidi.tuple2time( 
                    alsaseq.status()[1] ) * 1000
    t = pista.construye( ritmo, tempo, compases, tiempoms)
    final = alsamidi.time2tuple( pista.duracion( ritmo, tempo, compases, tiempoms )/1000. )
    t.append( (alsaseq.SND_SEQ_EVENT_ECHO, 1, 0, 0, final, (0,0), (alsaseq.id(),0), (1,2,3,4,5) ) )
    
    for evento in t:
        alsaseq.output( evento )
        incoming.append( evento ) # record it


def parsecommand():
    'Read on letter from stdin.'
    global ritmos, nritmo, tempo, split, waitingforsplit
    global voz1, voz2, pgmchangevoz1, pgmchangevoz2
    if not playing:
        if letra == 'p':
            playback()
        elif letra == 'o':
            seq.read( ruta )
            print('read', ruta)
        elif letra == 's':
            seq.write( ruta )
            print('saved', ruta)
        elif letra == 't':
            enabledisabletracks()
        elif letra == 'k':
            print('hit keyboard split point:', end=' ')
            waitingforsplit = 1
        elif letra == 'v':
            voz1 = int(input())
            pgmchangevoz1 = alsamidi.pgmchangeevent( 0, voz1 )
            alsaseq.output( pgmchangevoz1 )
            print('voice 1:', voz1)
        elif letra == 'b':
            voz2 = int(input())
            pgmchangevoz2 = alsamidi.pgmchangeevent( 1, voz2 )
            if voz2:
                alsaseq.output( pgmchangevoz2 )
            print('voice 2:', voz2)
    else:
        if letra == 'p':
            stop()
        elif letra == 'r':
            ritmos = pista.lee( 'main.pat' )
            for i, x in enumerate(ritmos):
                print('{:2} {}'.format(i, x[0]))
            drums( ritmos[ nritmo ], tempo, compases )
        elif letra in '0123456789':
            nritmo = int( letra )
            print('{:2} {}'.format(nritmo, ritmos[nritmo][0]))
        elif letra == 'n':
            number = int( input() )
            if number < len( ritmos ):
                nritmo = number
                print('{:2} {}'.format(nritmo, ritmos[nritmo][0]))
        elif letra == 't':
            tempo = int( input() )
            print('tempo:', tempo)

rechazados = ( alsaseq.SND_SEQ_EVENT_CLOCK, alsaseq.SND_SEQ_EVENT_SENSING )
alsaseq.client( 'ReproductorGrabador', 1, 1, 1 )
alsaseq.connectfrom( 0, source_cliente, 0 )
alsaseq.connectto( 1, dest_cliente, 0 )
alsaseq.start()
pgmchangevoz1 = alsamidi.pgmchangeevent( 0, voz1 )
pgmchangevoz2 = alsamidi.pgmchangeevent( 1, voz2 )
alsaseq.output( pgmchangevoz1 )
if voz2:
    alsaseq.output( pgmchangevoz2 )

nlibres = 100
import kbhit
kbhit.unbuffer_stdin()
vivo = 1 
seq = alsamidi.Seq()
try:
    fd = alsaseq.fd()
    thso = threading.Thread( target=supplyoutput )
    thso.start()
    thri = threading.Thread( target=retrieveinput )
    thri.start()

    seq.read( ruta )
    playback()

    while letra != 'q':
        letra = kbhit.getch().decode()
        parsecommand()

except:
    traceback.print_exception(*sys.exc_info())
    kbhit.restore_stdin()
    vivo = 0

kbhit.restore_stdin()
print('End')
vivo = 0
