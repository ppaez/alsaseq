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
