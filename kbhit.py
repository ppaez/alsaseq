"""
	kbhit.py - kbhit functionality for Unix (with termios)

	How to use this module:

	unbuffer_stdin()
	Call unbuffer_stdin() before using any other functions.

	kbhit()
	Once stdin is in unbuffered mode, you can call kbhit() to
	see if a key is ready on stdin.  kbhit() will return immediately.
	Returns 1 if a key is ready, 0 otherwise.

	getchar()
	Calling getchar() will return one keypress from stdin.  If a
	key is not ready, then getchar() will block until the next keypress.
	Recommended usage is to call kbhit() until a key is ready,
	then getchar() to get the keypress.

	restore_stdin()
	When you are all done, call restore_stdin() to return stdin
	to its prior state.

	This module was tested with Linux.
	This module is NOT thread-safe.

	Author: Tim Bird, (termios handling from Andrew Kuchling)
"""

import sys
import os
import termios
#import TERMIOS
import select

# prepare stdin for kbhit usage
def unbuffer_stdin():
	"""unbuffer_stdin() - used to convert stdin to
	unbuffered mode.  That is, you can read a single character
	from stdin, without having to wait for a whole line of input
	"""
	global old_termios

	fd = sys.stdin.fileno()
	old_termios = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	# turn off canonical mode and echo
	new[3]=new[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, new)

# stop using stdin for kbhit
def restore_stdin():
	"""restore_stdin() - used to convert stdin to
	whatever mode it was in before calling unbuffer_stdin()
	"""
	global old_termios
	termios.tcsetattr(sys.stdin.fileno(),
		termios.TCSAFLUSH, old_termios)

# returns 0 if no key ready, or 1 if a key is ready
def kbhit():
	"""kbhit() - returns 1 if a key is ready, 0 othewise.
	kbhit always returns immediately.
	"""
	(read_ready, write_ready, except_ready) = \
		select.select( [sys.stdin], [], [], 0.0)
	if read_ready:
		return 1
	else:
		return 0

# get the last key hit
def getch():
	"""getchar() - reads one key from stdin.  Waits if there
	is not a key available.
	"""
	return os.read(sys.stdin.fileno(), 1)

def test():
	unbuffer_stdin()
	count = 0
	print("A trail of '*'s will be written while I poll for keystrokes")
	print("Press 'q' to quit")
	while 1:
		ready = kbhit()
		if ready:
			count = 0
			key = getchar()
			os.write(sys.stdout.fileno(), key)
			if key=='q':
				print()
				break
		else:
			count = count + 1
			if count==1000:
				os.write(sys.stdout.fileno(), '*'.encode())
				count = 0

	restore_stdin()

if __name__=='__main__':
	test()
