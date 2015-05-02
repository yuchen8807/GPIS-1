from abc import ABCMeta, abstractmethod

import models

class TerminationCondition:
    """
    Returns true when a condition is satisfied
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, k, cur_val, prev_val, cur_gradient = None, model = None):
        """
        Returns true or false based on whether or not a termination condition was met
        """
        pass

class MaxIterTerminationCondition(TerminationCondition):
    """
    Terminate based on too little progress
    """
    def __init__(self, max_iters):
        self.max_iters_ = max_iters

    def __call__(self, k, cur_val, prev_val, cur_gradient = None, model = None):
        return (k >= self.max_iters_)

class ProgressTerminationCondition(TerminationCondition):
    """
    Terminate based on lack of progress
    """
    def __init__(self, eps):
        self.eps_ = eps

    def __call__(self, k, cur_val, prev_val, cur_gradient = None, model = None):
        return (math.abs(cur_val - prev_val) < self.eps_)

class ConfidenceTerminationCondition(TerminationCondition):
    """
    Terminate based on model confidence
    """
    def __init__(self, eps):
        self.eps_ = eps

    def __call__(self, k, cur_val, prev_val, cur_gradient = None, model = None):
        return (model.confidence() < self.eps_)
    
class OrTerminationCondition(TerminationCondition):
    def __init__(self, term_conditions):
        self.term_conditions_ = term_conditions

    def __call__(self, k, cur_val, prev_val, cur_gradient = None, model = None):
        terminate = False
        for term_condition in term_conditions:
            terminate = terminate or term_condition(k, cur_val, cur_gradient, prev_val, model)
        return terminate

class AndTerminationCondition(TerminationCondition):
    def __init__(self, term_conditions):
        self.term_conditions_ = term_conditions

    def __call__(self, k, cur_val, prev_val, cur_gradient = None, model = None):
        terminate = True
        for term_condition in term_conditions:
            terminate = terminate and term_condition(k, cur_val, cur_gradient, prev_val, model)
        return terminate
