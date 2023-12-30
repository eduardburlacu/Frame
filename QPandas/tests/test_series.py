import unittest
from QPandas.qseries import QSeries

class MyTestCase(unittest.TestCase):
    def test_empty(self):
        s0 = QSeries(data=[], index=[], dtype=str, name="SKU")
        assert len(s0)==0
        assert s0.name=="SKU"

    def test_operations(self):
        s = QSeries(data=[k**2 for k in range(50)], dtype=int,name='squares')
        assert len(s)==50
        assert s.index==list(range(50))
        assert (s - (s//2) >= s//2)==QSeries(data=[True for _ in range(50)], dtype=bool)
        assert (s*2 - s - s) == QSeries(data=[0 for _ in range(50)],dtype=int)

    def test_logic_operations(self):
        t= QSeries(data= [True for _ in range(50)], dtype=bool,name="alltrue")
        f= QSeries(data=[False for _ in range(50)], dtype=bool,name="allfalse")
        assert (t&f) == f
        assert t | f == t
        assert t ^ f == t
        assert ~f == t
        assert ~(t&f) == ((~t) | (~f)) #From De Morgan

    def test_render(self):
        t = QSeries(data=[True for _ in range(50)], dtype=bool, name="alltrue")
        t.render()

if __name__ == '__main__':
    unittest.main()
