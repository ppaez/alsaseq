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

    def tearDown(self):
        import alsamidi

        alsamidi.merge = self.merge

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
