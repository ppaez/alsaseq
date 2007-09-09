
#    alsamidi.py - Helper functions for alsaseq module
#
#   Copyright (c) 2007 Patricio Paez <pp@pp.com.mx>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>

'''Helper functions to create ALSA events

Helper functions for the alsaseq module.

They provide frequent MIDI event funtions that return an ALSA event ready
to be sent with the alsaseq.output() function.

noteevent() returns an ALSA event that is always queued by alsaseq.output().

noteonevent() and noteoffevent() return ALSA events to be processed directly
without queueing by alsaseq.output().

pgmchangeevent(), pitchbendevent() and chanpress() have the optional start
parameter.  If it is omitted the returned ALSA event will be processed directly
without queueing by alsaseq.output().  If it is used, the returned ALSA event
will be queued by alsaseq.output().

All events contain queue value of 0.  This is normally overwritten by 
alsaseq.output() for scheduled events.

All start and duration times are in milliseconds.
'''

__version__ = '4'

'Parameter start in pitchbendevent() and chanpress() is now optional.'
'It triggers scheduled vs direct output.'

import alsaseq

queue = 0

def noteevent( ch, key, vel, start, duration ):
    'Returns an ALSA event tuple to be scheduled by alsaseq.output().'
    
    return ( alsaseq.SND_SEQ_EVENT_NOTE, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, queue, ( start/1000, start%1000 * 1000000),
        ( 0, 0 ), ( 0,0 ), ( ch, key, vel, 0, duration ) )

def noteonevent( ch, key, vel ):
    'Returns an ALSA event tuple to be sent directly with alsaseq.output().'

    return ( alsaseq.SND_SEQ_EVENT_NOTEON, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, 253, ( 0, 0),
        ( 0, 0 ), ( 0,0 ), ( ch, key, vel, 0, 0 ) )

def noteoffevent( ch, key, vel ):
    'Returns an ALSA event tuple to be sent directly with alsaseq.output().'

    return ( alsaseq.SND_SEQ_EVENT_NOTEOFF, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, 253, ( 0, 0),
        ( 0, 0 ), ( 0,0 ), ( ch, key, vel, 0, 0 ) )

def pgmchangeevent( ch, value, start=-1 ):
    '''Return an ALSA event tuple to be sent by alsaseq.output().
    
    If start is not used, the event will be sent directly.
    If start is provided, the event will be scheduled in a queue.'''

    if start < 0:
        return ( alsaseq.SND_SEQ_EVENT_PGMCHANGE, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, 253, ( 0, 0),
        ( 0, 0 ), ( 0,0 ), ( ch, 0, value ) )
    else:
        return ( alsaseq.SND_SEQ_EVENT_PGMCHANGE, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, queue, ( start/1000, start%1000 * 1000000),
        ( 0, 0 ), ( 0,0 ), ( ch, 0, value ) )

def pitchbendevent( ch, value, start = -1 ):
    '''Return an ALSA event tuple to be sent by alsaseq.output().
    
    If start is not used, the event will be sent directly.
    If start is provided, the event will be scheduled in a queue.'''

    if start < 0:
        return ( alsaseq.SND_SEQ_EVENT_PITCHBEND, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, 253, ( start/1000, start%1000 * 1000000),
        ( 0, 0 ), ( 0,0 ), ( ch, 0, value ) )
    else:
        return ( alsaseq.SND_SEQ_EVENT_PITCHBEND, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, queue, ( start/1000, start%1000 * 1000000),
        ( 0, 0 ), ( 0,0 ), ( ch, 0, value ) )

def chanpress( ch, value, start = -1 ):
    '''Return an ALSA event tuple to be sent by alsaseq.output().
    
    If start is not used, the event will be sent directly.
    If start is provided, the event will be scheduled in a queue.'''

    if start < 0:
        return ( alsaseq.SND_SEQ_EVENT_CHANPRESS, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, 253, ( start/1000, start%1000 * 1000000),
        ( 0, 0 ), ( 0,0 ), ( ch, 0, value ) )
    else:
        return ( alsaseq.SND_SEQ_EVENT_CHANPRESS, alsaseq.SND_SEQ_TIME_STAMP_REAL,
        0, queue, ( start/1000, start%1000 * 1000000),
        ( 0, 0 ), ( 0,0 ), ( ch, 0, value ) )

