import unittest


class Main(unittest.TestCase):

    def test(self):
        import aseqplay

        aseqplay.main(128, 'path')


if __name__ == '__main__':
    unittest.main()
