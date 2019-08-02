import time
import random

def quicky_nap(func):
   """
    Quick snap execute a very small random sleep before executing the target function
   :param func: callback
   :return: decorator
   """
   def func_wrapper(*args, **kwargs):
       nap_time = random.uniform(0, 0.5)
       time.sleep(nap_time)
       return func(*args, **kwargs)
   return func_wrapper