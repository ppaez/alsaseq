from unittest import TestCase

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
