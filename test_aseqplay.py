from __future__ import print_function
import unittest


class Main(unittest.TestCase):

    def setUp(self):
        try:
            from mock import Mock
        except:
            from unittest.mock import Mock
        import alsamidi
        self.merge = alsamidi.merge
        alsamidi.merge = Mock(return_value=[])
        self.Seq = alsamidi.Seq
        alsamidi.Seq = Mock()
        import aseqplay
        aseqplay.print = Mock()

    def tearDown(self):
        import alsamidi
        import aseqplay

        alsamidi.merge = self.merge
        alsamidi.Seq = self.Seq
        del aseqplay.print

    def test(self):
        import aseqplay

        aseqplay.main(128, 'path')

    def test_display(self):
        import alsamidi
        import aseqplay

        data = (9, 60, 127, 0, 10)
        event = (5, 1, 0, 0, (1, 0), (0, 0), (0, 0), data)
        track = [event]
        alsamidi.merge.return_value = track
        aseqplay.main(128, 'path', display=True)


if __name__ == '__main__':
    unittest.main()
