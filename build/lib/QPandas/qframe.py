"""
This dataframe reimplementation has the API consistent with the original DatFrame
(see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
"""

from collections import OrderedDict
from QPandas.qseries import QSeries
from copy import deepcopy
import warnings
from typing import (
    Union,
    Dict,
)

__all__= ["QFrame"]

class QFrame:
    _HANDLED_TYPES=(Dict, OrderedDict)

    def __init__(
            self,
            data:Union[Dict,OrderedDict,None]=None,
            index=None,
            columns=None,
            make_copy=True
    ):
        self._index_from_data=False
        self._columns_from_data=False
        self._shape= (0, 0)
        self._init_checks(data,index,columns)

        #Set the QFrame index and columns
        if self._index_from_data:
            if self._idx_checks(data):
                #All indexes are equal, using this as common index
                self.index=list(data.values())[0].index
            else:
                # Use default range index for all series
                warnings.warn(
                    "Dictionary contains series with inconsistent series indexes. Using the default range indexing instead..."
                )
                self.index = list(range(self._shape[0]))
        else:
            self.index = index.copy()

        if self._columns_from_data:
            # Use dictionary column index for all series
            self.columns = list(data.keys())
        else:
            self.columns = columns.copy()

        #Store data
        self.data={}
        if make_copy:
            for key,series in zip(self.columns, data.values()):
                self.data[key] = deepcopy(series)
                self.data[key].index = self.index
        else:
            self.data={
                key:series for key,series in
                zip(self.columns, data.values())
            }

    def _init_checks(self,data:Union[Dict,OrderedDict],index,columns):
        #Check data dimension
        ref:QSeries = list(data.values())[0]
        for ser in data.values():
            if len(ser)!=len(ref):
                raise ValueError("Dataframe initialized with series of different lengths")

        #Check index compatibility
        if index is None:
            warnings.warn("Index argument not provided, checking data indexing...")
            self._index_from_data=True
        else:
            assert len(index)==len(ref)
        #Check columns compatibility
        if columns is None:
            warnings.warn("Columns argument not provided, using default range indexing...")
            self._columns_from_data=True
        else:
            assert len(columns)==len(data)
            for c in columns:
                assert isinstance(c,str)

        self._shape = (len(ref),len(data))
    @staticmethod
    def _idx_checks(data):
        if len(data)==0:
            return False
        ref=list(data.values())[0].index
        for ser in data.values():
            if ser.index != ref:
                return False
        return True

    def __repr__(self):
        out = "\n __________________________________\n| Idx "
        for col in self.columns:
            out = out + f"| {col} "
        out =out + "|\n __________________________________\n|     "
        for ser in self.data.values():
            out = out + f"| {str(ser.dtype)} "
        out =out + "|\n __________________________________\n"
        for id in range(len(self.index)):
            current=f"|  {self.index[id]}  "
            for col in self.columns:
                current=current + f"|   {self[id,col]}   "
            current= current + "|\n __________________________________\n"
            out=out+current

        return out

    def __len__(self):
        return self._shape[0]

    @property
    def shape(self):
        return self._shape

    @property
    def index_from_data(self):
        return self._index_from_data

    @property
    def columns_from_data(self):
        return self._columns_from_data

    def __getitem__(self, item):
        if isinstance(item,str):
            try:
                return self.data[item]
            except:
                raise KeyError("Column to access does not exist")

        elif isinstance(item,(tuple,list)):
            assert len(item)==2
            try:
                return self.data[item[1]][item[0]]
            except:
                raise KeyError("Invalid key,column pair")

        elif isinstance(item,QSeries):
            assert item.dtype == bool
            assert self.index == item.index
            tab = {}
            for col,series in self.data.items():
                tab[col] = series[item]

            return QFrame(
                data=tab,
            )

        else:
            raise AttributeError("Getter type not supported")