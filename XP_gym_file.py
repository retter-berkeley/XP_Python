#XP functions to be in python plugin folder
from XPPython3 import xp
import time
class PythonInterface:
    def XPluginStart(self):
        gym.StateDataRef = []
        for Item in range(gym.obs_size):
            gym.InputDataRef.append(xp.findDataRef(gym.StateDataRefDescriptions[Item]))
    
        gym.ActionDataRef = []
        for Item in range(gym.action_size):
            gym.ActionDataRef.append(xp.findDataRef(gym.ActionDataRefDescriptions[Item]))
      
        #XP init:  make item list
        Item = xp.appendMenuItem(xp.findPluginsMenu(), "Python - Position 1", 0)
        gym.PositionMenuHandlerCB = self.PositionMenuHandler
        gym.Id = xp.createMenu("Position1", xp.findPluginsMenu(), Item, self.PositionMenuHandlerCB, 0)
        xp.appendMenuItem(self.Id, "Position1", 1)
    
        # Flag to tell us if the widget is being displayed.
        gym.MenuItem1 = 0
        return gym
    
    def XPobs(self):
        Pitch=[]
        Roll = []
        #Yaw = []
        Throttle =[]
        Alt = []
        Hdg = []
        Speed = []
        count = xp.getDatavf(self.InputDataRef[0], Throttle, 0, 1)
    
        # #Get pitch, roll, yaw
    
        Pitch = xp.getDataf(self.InputDataRef[1])#, self.Pitch, 0, 1) #normalized
        Roll = xp.getDataf(self.InputDataRef[2])#, self.Roll, 0, 1)
        #Yaw = xp.getDataf(self.InputDataRef[3])#, self.Yaw, 0, 1)
    
        # #Get altitude, heading, airspeed
    
        Alt = xp.getDataf(self.InputDataRef[4])#, self.Alt, 0, 1)
        Hdg = xp.getDataf(self.InputDataRef[5])#, self.Hdg, 0, 1)
        Speed = xp.getDataf(self.InputDataRef[6])#, self.Speed, 0, 1)
        #convert to degrees and normalize to +/- 1 with guessed limits 
        SpeedNorm= (Speed-120.)/(170-70) #if speed outside these limits, then fail
        AltNorm= (Alt-4000)/(5500-2500) #if alt outside limits, fail
        HdgNorm = (Hdg-180)/(270-90) # hdg limis 90-270
        #all other already normalized
        return(Pitch, Roll, Throttle, SpeedNorm, AltNorm, HdgNorm)
    
    def XPreset():
        xp.registerFlightLoopCallback(self.InputOutputLoopCB, 3.0, 0)
        AltRef=xp.findDataRef("sim/cockpit2/gauges/indicators/altitude_ft_pilot")
        SpeedRef=xp.findDataRef("sim/cockpit2/gauges/indicators/airspeed_kts_pilot")
        HdgRef=xp.findDataRef("sim/flightmodel/position/true_psi")
        
        xp.setDataf(AltRef, 4000.)
        xp.setDataf(SpeedRef, 120.)
        xp.setDataf(HdgRef, 180.)
    
            #send command
        ThrottleCmd=xp.findDataRef("sim/flightmodel/engine/ENGN_thro")
        PitchCmd=xp.findDataRef("sim/cockpit2/controls/total_pitch_ratio")
        RollCmd=xp.findDataRef( "sim/cockpit2/controls/total_roll_ratio")
        
        xp.setDataf(ThrottleCmd, action[0])
        xp.setDataf(PitchCmd, action[1])
        xp.setDataf(RollCmd, action[2])
       
    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        pass

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass
    
    def XPaction(action):
        #send command
        ThrottleCmd=xp.findDataRef("sim/flightmodel/engine/ENGN_thro")
        PitchCmd=xp.findDataRef("sim/cockpit2/controls/total_pitch_ratio")
        RollCmd=xp.findDataRef( "sim/cockpit2/controls/total_roll_ratio")
        
        xp.setDataf(ThrottleCmd, action[0])
        xp.setDataf(PitchCmd, action[1])
        xp.setDataf(RollCmd, action[2])

        
        #wait X seconds here, then get observation and reward
        xp.registerFlightLoopCallback(MyCallback, 3.0, 0)
        xp.unregisterFlightLoopCallback(MyCallback, 0)

    def MyCallback(lastCall, elapsedTime, counter, refCon):
    
       #xp.log(f"{elapsedTime}, {counter}")
    
       return 1.0
    
    def PositionMenuHandler(self, inMenuRef, inItemRef):
        # If menu selected create our widget dialog
        if inItemRef == 1:
            if self.MenuItem1 == 0:
                self.CreatePosition(300, 600, 300, 550)
                self.MenuItem1 = 1
            else:
                if not xp.isWidgetVisible(self.PositionWidget):
                    xp.showWidget(self.PositionWidget)
    def CreatePosition(self, x, y, w, h):
        FloatValue = []
        for Item in range(self.MAX_ITEMS):
            FloatValue.append(xp.getDataf(self.PositionDataRef[Item]))
    
        # X, Y, Z, Lat, Lon, Alt
        DoubleValue = [0.0, 0.0, 0.0]
        DoubleValue[0], DoubleValue[1], DoubleValue[2] = xp.localToWorld(FloatValue[0], FloatValue[1], FloatValue[2])
        DoubleValue[2] *= 3.28
    
        x2 = x + w
        y2 = y - h
        PositionText = []
    
        # Create the Main Widget window
        self.PositionWidget = xp.createWidget(x, y, x2, y2, 1, "Python - Position Example 1 by Sandy Barbour", 1,
                                              0, xp.WidgetClass_MainWindow)
    
        # Add Close Box decorations to the Main Widget
        xp.setWidgetProperty(self.PositionWidget, xp.Property_MainWindowHasCloseBoxes, 1)

    def XPluginStop(self):
        if self.MenuItem1 == 1:
            xp.destroyWidget(self.PositionWidget, 1)
            self.MenuItem1 = 0

        xp.destroyMenu(self.Id)