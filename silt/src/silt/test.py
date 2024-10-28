
def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the 
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method
    
class Alpha():
    def __init__(self):
        self.test='test'
        self.aval=0
        pass
    
    def printcat(self):
        print('cat')
        print(self.test)
        return 'cat'
    




class Beta():
    def __init__(self):
        self.aval=6
        self.test='woof'
        alpha=Alpha()
        bind(self, alpha.printcat)
        pass
    
    def printdog(self):
        print('dog')
        return 'dog'

beta=Beta()


beta.printcat()
breakpoint()

b.method=a.method1
b.method()
method = a.method1


print('asdg')