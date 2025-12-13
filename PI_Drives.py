#Xplane menu and initialization
#XP functions to be in python plugin folder
from XPPython3 import xp
from DDPGv2.functions import Buffer
from DDPGv2 import functions
import tensorflow as tf
import keras
import numpy as np
import datetime

class PythonInterface:
    def XPluginStart(self):
        self.Name = "Drive RL v1.0"
        self.Sig = "tbd"
        self.Desc = "RL training driving XPlane."

        Item = xp.appendMenuItem(xp.findPluginsMenu(), "Python - PI_Drives 1", 0)
        self.InputOutputMenuHandlerCB = self.InputOutputMenuHandler
        self.Id = xp.createMenu("PI_Drives 1", xp.findPluginsMenu(), Item, self.InputOutputMenuHandlerCB, 0)
        xp.appendMenuItem(self.Id, "Data", 1)

        self.StateDataRefDescriptions = ["sim/flightmodel/engine/ENGN_thro", "sim/joystick/yolk_pitch_ratio",
                                   "sim/joystick/yoke_roll_ratio","sim/joystick/FC_ptch",
                                   "sim/cockpit2/gauges/indicators/altitude_ft_pilot", "sim/flightmodel/position/true_psi",
                                   "sim/cockpit2/gauges/indicators/airspeed_kts_pilot"]
        self.ActionDataRefDescriptions = ["sim/flightmodel/engine/ENGN_thro", "sim/cockpit2/controls/total_pitch_ratio",
                                   "sim/cockpit2/controls/total_roll_ratio","sim/flightmodel/controls/rudd_def"]
        self.InputDataRef = []
        for Item in range(7):
            self.InputDataRef.append(xp.findDataRef(self.StateDataRefDescriptions[Item]))
    
        self.ActionDataRef = []
        for Item in range(4):
            self.ActionDataRef.append(xp.findDataRef(self.ActionDataRefDescriptions[Item]))
      
        #XP init:  make item list
        # Item = xp.appendMenuItem(xp.findPluginsMenu(), "Python - Drives 1", 0)
        # #self.PositionMenuHandlerCB = self.PositionMenuHandler
        # self.InputOutputMenuHandlerCB = self.InputOutputMenuHandler
        # self.Id = xp.createMenu("Drives1", xp.findPluginsMenu(), Item, self.PositionMenuHandlerCB, 0)
        # xp.appendMenuItem(self.Id, "Drives1", 1)
    
        # Flag to tell us if the widget is being displayed.
        self.MenuItem1 = 0
        
        #self.XP_test()
        self.InputOutputLoopCB = self.InputOutputLoopCallback
        xp.registerFlightLoopCallback(self.InputOutputLoopCB, 1.0, 0)

        
        return self.Name, self.Sig, self.Desc


    def XPluginStop(self):
        # Unregister the callback
        xp.unregisterFlightLoopCallback(self.InputOutputLoopCB, 0)

        if self.MenuItem1 == 1:
            xp.destroyWidget(self.InputOutputWidget, 1)
            self.MenuItem1 = 0

        xp.destroyMenu(self.Id)

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        pass

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass

    def InputOutputLoopCallback(self, elapsedMe, elapsedSim, counter, refcon):
        if self.MenuItem1 == 0:  # Don't process if widget not visible
            return 1.0

        # Process each engine
        self.start =  datetime.datetime.now().second
        if datetime.datetime.now().second %2 ==0:
            action=np.array([0.1,0.5,-0.5])
        else:
            action=np.array([0.9,-0.5,0.5])
        self.XP_test(action)
        print(datetime.datetime.now().second, action)
        state= self.XPobs()
        print("state ",state)
        # return 0.01 means call us ever 10ms.
        if datetime.datetime.now().second - self.start > 10:
            print("reset cmnd")
            XPreset()
            self.start =  datetime.datetime.now().second
            return 5
        return 1

    def InputOutputMenuHandler(self, inMenuRef, inItemRef):
        # If menu selected create our widget dialog
        if inItemRef == 1:
            if self.MenuItem1 == 0:
                self.CreateInputOutputWidget(300, 550, 350, 350)
                self.MenuItem1 = 1
            else:
                if not xp.isWidgetVisible(self.InputOutputWidget):
                    xp.showWidget(self.InputOutputWidget)

    """
    This will create our widget dialog.
    I have made all child widgets relative to the input paramter.
    This makes it easy to position the dialog
    """
    def CreateInputOutputWidget(self, x, y, w, h):
        x2 = x + w
        y2 = y - h

        # Create the Main Widget window
        self.InputOutputWidget = xp.createWidget(x, y, x2, y2, 1, "Python - XP Drives Example 1",
                                                 1, 0, xp.WidgetClass_MainWindow)

        # Add Close Box decorations to the Main Widget
        xp.setWidgetProperty(self.InputOutputWidget, xp.Property_MainWindowHasCloseBoxes, 1)

       
        self.InputOutputHandlerCB = self.InputOutputHandler
        xp.addWidgetCallback(self.InputOutputWidget, self.InputOutputHandlerCB)

    def InputOutputHandler(self, inMessage, inWidget, inParam1, inParam2):
        if inMessage == xp.Message_CloseButtonPushed:
            if self.MenuItem1 == 1:
                xp.hideWidget(self.InputOutputWidget)
            return 1

        return 0
        
    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        pass

    
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
        Throttle = xp.getDataf(self.InputDataRef[0])
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
        state = np.array([Pitch, Roll, Throttle, SpeedNorm, AltNorm, HdgNorm])
        return state
    
    def XPreset(self):
        #xp.registerFlightLoopCallback(self.InputOutputLoopCB, 3.0, 0)
        AltRef=xp.findDataRef("sim/flightmodel/position/elevation")
        SpeedRef=xp.findDataRef("sim/flightmodel/position/true_airspeed")
        HdgRef=xp.findDataRef("sim/flightmodel/position/mag_psi ")
        
        xp.setDataf(AltRef, 4000.)
        xp.setDataf(SpeedRef, 120.)
        xp.setDataf(HdgRef, 180.)
    
        # #send command
        ThrottleCmd=xp.findDataRef("sim/flightmodel/engine/ENGN_thro")
        PitchCmd=xp.findDataRef("sim/joystick/yolk_pitch_ratio")
        RollCmd=xp.findDataRef( "sim/joystick/yolk_roll_ratio")
        
        xp.setDataf(ThrottleCmd, 0.5)
        xp.setDataf(PitchCmd, 0.0)
        xp.setDataf(RollCmd, 0.0)
        print("reset")
        state = self.XPobs()
        return state

    def XPaction(self,action):
        #send command
        ThrottleCmd=xp.findDataRef("sim/flightmodel/engine/ENGN_thro")
        PitchCmd=xp.findDataRef("sim/joystick/yolk_pitch_ratio")
        RollCmd=xp.findDataRef( "sim/joystick/yolk_roll_ratio")
        
        xp.setDataf(ThrottleCmd, action[0])
        xp.setDataf(PitchCmd, action[1])
        xp.setDataf(RollCmd, action[2])

        #wait X=1 seconds here, then get observation and reward
        # xp.registerFlightLoopCallback(self.MyCallback, 1.0, 0)
        # xp.unregisterFlightLoopCallback(self.MyCallback, 0)
        state=self.XPobs()
        reward=np.sqrt(10.*(state[3])**2+10.*(state[4])**2+10.*(state[5])**2)
        done=False
        truncated=False
        if (state[3]>1 or state[3]<-1 or state[4]>1 or state[4]<-1 or 
            state[5]>1 or state[5]<-1 ):
            truncated= True
            reward=-5000  #if beyond these bounds then consider as departed controlled flight
        
        return state, reward, done, truncated

        

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

    def XPPPO(self):
        std_dev = 0.2
        ou_noise = functions.OUActionNoise(mean=np.zeros(1), std_deviation=float(std_dev) * np.ones(1))
        
        actor_model = functions.get_actor()
        critic_model = functions.get_critic()
        
        target_actor = functions.get_actor()
        target_critic = functions.get_critic()
        
        # Making the weights equal initially
        target_actor.set_weights(actor_model.get_weights())
        target_critic.set_weights(critic_model.get_weights())
        
        # Learning rate for actor-critic models
        critic_lr = 0.002
        actor_lr = 0.001
        
        critic_optimizer = keras.optimizers.Adam(critic_lr)
        actor_optimizer = keras.optimizers.Adam(actor_lr)
        
        total_episodes = 100
        # Discount factor for future rewards
        gamma = 0.99
        # Used to update target networks
        tau = 0.005

        num_states = 6
        num_actions = 3
        
        self.buffer = Buffer(50000, 64, num_states, num_actions)

        ep_reward_list = []
        # To store average reward history of last few episodes
        avg_reward_list = []
        
        for ep in range(total_episodes):

            prev_state, _ = self.XPreset
            
            episodic_reward = 0
            n_step = 0
            while True:
                tf_prev_state = keras.ops.expand_dims(
                    keras.ops.convert_to_tensor(prev_state), 0
                )
        
                action = policy(tf_prev_state, ou_noise)
                state, reward, done, truncated, _ = self.XPaction(action)
        
                buffer.record((prev_state, action, reward, state))
                episodic_reward += reward
        
                buffer.learn()
        
                update_target(target_actor, actor_model, tau)
                update_target(target_critic, critic_model, tau)

                if n_step > 100: done = True 
                else: n_step+=1
                # End this episode when `done` or `truncated` is True
                if done or truncated:
                    break
        
                prev_state = state
        
            ep_reward_list.append(episodic_reward)
        
            # Mean of last 40 episodes
            avg_reward = np.mean(ep_reward_list[-40:])
            print("Episode * {} * Avg Reward is ==> {}".format(ep, avg_reward))
            avg_reward_list.append(avg_reward)      
            
            
    def XP_test(self, action):#self, elapsedMe, elapsedSim, counter, refcon):
        state=self.XPreset()
        #action=np.array([0.1,0.1,0.9])
        state, reward, done, truncated = self.XPaction(action)
        print("PI drives test ",state, reward, done, truncated)
        return 1.00
    