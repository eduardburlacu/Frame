# QPandas Package

## What is it ?
This package provides a simplified implementation of a DataFrame, a tabular data structure with named columns. In this implementation, each column is represented as a QSeries, which can only hold values of a specific type (including None). The DataFrame can hold multiple Series, but each Series within it must have the same number of elements.

This version is limited to read/ create operations, but provides a more robust approach to dealing with missing data. The QSeries defines an expected behaviour for dealing with None for each operation supportable. This is important, as we are able to use data as expected without any surprising loss due to the generic NaN format of Pandas. For example, one might argue that the operation None&True should yield true, as it is invariant on the missing value, while a+None is ambiguous.

## What is next? To-do list

1. Changing lists with masked arrays.
   
2. Implement the processing methods present in Pandas(like views, merging/concatenation etc.)

3. Integration pipeline with the common ML frameworks(Tensorflow,PyTorch,Scikit Learn etc.)
