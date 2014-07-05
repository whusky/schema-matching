from __future__ import print_function
import utilities, itertools

if __debug__:
  import sys


class ItemCollector(object):
  """Base class for collecting information about a column"""


  def dependencies(self):
    """Return collector types this collector depends on"""
    return ()


  def collect(self, item, collector_set = None):
    """Called for every item in a column.
    Dependencies are guaranteed to have collected the same value before this collected.
    Override this in subclasses.
    """
    pass


  def get_result(self, collector_set = None):
    """Returns the result of this collector after all items have been collected."""
    return NotImplemented



class ItemCollectorSet(ItemCollector, dict):
  """Manages a set of collectors for a single column"""

  def __init__(self, collectors = ()):
    ItemCollector.__init__(self)
    dict.__init__(self)
    self.__semiordered_keylist = list()
    utilities.each(self.add, collectors)


  def collect(self, item, collector_set = None):
    assert collector_set is None
    ItemCollector.collect(self, item, self)
    utilities.each(
      lambda collector: collector.collect(item, self),
      map(self.__getitem__, self.__semiordered_keylist))


  def get_result(self, collector_set = None):
    assert collector_set is None
    return (collector.get_result(self) for collector in self.itervalues())


  def __str__(self):
    return '{{{}}}'.format(', '.join(
      ('{}: {}'.format(cls.__name__, collector.get_result()) for cls, collector in self.iteritems())))


  def add(self, collector):
    """Adds an item collector and all its dependencies to this set with its type a key,
    if one of the same type isn't in the set already.

    Returns the collector the same type from this set, possibly the one just added.
    """
    if isinstance(collector, type):
      collector = collector()

    utilities.each(self.add, collector.dependencies())
    result = self.setdefault(collector.__class__, collector)
    if result is collector:
      self.__semiordered_keylist.append(collector.__class__)
      assert len(self.__semiordered_keylist) == len(self)
      assert len(self) == len(set(self.__semiordered_keylist))
    return result



class RowCollector(list):
  """Manages collectors for a set of rows"""

  def collect(self, *items):
    """Collects the data of all columns of a row"""
    if __debug__ and len(self) != len(items):
      print('Row has {} columns, expected {}: {}'.format(len(items), len(self), items), file=sys.stderr)

    assert len(self) <= len(items)
    utilities.each_unpack(lambda collector, item: collector.collect(item), itertools.izip(self, items))


  def __str__(self):
    return '[{}]'.format(', '.join(map(str, self)))
