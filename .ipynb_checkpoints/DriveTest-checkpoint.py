#test if an external file can send commands to XP via an XPPython call
import PI_ThrottleControl as tc
sys.path.insert(0, '/home/amninder/Desktop/Folder_2')
Pitch, Roll, Throttle, SpeedNorm, AltNorm, HdgNorm = tc.obs()
print(Pitch)
tc.SetPitch(Pitch+0.05)