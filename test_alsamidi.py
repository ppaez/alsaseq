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


class Merge(TestCase):

    def test_no_tracks(self):
        from alsamidi import merge

        self.assertEqual([], merge([]))

    def test_track(self):
        from alsamidi import merge

        event = (0, 0, 0, 0, 0)
        self.assertEqual([event], merge([[event]]))

if __name__ == '__main__':
    unittest.main()
