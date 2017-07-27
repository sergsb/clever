import sys

from operators.exceptions import InternalTypeException, NoModuleException
import re

def get_short_name_for_type(instance):
    """
    <class 'datatypes.strings.Smiles'> to smiles
    :return: short name
    """
    try:
        return  (re.search('\w+\'', str(instance)).group(0)[:-1].lower())
    except:
        return None

class Operator(object):
    pass
    '''
    prevlink = None
    def __init__(self,input_type,output_type):
        # Check requirements
        for requirement in self.requirements:
            if requirement not in sys.modules: raise NoModuleException("We have no module {}".format(requirement))
        assert input_type in self.possible_input
        assert output_type in self.possible_output

    def __rshift__(self, other):
        if not isinstance(other,Operator): raise InternalTypeException("The type to bind is not the same {}".format(type(other)))
        other.prevlink = self
        return other
    '''