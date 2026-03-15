
import os
import time

import numpy as np

def basic_function(n=5, delay=0.2):
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(delay)
        value = np.random.rand()
        print(f"Calcul en cours... étape {i+1}/{n}, valeur aléatoire : {value}")
    return result


