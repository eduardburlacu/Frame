"""
This series reimplementation has the API consistent with the original Series
(see https://pandas.pydata.org/docs/reference/api/pandas.Series.html)
"""
from collections.abc import Hashable
from collections import OrderedDict
import warnings
from IPython.display import display,HTML
import plotly.graph_objects as go
from typing import (
    List,
    Union,
    Tuple,
    Dict,
    Literal
)

__all__= ["QSeries"]

class QSeries:
    _HANDLED_INPUT_TYPES=(List,Tuple,Dict,OrderedDict)
    _HANDLED_DTYPES=(float,int,str,bool)
    _NAME: Hashable
    HTML:bool = False

    """
    :param allow_none_equality(bool) : If set to True, == between None and None will
     always yield True(warning raised).
    If set to False, comparisons between None types yield None. 
    
    :param allow_none_comparison(bool) : If set to True, inequalities between None and 
    other type will always yield False.
    If set to False, comparisons with None type will yield None.
    """
    allow_none_equality = False
    allow_none_comparison=False
    # See the code for __get_item__
    element_access:Literal["python_std","in_range","circular"] ="python_std"

    def __init__(
            self,
            data:Union[Dict,OrderedDict,List,Tuple]= None,
            index= None,
            dtype= None,
            name=None,
    ):
        """
        :param data: Usually initialized using Lists. Values of series considered.
         Must be of unique datatype or None for missing values.
        :param index: List with Series indexes. If missing, the range indexing is used.
        :param dtype: One of the entries in _HANDLED_DTYPES.
        Operations are strictly between Series of identical dtype.
        :param name: String used for hashing purposes in a QFrame
        if the columns are not provided
        """
        self.set_name(name)
        self.index=None
        self.values=None
        self.dtype = dtype
        self._get_with(data, index, self.dtype)

    def _init_dict(
            self,
            data:Union[dict, OrderedDict],
            index:Union[List,Tuple]=None,
            dtype: Union[str,None]  = None,
    ):
        # Initializer function for dictionary data entries
        cdata=data.copy()
        keys = list(cdata.keys())
        vals = list(cdata.values())

        #Indexing checks
        if index is not None:
            assert (self._check_type(index,Hashable)==0)

            if len(index)!=len(keys):
                raise AttributeError("Index argument not consistent to the dimension of data")
            self.index = list(index)

        else:
            warnings.warn("Index argument not hashable/not provided... using the dictionary keys instead")
            self.index = list(keys)


        #Entries checks
        if dtype is not None:
            self._check_type(vals,dtype,allow_none=True)
            self.values=vals
        else:
            warnings.warn("Data type not specified, using the default type in the dict values if possible...")
            if len(vals)==0:
                raise AttributeError("Ambiguous Series declaration for empty series. dtype needs to be passed as argument" )

            elif self._check_type(vals,type(vals[0]),allow_none=True)==0:
                self.values=vals
                self.dtype=type(vals[0])
            else:
                raise AttributeError("Data includes different types and no dtype argument has been passed.")

    def _init_list(
            self,
            data:Union[List,Tuple],
            index:Union[List,Tuple],
            dtype: Union[str, None]  = None,
    ):
        # Initializer function for list data entries
        cdata=data.copy()
        #Indexing checks
        if index is not None and self._check_type(index, Hashable)==0:
            if len(index)!=len(cdata):
                raise AttributeError("Index argument not consistent to the dimension of data")
            self.index = list(index)

        else:
            if index is not None:
                warnings.warn("Dictionary keys not hashable... using the range indexing instead")
            self.index=list(range(len(cdata)))

        #Entries checks
        if dtype is not None:
            self._check_type(cdata, dtype, allow_none=True)
            self.values = cdata
        else:
            warnings.warn("Data type not specified, using the default type in the data if possible...")
            if len(cdata) == 0:
                raise AttributeError(
                    "Ambiguous Series declaration for empty series. dtype needs to be passed as argument")
            elif self._check_type(cdata, type(cdata[0]),allow_none=True):
                self.values = cdata
            else:
                raise AttributeError("Data includes different types and no dtype argument has been passed.")

    def _get_with(
            self,
            data:Union[List,Tuple],
            index: Union[List, Tuple],
            dtype: Union[str, None] = None,
    ):
        if isinstance(data,list) or isinstance(data,tuple):
            self._init_list(data,index,dtype)
        elif isinstance(data, dict) or isinstance(data,OrderedDict):
            self._init_dict(data,index,dtype)
        else:
            raise NotImplementedError("Data type not supported yet")

    def set_name(self,name:str):
        # Can be overriden as well.
        if isinstance(name, Hashable):
            if name is not None:
                self.name = name
            else:
                warnings.warn("Name not provided for series initialization, using default empty name")
                self.name=""
        else:
            raise AttributeError("Series name is not hashable")


    def type(self):
        if self.dtype==int:
            return "int"
        elif self.dtype==float:
            return "float"
        elif self.dtype==bool:
            return "bool"
        elif self.dtype==str:
            return "str"
        else:
            raise TypeError("Invalid dtype.")
    @staticmethod
    def _check_type(item, dtype, allow_none=False):
        # Method for checking an item has the requested dtype.
        if isinstance(dtype,(tuple,list)):
            checker = (*dtype,type(None))
            # This ensures True/False entries are not considered int
            if bool not in dtype:
                if any([isinstance(element, bool) for element in item]):
                    raise AttributeError(f"Data argument passed with inconsistent data type, requested as {dtype}")
        else:
            checker=(dtype, type(None))
            if dtype!=bool:
                if any([isinstance(element, bool) for element in item]):
                    raise AttributeError(f"Data argument passed with inconsistent data type, requested as {dtype}")

        if allow_none and not all([isinstance(element, checker) for element in item]):
            raise AttributeError(f"Data argument passed with inconsistent data type, requested as {dtype}")
        elif not allow_none and not all([isinstance(element,dtype) for element in item]):
            raise AttributeError(f"Data argument passed with inconsistent data type, requested as {dtype}")
        else:
            return 0

    @staticmethod
    def none_equality():
        # Typical pattern for operations that
        # handle None arithmetic like ==
        if QSeries.allow_none_equality:
            return True
        else:
            return None

    @staticmethod
    def none_inequality():
        # Typical pattern for comparison operations
        if QSeries.allow_none_comparison:
            return False
        else:
            return None

    @staticmethod
    def compare(val, other_val, operator:str):
        # To do: For Python >=3.10 use match-case statement
        if operator=='>':
            return val>other_val
        elif operator=='<':
            return val<other_val
        elif operator=='>=':
            return val>=other_val
        elif operator=='<=':
            return val<=other_val
        elif operator=='!=':
            return val!=other_val
        elif operator=="==":
            return val==other_val
        elif operator=="&":
            return val and other_val
        elif operator=="|":
            return val or other_val
        elif operator=="^":
            return val^other_val
        elif operator=="+":
            return val+other_val
        elif operator=="-":
            return val-other_val
        elif operator=="*":
            return val*other_val
        elif operator=="/":
            if other_val in {0,0.0}:
                raise ZeroDivisionError("Divisor QFrame contains one ore more zeros")
            return val/other_val
        elif operator=="//":
            if other_val in {0,0.0}:
                raise ZeroDivisionError("Divisor QFrame contains one ore more zeros")
            return val//other_val
        else:
            raise(AttributeError("Comparison operator not supported"))

    def _get_comparison_data(self, other, operator:str, custom_none:Tuple=tuple())->Tuple[List,str]:
        """
        :param operator: Symbol to be used in compare method

        :param custom_none: Tuple of length 2 showing how the defined function,
        say @, behaves for None @ None, x @ None. Ex.(None,None),(True,None) etc.

        :return: Tuple[
                    data:List the value of the operator applied to all entries. ,
                    name:str a predifined name for the new series
                    ]
        """
        data = []
        if len(custom_none)==2:
            assert all([isinstance(e,(bool,type(None))) for e in custom_none])
        elif len(custom_none)==0:
            custom_none=[self.none_inequality(),self.none_inequality()]

        else:
            raise AttributeError("Custom none length should be 2 or 0")

        if type(other)==QSeries:
            assert self.dtype == other.dtype
            assert self.index == other.index # Implicitly checks length match
            name=f"{self.name} {operator} {other.name}"
            for val, other_val in zip(self.values,other.values):
                cond=[type(val)==type(None), type(other_val)==type(None)]
                if all(cond):
                    data.append(custom_none[0])
                elif any(cond):
                    data.append(custom_none[1])
                else:
                    data.append(self.compare(val,other_val,operator))

        elif self.dtype in QSeries._HANDLED_DTYPES and type(other) in QSeries._HANDLED_DTYPES:
            assert self.dtype == type(other)
            name = f"{self.name} {operator} {self.type()}"
            for val in self.values:
                cond =[type(val)==type(None), type(other)==type(None)]
                if(all(cond)):
                    data.append(custom_none[0])
                elif any(cond):
                    data.append(custom_none[1])
                else:
                    data.append(self.compare(val,other,operator))

        else:
            raise TypeError("Comparison object not supported for QSeries")

        return data, name

    def render(self):
        """
        Use a specialized table visualisation tool. Only work within Jupyter Notebooks. To allow rendering:
        QFrame.HTML=True
        series.render()
        """
        if QSeries.HTML:
            table = go.Figure(data=[go.Table(
                header={"values": ["Idx", self.name],"fill_color":'lightblue', "align":'center'},
                cells={"values": [self.index, self.values],"fill_color":'lavender', "align":'center'}
            )])
            table.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="LightSteelBlue",
            )
            display(HTML(table.to_html()))
        else:
            warnings.warn("Rendering only possible when using Jupyter Notebook")

    def __repr__(self):
        out= repr(self.name) + "\n__________________\n"
        for id, val in zip(self.index,self.values):
            out = out + f"|  {id}   |  {val}  |\n" + "__________________\n"

        out=out + "dtype: " + self.type()
        return out

    def __len__(self):
        return len(self.index)

    def __add__(self, other):
        assert self.dtype in {float,int,str}
        data, name = self._get_comparison_data( other,"+",(None,None) )
        return QSeries(
            data=data,
            index=self.index,
            dtype=self.dtype,
            name=name,
        )

    def __sub__(self, other):
        assert self.dtype in {float, int}
        data, name = self._get_comparison_data( other,"-",(None,None) )
        return QSeries(
            data=data,
            index=self.index,
            dtype=self.dtype,
            name=name,
        )

    def __mul__(self, other):
        assert self.dtype in {float, int, str}
        data, name = self._get_comparison_data( other,"*",(None,None) )
        return QSeries(
            data=data,
            index=self.index,
            dtype=self.dtype,
            name=name,
        )

    def __truediv__(self, other):
        assert self.dtype in {float, int}
        data, name = self._get_comparison_data( other,"/",(None,None) )
        return QSeries(
            data=data,
            index=self.index,
            dtype=float,
            name=name,
        )

    def __floordiv__(self, other):
        assert self.dtype in {float, int}
        data, name = self._get_comparison_data( other,"//",(None,None) )
        return QSeries(
            data=data,
            index=self.index,
            dtype=self.dtype,
            name=name,
        )

    def __and__(self, other):
        assert self.dtype==bool
        data, name = self._get_comparison_data(other,"&",custom_none=(self.none_inequality(),self.none_inequality()))

        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __or__(self, other):
        assert self.dtype==bool
        data, name = self._get_comparison_data(other,"|",custom_none=(self.none_equality(),self.none_equality()))
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __xor__(self, other):
        assert self.dtype==bool
        data, name = self._get_comparison_data(other,"^",custom_none=(None,None))
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __invert__(self):
        assert self.dtype == bool
        name = f"not {self.name}"
        data=[]
        for val in self.values:
            if type(val) == type(None):
                data.append(None)
            else:
                data.append(not val)
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __gt__(self, other):
        data,name=self._get_comparison_data(other,">")
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __ge__(self, other):
        data, name=self._get_comparison_data(other,">=")
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __lt__(self, other):
        data, name =self._get_comparison_data(other,"<")
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __le__(self, other):
        data, name=self._get_comparison_data(other,"<=")
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __ne__(self, other):
        data, name=self._get_comparison_data(other,"!=")
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __eq__(self, other):
        data, name = self._get_comparison_data(other, "==",custom_none=(self.none_equality(),self.none_inequality()))
        return QSeries(
            data=data,
            index=self.index,
            dtype=bool,
            name=name,
        )

    def __getitem__(self, item):
        """
        :param item:
            - If item is int, it returns the (i+1)th element in the series(irrespective of indexing names)
             If item is a boolean QSeries(condition), it returns a new QSeries with all the entries from the
            original series that correspond to True in the condition series
        """
        if isinstance(item, int):
            # Choose if the access index remains circular,
            # within the original range or matched with
            # the Python standard library
            if QSeries.element_access=="python_std":
                if (item<-len(self) or item>=len(self)):
                    raise IndexError("QSeries index out of range")
                return self.values[item]
            elif QSeries.element_access=="in_range":
                if item<0 or item>=len(self):
                    raise IndexError("QSeries index out of range")
                return self.values[item]
            elif QSeries.element_access=="circular":
                return self.values[item%len(self)]
            else:
                raise AttributeError("Element access key not supported")

        elif isinstance(item,QSeries):
            assert item.dtype==bool
            assert self.index==item.index
            data=[]
            idx=[]
            for i in range(len(self)):
                if item.values[i]:
                    idx.append(self.index[i])
                    data.append(self.values[i])

            return QSeries(
                data=data,
                index=idx,
                dtype=self.dtype,
                name=f"{self.name}[{item.name}]"
            )
        else:
            raise AttributeError("Accessor must be either integer or boolean QSeries")
