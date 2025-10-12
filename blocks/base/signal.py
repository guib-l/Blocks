import os
import sys
import time

from typing import Dict, Optional, List, Callable, Any
from enum import Enum, auto


class SignalType(str, Enum):
    """Enumération des types de signaux disponibles."""
    NONE      = 'No signal'
    STAGING   = 'On stage'
    LOADED    = 'Loaded process'
    WAITING   = 'Waiting process'
    RUNNING   = 'Run process'
    INTERRUPTED = 'Interrupted process'
    COMPLETED = 'Process completed'
    CANCELED  = 'Process canceled'
    ERROR     = 'Raise an error'
    WARNING   = 'Warning raised'
    PAUSED    = 'Process paused'
    RESUMED   = 'Process resumed'

    
class SignalError(Exception):
    """Exception levée pour les erreurs liées aux signaux."""
    def __init__(self, message: str = "Signal error occurred", signal_name: Optional[str] = None):
        self.signal_name = signal_name
        if signal_name:
            message = f"{message}: Invalid signal '{signal_name}'"
        super().__init__(message)


# =========================================================
# - COMMENTAIRES -
# Ajouter un systeme de sauvegarde des signaux
# ainsi qu'un gestionnaire d'événements
# handler d'evenement (observer pattern)

class Signal(object):

    __SIGNAL__ = 'NONE'

    def __init__(self, signal):
        self.__SIGNAL__ = signal

    @property
    def signal(self,):
        return self.__SIGNAL__
    
    @signal.setter
    def signal(self, value:str):
        
        try:
            # Convertir en majuscules pour normaliser
            value = value.upper() if isinstance(value, str) else value
                
            # Vérifier si le signal est valide
            if isinstance(value, SignalType):
                signal_type = value
            elif value in [s.name for s in SignalType]:
                signal_type = SignalType[value]
            else:
                raise SignalError("Invalid signal type", value)

            # Mettre à jour le signal
            self.__SIGNAL__ = signal_type.name
        
        except (KeyError, AttributeError):
            raise SignalError("Invalid signal type", value)

    def assign(self, signal=None):

        if signal is not None:
            self.signal = signal

    def __call__(self, new_signal=None):
        if new_signal is not None:
            self.signal = new_signal
        return self.__SIGNAL__

    def __repr__(self):
        return f"Signal({self.__SIGNAL__})"




