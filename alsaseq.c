/*
    alsaseq.c - ALSA sequencer bindings for Python

    Copyright (c) 2007 Patricio Paez <pp@pp.com.mx>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
*/

#include "Python.h"
#include <alsa/asoundlib.h>

#define maximum_nports 4

static PyObject *ErrorObject;

/* ----------------------------------------------------- */

static char alsaseq_client__doc__[] =
"client( name, ninputports, noutputports, createqueue ) --> None.\n\nCreate an ALSA sequencer client with zero or more input or output ports, and optionally a timing queue.\n\nninputports and noutputports are created if quantity requested is between 1 and 4 for each.\ncreatequeue = True creates a queue for stamping arrival time of incoming events and scheduling future start time of outgoing events.\ncreatequeue = None will create a client that receives events without stamping arrival time and sends outgoing events for imediate execution."
;

snd_seq_t *seq_handle;
int queue_id, ninputports, noutputports, createqueue;

static PyObject *
alsaseq_client(PyObject *self /* Not used */, PyObject *args)
{
  const char * client_name;

  if (!PyArg_ParseTuple(args, "siii", &client_name, &ninputports, &noutputports, &createqueue ) )
		return NULL;

  if ( ninputports > maximum_nports || noutputports > maximum_nports ) {
    printf( "Only %d ports of each are allowed.\n", maximum_nports );
    exit( 1 );
    }

  int portid, n;

  if (snd_seq_open(&seq_handle, "default", SND_SEQ_OPEN_DUPLEX, 0) < 0) {
    fprintf(stderr, "Error creating ALSA client.\n");
    exit(1);
  }
  snd_seq_set_client_name(seq_handle, client_name );

  if ( createqueue )
      queue_id = snd_seq_alloc_queue(seq_handle);
  else
      queue_id = SND_SEQ_QUEUE_DIRECT;

  for ( n=0; n < ninputports; n++ ) {
    if (( portid = snd_seq_create_simple_port(seq_handle, "Input port",
            SND_SEQ_PORT_CAP_WRITE|SND_SEQ_PORT_CAP_SUBS_WRITE,
            SND_SEQ_PORT_TYPE_APPLICATION)) < 0) {
    fprintf(stderr, "Error creating input port %d.\n", n );
    exit(1);
    }
    if( createqueue ) {
      /* set timestamp info of port  */
      snd_seq_port_info_t *pinfo;
      snd_seq_port_info_alloca(&pinfo);
      snd_seq_get_port_info( seq_handle, portid, pinfo );
      snd_seq_port_info_set_timestamping(pinfo, 1);
      snd_seq_port_info_set_timestamp_queue(pinfo, queue_id );
      snd_seq_port_info_set_timestamp_real( pinfo, 1 );
      snd_seq_set_port_info( seq_handle, portid, pinfo );
    }
  }

  for ( n=0; n < noutputports; n++ ) {
    if (( portid = snd_seq_create_simple_port(seq_handle, "Output port",
            SND_SEQ_PORT_CAP_READ|SND_SEQ_PORT_CAP_SUBS_READ,
            SND_SEQ_PORT_TYPE_APPLICATION)) < 0) {
      fprintf(stderr, "Error creating output port %d.\n", n );
      exit(1);
    }
  }

    Py_INCREF(Py_None);
    return Py_None;
}

static char alsaseq_start__doc__[] =
"Start the queue.\n\nIt is ignored if the client does not have a queue."
;

static PyObject *
alsaseq_start(PyObject *self /* Not used */, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;

        snd_seq_start_queue(seq_handle, queue_id, NULL);
        snd_seq_drain_output(seq_handle);

	Py_INCREF(Py_None);
	return Py_None;
}

static char alsaseq_stop__doc__[] =
"Stop the queue.\n\nIt is ignored if the client does not have a queue."
;

static PyObject *
alsaseq_stop(PyObject *self /* Not used */, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;

        snd_seq_stop_queue(seq_handle, queue_id, NULL);
        snd_seq_drain_output(seq_handle);

	Py_INCREF(Py_None);
	return Py_None;
}

static char alsaseq_status__doc__[] =
"Return ( status, time, events ) of queue.\n\nTime is a tuple ( sec, millionths ) and reflects the queue's current time.\n\nIf the client does not have a queue the value ( 0, ( 0, 0 ), 0 ) is returned."
;

static PyObject *
alsaseq_status(PyObject *self /* Not used */, PyObject *args)
{
        snd_seq_queue_status_t *queue_status;
        int running, events;
        const snd_seq_real_time_t *current_time;
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;

        snd_seq_queue_status_malloc( &queue_status );
        snd_seq_get_queue_status( seq_handle, queue_id, queue_status );
        current_time = snd_seq_queue_status_get_real_time( queue_status );
        running = snd_seq_queue_status_get_status( queue_status );
        events = snd_seq_queue_status_get_events( queue_status );
        snd_seq_queue_status_free( queue_status );
        
	return Py_BuildValue( "(i(ii),i)", running, current_time->tv_sec, current_time->tv_nsec, events );
}


static char alsaseq_output__doc__[] =
"output( event ) --> None.\n\n"
"Send event immediately to output port if a queue\n"
"has not been created in this client.  If a queue already exists,\n"
"use that queue to schedule the event.";

static PyObject *
alsaseq_output(PyObject *self, PyObject *args)
{
  int port_out_id = 0, relative = 0;
  struct snd_seq_real_time timestamp;
  snd_seq_event_t ev;
  static PyObject * data;
        
	if (!PyArg_ParseTuple(args, "(bbbb(ii)(bb)(bb)O)", &ev.type, &ev.flags, &ev.tag, &ev.queue, &ev.time.time.tv_sec, &ev.time.time.tv_nsec, &ev.source.client, &ev.source.port, &ev.dest.client, &ev.dest.port, &data ))
		return NULL;
        /* printf ( "event.type: %d\n", ev.type ); */
        switch( ev.type ) {
        case SND_SEQ_EVENT_NOTE:
        case SND_SEQ_EVENT_NOTEON:
        case SND_SEQ_EVENT_NOTEOFF:
        case SND_SEQ_EVENT_KEYPRESS:
            if (!PyArg_ParseTuple( data, "bbbbi;data parameter should have 5 values", &ev.data.note.channel, &ev.data.note.note, &ev.data.note.velocity, &ev.data.note.off_velocity, &ev.data.note.duration))
            return NULL;
            break;

        case SND_SEQ_EVENT_CONTROLLER:
        case SND_SEQ_EVENT_PGMCHANGE:
        case SND_SEQ_EVENT_CHANPRESS:
        case SND_SEQ_EVENT_PITCHBEND:
            if (!PyArg_ParseTuple( data, "bbbbii;data parameter should have 6 values", &ev.data.control.channel, &ev.data.control.unused[0], &ev.data.control.unused[1], &ev.data.control.unused[2], &ev.data.control.param, &ev.data.control.value ))
            return NULL;
            break;
        }
        /* If not a direct event, use the queue */
        if ( ev.queue != SND_SEQ_QUEUE_DIRECT )
            ev.queue = queue_id;
        if ( ev.type != SND_SEQ_EVENT_ECHO ) snd_seq_ev_set_subs(&ev); /* Set to subscribed ports */
        snd_seq_event_output_direct( seq_handle, &ev );

	Py_INCREF(Py_None);
	return Py_None;
}


static char alsaseq_id__doc__[] =
"id() --> number.\n\nReturn the client number.  0 if client not created yet."
;

static PyObject *
alsaseq_id(PyObject *self, PyObject *args)
{
  int res = 0;
        
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;
        res = snd_seq_client_id( seq_handle );

        return PyInt_FromLong( res );
}


static char alsaseq_syncoutput__doc__[] =
"syncoutput() --> None.\n\nWait until output events are processed."
;

static PyObject *
alsaseq_syncoutput(PyObject *self, PyObject *args)
{
        snd_seq_sync_output_queue( seq_handle );

	Py_INCREF(Py_None);
	return Py_None;
}



static char alsaseq_connectto__doc__[] =
"connectto( myport, dest_client, dest_port ) --> None.\n\nConnect from myport to dest_client:dest_port."
;

static PyObject *
alsaseq_connectto(PyObject *self, PyObject *args)
{
  int myport, dest_client, dest_port;
        
	if (!PyArg_ParseTuple(args, "iii", &myport, &dest_client, &dest_port ))
		return NULL;
        snd_seq_connect_to( seq_handle, myport, dest_client, dest_port);

	Py_INCREF(Py_None);
	return Py_None;
}


static char alsaseq_connectfrom__doc__[] =
"connectfrom( myport, src_client, src_port ) --> None.\n\nConnect from src_client:src_port to myport."
;

static PyObject *
alsaseq_connectfrom(PyObject *self, PyObject *args)
{
  int myport, dest_client, dest_port;
        
	if (!PyArg_ParseTuple(args, "iii", &myport, &dest_client, &dest_port ))
		return NULL;
        snd_seq_connect_from( seq_handle, myport, dest_client, dest_port);

	Py_INCREF(Py_None);
	return Py_None;
}


static char alsaseq_input__doc__[] =
"input() --> event.\n\nWait for an ALSA event in the input port and return it.\n\nALSA events are returned as a tuple with 8 elements:\n    (type, flags, tag, queue, time stamp, source, destination, data)\n\nSome elements are also tuples:\n    time = (seconds, millionths)\n    source, destination = (client, port)\n    data = ( varies depending on type )";

static PyObject *
alsaseq_input(PyObject *self, PyObject *args)
{
  snd_seq_event_t *ev;
        
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;
        snd_seq_event_input( seq_handle, &ev );

        switch( ev->type ) {
        case SND_SEQ_EVENT_NOTE:
        case SND_SEQ_EVENT_NOTEON:
        case SND_SEQ_EVENT_NOTEOFF:
        case SND_SEQ_EVENT_KEYPRESS:
            return Py_BuildValue( "(bbbb(ii)(bb)(bb)(bbbbi))", ev->type, ev->flags, ev->tag, ev->queue, ev->time.time.tv_sec, ev->time.time.tv_nsec, ev->source.client, ev->source.port, ev->dest.client, ev->dest.port, ev->data.note.channel, ev->data.note.note, ev->data.note.velocity, ev->data.note.off_velocity, ev->data.note.duration );
            break;

        case SND_SEQ_EVENT_CONTROLLER:
        case SND_SEQ_EVENT_PGMCHANGE:
        case SND_SEQ_EVENT_CHANPRESS:
        case SND_SEQ_EVENT_PITCHBEND:
            return Py_BuildValue( "(bbbb(ii)(bb)(bb)(bbbbii))", ev->type, ev->flags, ev->tag, ev->queue, ev->time.time.tv_sec, ev->time.time.tv_nsec, ev->source.client, ev->source.port, ev->dest.client, ev->dest.port, ev->data.control.channel, ev->data.control.unused[0], ev->data.control.unused[1], ev->data.control.unused[2], ev->data.control.param, ev->data.control.value );
            break;

        default:
            return Py_BuildValue( "(bbbb(ii)(bb)(bb)(bbbbi))", ev->type, ev->flags, ev->tag, ev->queue, ev->time.time.tv_sec, ev->time.time.tv_nsec, ev->source.client, ev->source.port, ev->dest.client, ev->dest.port, ev->data.note.channel, ev->data.note.note, ev->data.note.velocity, ev->data.note.off_velocity, ev->data.note.duration );
        }

}


static char alsaseq_inputpending__doc__[] =
"inputpending() --> number.\n\nReturn number of bytes available in input buffer."
;

static PyObject *
alsaseq_inputpending(PyObject *self, PyObject *args)
{
  int res;
        
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;
        res = snd_seq_event_input_pending( seq_handle, 1 ); /* fetch_sequencer */

        return PyInt_FromLong( res );
}

static char alsaseq_fd__doc__[] =
"fd() --> number.\n\nReturn fileno of sequencer."
;

static PyObject *
alsaseq_fd(PyObject *self, PyObject *args)
{
  int npfd;
  struct pollfd *pfd;
        
	if (!PyArg_ParseTuple(args, "" ))
		return NULL;
  npfd = snd_seq_poll_descriptors_count(seq_handle, POLLIN);
  pfd = (struct pollfd *)alloca(npfd * sizeof(struct pollfd));
  snd_seq_poll_descriptors(seq_handle, pfd, npfd, POLLIN);

        return PyInt_FromLong( pfd->fd );
}



/* List of methods defined in the module */

static struct PyMethodDef alsaseq_methods[] = {
	{"client",	(PyCFunction)alsaseq_client,	METH_VARARGS,	alsaseq_client__doc__},
 {"start",	(PyCFunction)alsaseq_start,	METH_VARARGS,	alsaseq_start__doc__},
 {"stop",	(PyCFunction)alsaseq_stop,	METH_VARARGS,	alsaseq_stop__doc__},
 {"status",	(PyCFunction)alsaseq_status,	METH_VARARGS,	alsaseq_status__doc__},
 {"output",	(PyCFunction)alsaseq_output,	METH_VARARGS,	alsaseq_output__doc__},
 {"syncoutput",	(PyCFunction)alsaseq_syncoutput,	METH_VARARGS,	alsaseq_syncoutput__doc__},
 {"connectto",	(PyCFunction)alsaseq_connectto,	METH_VARARGS,	alsaseq_connectto__doc__},
 {"connectfrom",	(PyCFunction)alsaseq_connectfrom,	METH_VARARGS,	alsaseq_connectfrom__doc__},
 {"inputpending",	(PyCFunction)alsaseq_inputpending,	METH_VARARGS,	alsaseq_inputpending__doc__},
 {"id",	(PyCFunction)alsaseq_id,	METH_VARARGS,	alsaseq_id__doc__},
 {"input",	(PyCFunction)alsaseq_input,	METH_VARARGS,	alsaseq_input__doc__},
 {"fd",	(PyCFunction)alsaseq_fd,	METH_VARARGS,	alsaseq_fd__doc__},
 
	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initalsaseq) */

static char alsaseq_module_documentation[] = 
"This modules provides access to the ALSA sequencer.\n\nIt provides easy access to the ALSA sequencer.\n\nExample of use basic use:\n\nclient( 'Python client', 1, 1, False )\nconnectto( 0, 129, 0 )\nconnectfrom( 1, 130, 0 )\nif inputpending():\n    event = input()\n    output( event )\n\nTo timestamp incoming events and to schedule outgoing events,\nuse True for the createqueue parameter.\n"
;

void
initalsaseq()
{
	PyObject *m, *d;

	/* Create the module and add the functions */
	m = Py_InitModule4("alsaseq", alsaseq_methods,
		alsaseq_module_documentation,
		(PyObject*)NULL,PYTHON_API_VERSION);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	ErrorObject = PyString_FromString("alsaseq.error");
	PyDict_SetItemString(d, "error", ErrorObject);

	/* XXXX Add constants here */
	#include "constants.c"
        
	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module alsaseq");
}

