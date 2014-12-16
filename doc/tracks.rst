tracks
======

tracks is a simple sequencer that uses alsaseq.  It can record
and playback one or more tracks. The input note range is split
in two channels by default. The split note can be changed, as
well as the voice on each channel.  The use can pause the
sequencer, save the events to a file and some other basic
actions.

Uses the threading module to create two threads that handle ALSA
sequencer events: One fetches events received by the sequencer,
the other sends events to the sequencer.

The receiving thread uses select.poll() to check if there are
input events.

kbhit by Tim Bird is used to get commands from the user, in the
form of single characters.

The drums() function generates events for the next measure of
a loop.  It uses an ALSA echo event to trigger itself shortly
before the next measure needs to be schedule again.

The command-line parameters are::

  python tracks.py source destination voice1 voice2 split path

The meaning of each parameter:
    - source ALSA client number,
      events are received from this devic.
    - destination ALSA client numbre,
      events are sent to this device.
    - voice 1 General MIDI instrument number
    - voice 2 General MIDI instrument number
    - split note number
    - path to a sequence file

An example command line::

  python tracks.py 128 129 1 50 59 file.seq


When the program starts, it is in playback mode and will
reproduce the events in the input file.  The following
commands are available in playback mode:

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
