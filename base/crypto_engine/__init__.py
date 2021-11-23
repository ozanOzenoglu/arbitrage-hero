import sys,os
print("crypto_engine module init..")
module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
sys.path.append(module_path)