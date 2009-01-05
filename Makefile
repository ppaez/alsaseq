#
# Alsaseq
#

VERSION = 0.3
PYVER = $(shell python -V 2>&1 | cut -d\  -f2 | cut -d. -f1-2)
RST2HTML = rst2html

all: doc/project.html alsaseq.so

alsaseq.so: alsaseq.c constants.c
	gcc -shared -I /usr/include/python$(PYVER) -lasound -o alsaseq.so \
	    alsaseq.c

doc/project.html: doc/project.rst
	$(RST2HTML) $< $@

test:
	@if python -c 'import alsaseq, alsamidi'; \
	then echo Test passed; \
	else echo Test failed; \
	fi

install: all
	install alsaseq.so alsamidi.py midiinstruments.py \
	    /usr/local/lib/python$(PYVER)/site-packages

uninstall:
	@rm -v /usr/local/lib/python$(PYVER)/site-packages/alsaseq.so
	@rm -v /usr/local/lib/python$(PYVER)/site-packages/alsamidi.py
	@rm -v /usr/local/lib/python$(PYVER)/site-packages/midiinstruments.py

clean:
	@rm -vri *.so doc/*.html

dist: CHANGELOG COPYING CREDITS README alsaseq.c constants.c alsamidi.py \
      midiinstruments.py doc/project.html Makefile
	mkdir -p alsaseq-$(VERSION)/doc
	cp -avf CHANGELOG COPYING CREDITS README alsaseq.c constants.c \
	    alsamidi.py midiinstruments.py doc Makefile \
	    alsaseq-$(VERSION)
	tar -czf alsaseq-$(VERSION).tar.gz alsaseq-$(VERSION)

