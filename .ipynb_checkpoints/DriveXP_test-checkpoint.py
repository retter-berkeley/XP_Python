import numpy as np
import time
import sys

from PI_Drive import PythonInterface as pi

sys.path.insert(0, '/home/amninder/Desktop/Folder_2')

action=np.array([0.,0.,0.,])
while action[0]<1:
    pi.ApplyValues(action)
    action=action+np.array([0.05,0.05,0.05])
    time.sleep(3)
