from typing import Self
from XPPython3 import xp
from XPPython3.utils.easy_python import EasyPython
from XPPython3.utils.timers import run_timer
from XPPython3.utils.datarefs import find_dataref, DataRef
from XPPython3.xp_typing import XPLMProbeRef

M2FT = 3.28084


class PythonInterface(EasyPython):
    def __init__(self: Self) -> None:
        self.probe: XPLMProbeRef = None
        self.surface: float = None
        self.x: DataRef = None
        self.y: DataRef = None
        self.z: DataRef = None
        super().__init__()

    def onStart(self: Self) -> None:
        self.probe = xp.createProbe()
        self.x = find_dataref('sim/flightmodel/position/local_x')
        self.y = find_dataref('sim/flightmodel/position/local_y')
        self.z = find_dataref('sim/flightmodel/position/local_z')
        run_timer(self.queryProbe, delay=0, interval=5)
        xp.registerDrawCallback(self.draw)
        self.surface = None

    def queryProbe(self: Self) -> None:
        info = xp.probeTerrainXYZ(self.probe, self.x.value, self.y.value, self.z.value)
        self.surface = xp.localToWorld(info.locationX, info.locationY, info.locationZ)[2] * M2FT

    def draw(self: Self, *args) -> None:
        xp.drawString(x=10, y=10, value=f"{self.surface:.0f} ft")


Step 2a
probe demo:  https://github.com/pbuckner/xppython3-demos/blob/main/PI_Probe.py
modify to get all relevant state information
Xplane data ref available:  https://developer.x-plane.com/datarefs/

working list:
these pitch/roll/yaw and throttle are control inputs -1/+1
pitch:  sim/cockpit2/controls/total_pitch_ratio, sim/cockpit2/controls/yoke_pitch_ratio 
roll:  sim/cockpit2/controls/total_roll_ratio , sim/cockpit2/controls/yoke_roll_ratio 
yaw:  sim/flightmodel/controls/rudd_def (?)
throttle:  sim/cockpit2/engine/actuators/throttle_ratio, sim/flightmodel/engine/ENGN_thro, sim/flightmodel2/engines/throttle_used_ratio 
altitue:  sim/cockpit2/gauges/indicators/altitude_ft_pilot 
heading:  sim/cockpit2/gauges/indicators/heading_vacuum_deg_mag_pilot, sim/cockpit2/gauges/indicators/heading_electric_deg_mag_pilot, sim/cockpit2/gauges/indicators/heading_AHARS_deg_mag_pilot 
airspeed:  sim/cockpit2/gauges/indicators/airspeed_kts_pilot 

# from typing import Self
# from XPPython3 import xp
# from XPPython3.utils.easy_python import EasyPython
# from XPPython3.utils.timers import run_timer
# from XPPython3.utils.datarefs import find_dataref, DataRef
# from XPPython3.xp_typing import XPLMProbeRef

# M2FT = 3.28084

# class PythonInterface(EasyPython):
    # def __init__(self: Self) -> None:
        # self.probe: XPLMProbeRef = None
        # self.surface: float = None
        # self.x: DataRef = None
        # self.y: DataRef = None
        # self.z: DataRef = None
        # super().__init__()

    # def onStart(self: Self) -> None:
        # self.probe = xp.createProbe()
        # self.pitch = find_dataref('sim/cockpit2/controls/total_pitch_ratio')
        # self.roll = find_dataref('sim/cockpit2/controls/total_roll_ratio')
        # self.yaw = find_dataref('sim/flightmodel/controls/rudd_def')
        # self.throttle = find_dataref('sim/cockpit2/engine/actuators/throttle_ratio')
        # self.altitude = find_dataref('sim/cockpit2/gauges/indicators/altitude_ft_pilot ')
        # self.heading = find_dataref('sim/cockpit2/gauges/indicators/heading_vacuum_deg_mag_pilot')
        # self.airspeed = find_datatref('sim/cockpit2/gauges/indicators/airspeed_kts_pilot ')
        # run_timer(self.queryProbe, delay=0, interval=5)
        # xp.registerDrawCallback(self.draw)
        # self.surface = None

    # def queryProbe(self: Self) -> None:
        # info = xp.probeTerrainXYZ(self.probe, self.x.value, self.y.value, self.z.value)
        # self.surface = xp.localToWorld(info.locationX, info.locationY, info.locationZ)[2] * M2FT

    # def draw(self: Self, *args) -> None:
        # xp.drawString(x=10, y=10, value=f"{self.surface:.0f} ft")