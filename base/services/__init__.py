import os,sys
print("init_services of services module")

module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
print("{:s} is added to sys paths".format(str(module_path)))
sys.path.append(module_path)