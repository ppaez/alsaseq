from __future__ import print_function
# -*- coding: UTF-8 -*-

__version__ = '2'

'Do not fill queue.'

import alsaseq, sys, time, threading, alsamidi, select, pista

waitingforsplit = 0; split = 0
source_cliente = int( sys.argv[1] )
dest_cliente = int( sys.argv[2] )
voz1 = int( sys.argv[3] )
voz2 = int( sys.argv[4] )
split = int( sys.argv[5] )
ruta = sys.argv[6]

eventos = []
incoming = []
tracks = []
ritmos = []
nritmo = 0; tempo = 80; compases = 1
playing = False
letra = ''

def bytimestamp( a, b ):
    return cmp( a[4], b[4] )

def merge( lists ):
    'Join each list in list in to one list.'
    listagral = []
    for lista in lists:
        listagral.extend( lista )
    listagral.sort( bytimestamp ) # order by timestamp
    return listagral


def supplyoutput():
  'Supply events to the sequencer.'
  global eventos
  while vivo:
    enfila = alsaseq.status()[2]
    if enfila < 250 and eventos:
        print(enfila, 'eventos en fila')
        print(len( eventos ), 'eventos tenemos.')
        print(500 - enfila, 'eventos pueden enviarse')
        nenviar = 500 - enfila - nlibres
        print(nlibres, 'eventos se envían')
        if len( eventos ) > nlibres:
            print(nlibres, 'eventos se envían.')
            for evento in eventos[ :nlibres ]:
                alsaseq.output( evento )
            eventos = eventos[ nlibres : ]
        else:
            print(len( eventos ), 'eventos restantes se envían.')
            for evento in eventos:
                alsaseq.output( evento )
                eventos = []
    time.sleep( 0.5 ) 
  print('Terminando supplyoutput()')

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
            print('echo event')
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
        print(len( incoming ), 'entrantes')

    print('Terminando retrieveinput()')


def playback():
    'Start playing events.'
    global playing, eventos, incoming
    playing = True
    incoming = []
    eventos = merge( tracks )
    #eventos = alsamidi.modifyevents( eventos, source=(20,1) )
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
        tracks.append( incoming )
        incoming = []
    print('stopped')
    print(len(tracks), 'tracks')

def drums( ritmo, tempo, compases ):
    'Output one measure to queue.'
    global incoming
    tiempoms = alsamidi.tuple2time( 
                    alsaseq.status()[1] ) * 1000
    t = pista.construye( ritmo, tempo, compases, tiempoms)
    final = alsamidi.time2tuple( pista.duracion( ritmo, tempo, compases, tiempoms )/1000. )
    print(final)
    t.append( (alsaseq.SND_SEQ_EVENT_ECHO, 1, 0, 0, final, (0,0), (alsaseq.id(),0), (1,2,3,4,5) ) )
    #t = alsamidi.modifyevents( t, source = (20, 1) )
    
    for evento in t:
        alsaseq.output( evento )
        incoming.append( evento ) # record it

def parsecommand():
    'Read on letter from stdin.'
    global tracks, ritmos, nritmo, tempo, split, waitingforsplit
    global voz1, voz2, pgmchangevoz1, pgmchangevoz2
    if not playing:
        if letra == 'p':
            playback()
        elif letra == 'o':
            seq.read( ruta )
            tracks = seq.tracks
        elif letra == 's':
            seq.write( ruta )
        elif letra == 't':
            enabledisabletracks()
        elif letra == 'k':
            print('hit keyboard split point:', end=' ')
            waitingforsplit = 1
        elif letra == 'v':
            number = int( input() )
            voz1 = number
            pgmchangevoz1 = alsamidi.pgmchangeevent( 0, voz1 )
            alsaseq.output( pgmchangevoz1 )
        elif letra == 'b':
            number = int( input() )
            voz2 = number
            pgmchangevoz2 = alsamidi.pgmchangeevent( 1, voz2 )
            if voz2:
                alsaseq.output( pgmchangevoz2 )
    else:
        if letra == 'p':
            stop()
        elif letra == 'r':
            ritmos = pista.lee( 'main.pat' )
            print([x[0] for x in ritmos])
            drums( ritmos[ nritmo ], tempo, compases )
        elif letra in '0123456789':
            nritmo = int( letra )
            print(ritmos[ nritmo ][0])
        elif letra == 'n':
            number = int( input() )
            if number < len( ritmos ):
                nritmo = number
                print(ritmos[ nritmo ][0])
        elif letra == 't':
            number = int( input() )
            tempo = number

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
    tracks = seq.tracks
    playback()

    while letra != 'q':
        letra = kbhit.getch()
        parsecommand()

except:
    print('except', sys.exc_info())
    kbhit.restore_stdin()
    vivo = 0

kbhit.restore_stdin()
print('fin.')
vivo = 0
#thri.join() # wait for thread to finish
