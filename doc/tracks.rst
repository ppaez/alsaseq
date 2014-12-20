======
tracks
======

tracks is a simple command-line MIDI sequencer for GNU/Linux
that uses the modules
from the `alsaseq`__ project.  It can record
and playback one or more tracks. The input note range is split
in two channels by default. The split note can be changed, as
well as the voice on each channel.  The user can pause the
sequencer, save the events to a file and some other basic
actions.

__ https://github.com/ppaez/alsaseq

Running
=======
The command-line parameters are::

  python tracks.py source destination voice1 voice2 split path

The meaning of each parameter is:

    - source ALSA client number,
      events are received from this device.
    - destination ALSA client number,
      events are sent to this device.
    - voice 1 General MIDI instrument number
    - voice 2 General MIDI instrument number
    - split note number
    - path to a sequence file

An example command line::

  python tracks.py 128 129 1 50 59 file.seq

Events are received from client 128, events are sent to
client 129, the first voice is piano on channel 0, the
second voice is string ensemble on channel 1, the
split note is B3, and file.seq is the sequence file.

Operation
=========

When the program starts, it is in playback mode and will
reproduce the events in the input file.  Incoming events
are recorded and sent to the destination ALSA client
using MIDI channel 0.
Incoming notes equal to or below the split note, are
recorded and sent to the destination ALSA client
using MIDI channel 1.

The following commands are available in playback mode:

- `p` stop
- `r` read pattern file `main.pat`
- `0` `1` ... `9` select pattern
- `n` enter pattern number
- `t` enter tempo

The following commands are available when in stop mode:

- `p` playback
- `o` read sequence file
- `s` save sequence file
- `t` enable/disable tracks (not implemented)
- `k` enter keyboard split note
- `v` enter voice 1
- `b` enter voice 2

`q` ends the program.

Rhythm Loops
============

A basic mechanism to play percussion sounds in a loop with is
available.  It is based on a text file `main.path` that stores
sequences.  Each sequence has a name and a track for each
instrument.  A track is stored in a row in the file; the row
includes the time subdivisions per measure, showing on which
subdivisions an instrument is played, the instrument name, and
the velocity.

The first sequence in the file is chosen as default, but it can
be changed during playback by pressing a number key or entering
the number with the `n` command.  The change takes effect on the
next measure.

The tempo for the loop is set to 80 by default, it can be
changed by entering a new value with the `t` command.  Then
change takes effect on the next measure.


Implementation
==============

tracks uses the `alsamidi`__ module to read the sequence file, using an
instance of the Seq class.  The `tracks` attribute of the instance is a list
of tracks, each track is a sequence of ALSA sequencer events.  The `tracks`
list is loaded with the events that are read from the sequence file at
the start of the program, or when the `o` command is used.

tracks keeps two lists of ALSA sequencer events:

    - `incoming`, the events received from the source client.
      It is cleared when playback mode is entered.  When stop mode
      is entered, one or two voice change events are added at the
      beginning, and its contents are appended to the `tracks` list.

    - `eventos`, the events that will be sent to the destination
      client.  It is set to the contents of all the tracks in the `tracks`
      list when playback mode is entered.  The `tracks` list is first
      processed by `merge` to become a single event list.

tracks uses the `threading`__ module to populate the `incoming`
and `eventos` lists with ALSA sequencer events.  It creates two
threads:

    - `thri`, runs `retrieveinput`

        - fetches events received by the sequencer and adds
          them to the `incoming` list

    - `thso`, runs `supplyoutput`

        - sinks events from the `eventos` list and schedules
          them to the sequencer

The receiving thread uses poll() in the `select`__ module to check if there are
input events.

Both threads are started at the beginning of the program execution.  They are
ended after the `q` command is used, when the main program will end, by
setting the `vivo` variable to 0.


The `kbhit`__ module by Tim Bird is used to get commands from the user, in the
form of single characters.

The drums() function generates events for the next measure of
a loop.  It uses an `ALSA echo event`__ to trigger itself shortly
before the next measure needs to be scheduled again.  It uses
the `pista`__ module.

__ https://github.com/ppaez/alsaseq/blob/master/alsamidi.py
__ https://docs.python.org/3/library/threading.html
__ https://docs.python.org/3/library/select.html
__ https://groups.google.com/forum/#!topic/comp.lang.python/rGIpVDmIpOU
__ http://alsa-project.org/alsa-doc/alsa-lib/group___seq_events.html#ggaef39e1f267006faf7abc91c3cb32ea40a71cd073dbeb98982d8b094ab6d841376
__ https://github.com/ppaez/alsaseq/blob/master/pista.py
