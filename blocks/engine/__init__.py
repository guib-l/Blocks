import os
import sys



class ExecutionError(RuntimeError):
    """Base class of error types related to Execution."""

class ExecutionSetupError(ExecutionError):
    """Execution cannot be performed with the given parameters."""

class ExecutionFailed(ExecutionError):
    """Calculation failed unexpectedly."""

class ExecutionNotFound(ExecutionError):
    """Execution not found in the given path."""

class EnvironmentError(ExecutionSetupError):
    """Raised if Execution is not properly set up with Block."""

class InputError(ExecutionSetupError):
    """Raised if inputs given to the calculator were incorrect."""

class OutputError(ExecutionSetupError):
    """Raised if inputs given to the calculator were incorrect."""



