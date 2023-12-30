import unittest
from QPandas.qseries import QSeries
from QPandas.qframe import QFrame

class MyTestCase(unittest.TestCase):
    def test_access(self):
        idx = list(range(4))
        s1 = QSeries(data=["X4E", "T3B", "F8D", "C7X"], index=idx, dtype=str, name="SKU")
        s2 = QSeries(data=[7.0, 3.5, 8.0, 6.0], index=idx, dtype=float, name="price")
        s3 = QSeries(data=[5, 3, 1, 10], index=idx, dtype=int, name="sales")
        s4 = QSeries(data=[False, False, True, False], index=idx, dtype=bool, name="taxed")
        df = QFrame(data={
            s1.name: s1,
            s2.name: s2,
            s3.name: s3,
            s4.name: s4
        },
            index=idx,
            columns=["SKU", "price", "sales", "taxed"])
        assert df.columns==["SKU", "price", "sales", "taxed"]
        assert df.index==list(range(4))
        assert df["taxed"]==s4
        assert df["price"].dtype==float
        assert df[0,"SKU"]=="X4E"
        query_ser= df[(df["price"] + 5.0 > 10.0) & (df["sales"] > 3) & ~df["taxed"]]["SKU"]
        assert query_ser==QSeries(data=["X4E","C7X"],index=[0,3],dtype=str)

    def test_empty(self):
        s0 = QSeries(data=[], index=[], dtype=str, name="SKU")
        df=QFrame(data={"empty":s0})
        assert df.shape[0]==0
        assert df.columns==["empty"]
        assert len(df)==0


if __name__ == '__main__':
    unittest.main()
