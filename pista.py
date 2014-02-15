#! /usr/bin/python
# -*- coding: UTF-8 -*-

import alsamidi, re, sys

def CanalPgmyNota( timbre ):
    'Convierte nombre a canal, pgmchange y nota .'
    timbre = timbre.replace( ' ', '' )
    if timbres.has_key( timbre ):
        return timbres[ timbre ]
    else:
        return 9, 0, int( timbre )

def velocidad( cadena ):
    'Convierte cadena a entero.'
    return int( cadena )


timbres = { 'TaikoDrum': ( 1, 116, 60 ),
            'MetronomeTick': ( 9, 0, 33 ),
            'MetronomeBell': ( 9, 0, 34 ),
            'BassDrum1': ( 9, 0, 36 ),
            'AcousticSnare': ( 9, 0, 38 ),
            'ClosedHiHat': ( 9, 0, 42 ),
            'OpenHiHat': ( 9, 0, 46 ),
            'HiBongo': ( 9, 0, 60 ),
            'LowBongo': ( 9, 0, 61 ),
            'OpenHiConga': ( 9, 0, 63 ) ,
            'Claves': ( 9, 0, 75 ),
            'LowConga': ( 9, 0, 64 ) }


def lee( archivo ):
    'Lee uno o más ritmos de archivo.'
    ritmos = []

    lines = open( archivo ).read().split( '\n' )
    for line in lines:
        line = line.rstrip()
        if '|' in line:
            izq, der = line.split( '|' )
            if not parametros:
                pulsos = 4
                numbeats = len( izq )
                parametros.extend( [ pulsos, numbeats] )
            der = der.strip()
            if der:
                timbre, vel = re.split( '   *', der )
                ch, pgm, timbre = CanalPgmyNota( timbre )
                vel = velocidad( vel )
                instrumentos.append( ( ch, pgm, timbre, vel, izq ) )
        elif line:  # rhythm name, start new rhythm
            parametros = []
            instrumentos = []
            ritmo = [ line, parametros, instrumentos ]
            ritmos.append( ritmo )
    return ritmos

def construye( ritmo, tempo, compases, start=0 ):
    'Construye lista de eventos a partir de ritmo.'

    def itotiempo( i ):
        'Regresa tiempo dentro del compas.'
        return i * tbeat * numerador / numbeats + start
    
    tbeat = int( 60. / tempo * 1000 )
    numerador = ritmo[ 1 ][ 0 ]
    numbeats = ritmo[ 1 ][ 1]
    inicios = map( itotiempo, range( numbeats * compases ) )
    duracion = int( tbeat * 0.9 )
    instrumentos = ritmo[ 2 ]
    
    eventos = []
    for ch, pgm, timbre, vel, notas in instrumentos:
        if pgm:
            eventos.append( alsamidi.pgmchangeevent( ch, pgm, start=0 ) )
        for ibeat, nota in enumerate( notas * compases ):
            if nota != ' ':
                eventos.append( alsamidi.noteevent( ch, timbre, vel, 
                        inicios[ ibeat ], duracion ) )
    return eventos

def duracion( ritmo, tempo, compases, start=0 ):
    'Regresa tiempo final de compases de ritmo a tempo.'
    
    tbeat = int( 60. / tempo * 1000 )
    numerador = ritmo[ 1 ][ 0 ]
    return start + compases * tbeat * numerador

def main():

    cliente_destino = int( sys.argv[1] )
    archivo = sys.argv[2]
    trios = []
    for e in sys.argv[3:]:
        n, tempo, compases = map( int, e.split() )
        trios.append( ( n, tempo, compases ) )

    import alsaseq
    alsaseq.client( 'Reproductor', 0, 1, True )
    alsaseq.connectto( 0, cliente_destino, 0 )
    alsamidi.queue = 1

    def play( eventos ):
        'Envia lista de eventos a la cola del secuenciador.'
        alsaseq.start()
        for evento in eventos:
            alsaseq.output( evento )
        alsaseq.syncoutput()

    ritmos = lee( archivo )
    print len(ritmos), 'ritmos:', map( lambda x: x[0], ritmos )

    eventos = []
    end = 0
    for trio in trios:
        n, tempo, compases = trio
        ritmo = ritmos [ n ]
        eventos.extend( construye( ritmo, tempo, compases, end ) )
        print str( end ).rjust( 5 ), str( compases ).rjust( 3 ), ritmo[ 0 ]
        end = end + compases * int( 60. / tempo * 1000 ) * ritmo[1][0]

    play( eventos )

if __name__ == '__main__':
    main()
