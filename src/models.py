
from abc import ABC, abstractmethod, abstractproperty
from typing import List, Tuple, Union, Any, Optional
from dataclasses import dataclass

from sklearn.linear_model import LinearRegression # for linear regression of type vs difficulty
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVR
import sklearn.model_selection # for k-fold splitting, see source at https://datascience.stanford.edu/news/splitting-data-randomly-can-ruin-your-model
from sklearn.model_selection import train_test_split
import numpy as np

import sexpdata as sexp

Symbol = sexp.Symbol

Sexpr = Union[sexp.Symbol, int, str, List['Sexpr']]

@dataclass
class Lemma:
  name: str
  type: Sexpr

class ILearner(ABC):
  @abstractmethod
  def learn(self, lemmas: List[Tuple[Lemma, int]]) -> None:
    raise NotImplemented

  @abstractmethod
  def predict(self, lemma: Lemma) -> float:
    raise NotImplemented

  @property
  @abstractmethod
  def name(self) -> str:
    raise NotImplemented

class UnhandledExpr(Exception):

  def __init__(self, e: Sexpr) -> None:
    super().__init__(e)

class NaiveMeanLearner(ILearner):

  _mean: float = 0

  def learn(self, lemmas):
    self._mean = float(np.mean([x for _, x in lemmas]))

  def predict(self, lemma): return self._mean

  @property
  def name(self):
    return "naive mean"

class LinRegressionLearner(ILearner):

  _model : LinearRegression = LinearRegression()

  def learn(self, lemmas):
    lems, ys = zip(*lemmas)
    xs = [[float(nested_size(l.type))] for l in lems]

    self._model.fit(xs, ys)

  def predict(self, lemma):
    return self._model.predict([[float(nested_size(lemma.type))]])

  @property
  def name(self):
    return "LR size"


class SVRLength(ILearner):

  _model : Any = make_pipeline(StandardScaler(), SVR(C=1.0, epsilon=0.2))

  def learn(self, lemmas):
    lems, ys = zip(*lemmas)
    xs = [[float(nested_size(l.type))] for l in lems]

    self._model.fit(xs, ys)

  def predict(self, lemma):
    return self._model.predict([[float(nested_size(lemma.type))]])

  @property
  def name(self):
    return "SVR size"

class SVRIdent(ILearner):

  _model : Any = make_pipeline(StandardScaler(), SVR(C=1.0, epsilon=0.2))

  def learn(self, lemmas):
    lems, ys = zip(*lemmas)
    xs = [[float(ident_size(l.type))] for l in lems]

    self._model.fit(xs, ys)

  def predict(self, lemma):
    return self._model.predict([[float(ident_size(lemma.type))]])

  @property
  def name(self):
    return "SVR idents"

class SVRIdentLength(ILearner):

  _model : Any = make_pipeline(StandardScaler(), SVR(C=1.0, epsilon=0.2))

  def learn(self, lemmas):
    lems, ys = zip(*lemmas)
    xs = [[float(ident_size(l.type)), float(nested_size(l.type))] for l in lems]

    self._model.fit(xs, ys)

  def predict(self, lemma):
    return self._model.predict([[float(ident_size(lemma.type)), float(nested_size(lemma.type))]])

  @property
  def name(self):
    return "SVR idents + size"

def nested_size(obj: Sexpr) -> int:
  if isinstance(obj, sexp.Symbol) or isinstance(obj, str) or isinstance(obj, int):
    return 1
  elif isinstance(obj, List):
    return sum([nested_size(x) for x in obj]) + 1
  else:
    print("weird type?", obj, type(obj))
    raise Exception()

def ident_size(obj: Sexpr) -> int:
  inner = strip_toplevel(obj)
  if not inner:
    return 0

  idents = gather_idents(inner)

  return len(idents)

def strip_toplevel(e: Sexpr) -> Optional[Sexpr]:
  match e:
    case ['CoqConstr', x]:
      return x
    case _ :
      return None

def gather_idents(e: Sexpr) -> set[Sexpr]:
  match e:
    case [name, *args]:
      if name == Symbol("Ind"):
        return gather_idents(args[0][0][0])
      elif name == Symbol("Prod"):
        match e:
          case [_, _, typ, bod]: return gather_idents(typ) | gather_idents(bod)
          case _ : raise UnhandledExpr(e)
      elif name == Symbol("Const"):
        match e:
          case [_, [inner, _]]: return gather_idents(inner)
          case _ : raise UnhandledExpr(e)
      elif name == Symbol("App"):
        f = args[0]
        es = args[1]
        res = gather_idents(f)
        for inner in es:
          res |= gather_idents(inner)
        return res
      elif name == Symbol("LetIn"):
        # let arg0 : arg1 = arg2 in arg3
        return gather_idents(args[1]) | gather_idents(args[2]) | gather_idents(args[3])
      elif name == Symbol("Lambda"):
        # \ arg0 : arg1 . arg2
        return gather_idents(args[1]) | gather_idents(args[2])
      elif name == Symbol("Rel") or name == Symbol("Var") or name == Symbol("Sort") or name == Symbol("MPbound"):
        return set()
      elif name == Symbol("Construct"):
        return gather_idents(args[0][0][0][0])

      elif name == Symbol("Case"):

        base = gather_idents(args[0][0][1][0]) | gather_idents(args[1]) | gather_idents(args[2])
        for inner in args[3]:
          base |= gather_idents(inner)
        return base
      elif name == Symbol("MutInd"):
        pref = join_module(args[0])
        if pref:
          return {f"{pref}.{conv_id(args[1])}"}
        else:
          return set()

      elif name == Symbol('Constant'):
        pref = join_module(args[0])
        if pref:
          return {f"{pref}.{conv_id(args[1])}"}
        else:
          return set()

      else:
        print("unrecognized symbol", name)
        raise UnhandledExpr(e)
        # out = set()
        # for arg in args:
        #   out |= gather_idents(arg)
        # return out
    case int(_) | str(_): return set()
    case _: raise UnhandledExpr(e)

def join_module(e: Sexpr) -> Optional[str]:
  match e:
    case [name, [_, path]] if name == Symbol("MPfile"):
      paths = [conv_id(x) for x in path]
      return '.'.join(paths)
    case [name, inner, outer] if name == Symbol("MPdot"):
      return f"{join_module(inner)}.{conv_id(outer)}"
    case [name, *args] if name == Symbol("MPbound"):
      return None
    case _:
      raise UnhandledExpr(e)
  return None

def conv_id(e: Sexpr) -> Optional[str]:
  match e:
    case [l, r] if l == Symbol('Id'):
      if isinstance(r, Symbol):
        return r.value()
      else:
        return None
    case _ : return None
  return None
