
class TestModule1(object):

  def stateupdate(self, a):
    print "received state update %s" % str(a)

  def crazy_function(self, a, b, name=None):
    print "a: %s, b: %s, name=%s" % (a, b, name)


class TestModule2(object):

  def blahness(self, b):
    print "fuckit! %s" % str(b)

class Modules(object):

  def __init__(self):
    self.modules = []
    self.modules.append(TestModule1())
    self.modules.append(TestModule2())

  def iter_modules_with(self, attr):
    for m in self.modules:
      if hasattr(m, attr):
        yield m

  def responds_to(self, attr):
    for m in self.modules:
      if hasattr(m, attr):
        yield getattr(m, attr) 


  def trigger(self, attr, *args, **kwargs):
    for f in self.responds_to(attr):
      f(*args, **kwargs)


main = Modules()

for m in main.iter_modules_with('stateupdate'):
  m.stateupdate("moooo")

for f in main.responds_to('blahness'):
  f("moooo")

main.trigger('crazy_function', 1, 2, name="Niels")