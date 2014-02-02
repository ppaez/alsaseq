from __future__ import print_function
from unittest import TestCase


class NoteEvent(TestCase):

    def test(self):
        from alsamidi import noteevent

        midi_event = (1, 60, 127, 1000, 10)
        data = (1, 60, 127, 0, 10)
        expected = (5, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, noteevent(*midi_event))


class NoteOnEvent(TestCase):

    def test(self):
        from alsamidi import noteonevent

        midi_event = (1, 60, 127)
        data = (1, 60, 127, 0, 0)
        expected = (6, 1, 0, 253, (0, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, noteonevent(*midi_event))


class NoteOffEvent(TestCase):

    def test(self):
        from alsamidi import noteoffevent

        midi_event = (1, 60, 10)
        data = (1, 60, 10, 0, 0)
        expected = (7, 1, 0, 253, (0, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, noteoffevent(*midi_event))


class PgmChangeEvent(TestCase):

    def test_sent_directly(self):
        from alsamidi import pgmchangeevent

        data = (1, 0, 0, 0, 0, 9)
        expected = (11, 1, 0, 253, (0, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, pgmchangeevent(1, 9))

    def test_scheduled(self):
        from alsamidi import pgmchangeevent

        data = (1, 0, 0, 0, 0, 9)
        expected = (11, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, pgmchangeevent(1, 9, 1000))


class PitchbendEvent(TestCase):

    def test_sent_directly(self):
        from alsamidi import pitchbendevent

        data = (1, 0, 9)
        expected = (13, 1, 0, 253, (0, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, pitchbendevent(1, 9))

    def test_scheduled(self):
        from alsamidi import pitchbendevent

        data = (1, 0, 9)
        expected = (13, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, pitchbendevent(1, 9, 1000))


class ChanPress(TestCase):

    def test_sent_directly(self):
        from alsamidi import chanpress

        data = (1, 0, 9)
        expected = (12, 1, 0, 253, (0, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, chanpress(1, 9))

    def test_scheduled(self):
        from alsamidi import chanpress

        data = (1, 0, 9)
        expected = (12, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        self.assertEqual(expected, chanpress(1, 9, 1000))


class Tuple2Time(TestCase):

    def test(self):
        from alsamidi import tuple2time

        self.assertEqual(1.5, tuple2time((1, 500000000)))


class Time2Tuple(TestCase):

    def test(self):
        from alsamidi import time2tuple

        self.assertEqual((1, 500000000), time2tuple(1.5))


class ModifyEvent(TestCase):

    def test(self):
        from alsamidi import modifyevent

        data = (1, 60, 127, 0, 10)
        event = (5, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        modified_data = (15, 72, 127, 0, 10)
        modified_event = (5, 1, 0, 250, (2, 0), (2, 0), (3, 0), modified_data)
        self.assertEqual(modified_event, modifyevent(event, timedelta=1,
                ch=15, dest=(3, 0), source=(2, 0), queue=250, keydelta=12))


class ModifyEvents(TestCase):

    def test(self):
        from alsamidi import modifyevents

        data = (1, 60, 127, 0, 10)
        event = (5, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        modified_data = (15, 72, 127, 0, 10)
        modified_event = (5, 1, 0, 250, (2, 0), (2, 0), (3, 0), modified_data)
        self.assertEqual([modified_event], modifyevents([event], timedelta=1,
                ch=15, dest=(3, 0), source=(2, 0), queue=250, keydelta=12))


class Merge(TestCase):

    def test_no_tracks(self):
        from alsamidi import merge

        self.assertEqual([], merge([]))

    def test_track(self):
        from alsamidi import merge

        event = (0, 0, 0, 0, 0)
        self.assertEqual([event], merge([[event]]))


class UniqueNotes(TestCase):

    def test(self):
        from alsamidi import uniquenotes

        data = (1, 60, 127, 0, 10)
        event = (5, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        expected = {1: [60]}
        self.assertEqual(expected, uniquenotes([event]))


class TestSeq(TestCase):

    def setUp(self):
        try:
            from mock import Mock
        except:
            from unittest.mock import Mock
        import alsamidi

        alsamidi.print = Mock()

    def  tearDown(self):
        import alsamidi

        del alsamidi.print

    def test_instance(self):
        from alsamidi import Seq

        self.assertTrue(isinstance(Seq(), Seq))

    def test_info(self):
        from alsamidi import Seq
        import alsamidi

        data = (9, 60, 127, 0, 10)
        event = (5, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        track = [event]

        seq = Seq()
        seq.names = ['name']
        seq.tags = 'tags'
        seq.tracks = [track]
        seq.info()
        alsamidi.print.assert_any_call('tags')
        args = '0:', 'name           ', 0, 'Sec.', 1, 'events,', {9: [60]}, 'Hi Bongo'
        alsamidi.print.assert_called_with(*args)


class SeqReadWrite(TestCase):

    def setUp(self):
        try:
            from mock import Mock
        except:
            from unittest.mock import Mock
        import alsamidi

        self.file = Mock()
        text = 'track melody\n' \
               '6,1,0,1,2 5430786,20 0,130 0,1 108 82 0 0\n' \
               'name = value'
        self.file.readlines.return_value = text.split('\n')
        alsamidi.open = Mock(return_value=self.file)

        alsamidi.print = Mock()

    def  tearDown(self):
        import alsamidi

        del alsamidi.open
        del alsamidi.print

    def test_read(self):
        from alsamidi import Seq

        seq = Seq()
        seq.read('path')
        self.assertEqual(['track melody'], seq.names)

    def test_read_default_track(self):
        from alsamidi import Seq

        text = '6,1,0,1,2 5430786,20 0,130 0,1 108 82 0 0'

        self.file.readlines.return_value = text.split('\n')
        seq = Seq()
        seq.read('path')
        self.assertEqual(['Default'], seq.names)

    def test_error(self):
        from alsamidi import Seq
        import alsamidi

        alsamidi.open.side_effect = IOError
        seq = Seq()
        seq.read('path')


if __name__ == '__main__':
    unittest.main()
