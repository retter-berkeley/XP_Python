#Gymansium for Xplane
#taken from https://www.gymlibrary.dev/content/environment_creation/
#create gymansium to run XPlane.
#start with XPlane running, use with XPPyhton.  Don't see any way to reload situation
#will need to init by ??
#reset is give new command or set position?
#get obs gets state = [x;u]=[heading, alt, airspeed; pitch, roll, throttle]
#step by?
#to reduce crashes limit commands, faster failure
#start with current state (heading/alt/airspeed + control settings pitch, roll, throttle)
#try to get to commanded state and stay there, reward based on how far from commanded state normalized
#probably make commands a small set of discrete (+/-10 deg hdg change and/or +/-500 alt, airspeed constant)
#try to reach from "random" current state
#need way to time steps--maybe allow input every T=6s sim time, give it 1 sim time minute (at 10x or so sim speed)
#make sure situation display settings are turned way down
#score reward every 6s, cumulative

from os import path
from typing import Optional

import numpy as np
import math
import pde
import random
from XPPython3 import xp

import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.classic_control import utils
from gymnasium.error import DependencyNotInstalled
##At the top of the code
import logging
logger = logging.getLogger('requests_throttler')
logger.addHandler(logging.NullHandler())
logger.propagate = False


#not sure where to put these

#diffusion equation is included in py-pde, so don't need seperate dynamics
#import dynamics
#from dynamics import MGM

class XPlaneEnv(gym.Env):
    #observation space is state and control spaces, normalized
    #space is 7-vector
    #also make variables to support XP python calls
    #also add menu selection slot for XP python
    def __init__(self, render_mode=None, size: int =7):
        #gymansium init:  make spaces
        obs_size=6
        self.observation_space =spaces.Box(low=-1, high=1, shape=(obs_size+2,), dtype=float) #add two for commands
        action_size=3
        self.action_space = spaces.Box(low=-1, high=1, shape=(action_size,), dtype=float) 
        #need to update action to normal distribution

        self.grid=[]
        self.stepper=[]
        #XP init:  make variable list
        self.StateDataRefDescriptions = ["sim/flightmodel/engine/ENGN_thro", "sim/joystick/yolk_pitch_ratio",
                                   "sim/joystick/yoke_roll_ratio","sim/joystick/FC_ptch",
                                   "sim/cockpit2/gauges/indicators/altitude_ft_pilot", "sim/flightmodel/position/true_psi",
                                   "sim/cockpit2/gauges/indicators/airspeed_kts_pilot"]
        self.ActionDataRefDescriptions = ["sim/flightmodel/engine/ENGN_thro", "sim/cockpit2/controls/total_pitch_ratio",
                                   "sim/cockpit2/controls/total_roll_ratio","sim/flightmodel/controls/rudd_def"]


        #XP call
        XPinit(self)
        
        
    def _get_obs(self):

        Pitch, Roll, Throttle, AltNorm, HdgNorm, SpeedNorm=XPobs(self)
        self.state.data=[Pitch, Roll, Throttle, AltNorm, HdgNorm, SpeedNorm, self.command[0], self.command[1]]
        return self.state

    def reset(self, seed: Optional[int] = None, options=None):
        #reset to altitude 4000, airspeed 120, heading 180
        #only doing relative heading/altitude changes so shouldn't affect things much
        AltRef=xp.findDataRef("sim/cockpit2/gauges/indicators/altitude_ft_pilot")
        SpeedRef=xp.findDataRef("sim/cockpit2/gauges/indicators/airspeed_kts_pilot")
        HdgRef=xp.findDataRef("sim/flightmodel/position/true_psi")
        
        xp.setDataf(AltRef, 4000.)
        xp.setDataf(SpeedRef, 120.)
        xp.setDataf(HdgRef, 180.)

        #commands randmoly chosen from a matrix of possible commands 
        #+/- 45 deg heading, with fixed initial heading this is 225 or 135
        #+/- 500 ft elevation, with fixed initial altitude this is 4500 or 3500
        #combination of the two
        #commands is 2x8 array with heading change, elevation change as each row
        #commands = np.array([[225., 4000.], [135., 4000.], [180., 4500.], [180., 3500.], [225., 4500.], [135., 4500.], [225., 3500.], [135., 3500.]])
        #issue normalized commands
        commands = np.array([[45./180., 0.], [-45./180., 0.], [0., 500./3000], [0., -500./3000], [45./180, 500./3000], 
                             [-45./180, 500./3000], [45./180, -500./3000], [-45./180, -500./3000]])
        #choose a random command to send
        n=random.randint(0,7)
        self.command = commands[n,]

        observation = self._get_obs()
        
        return observation
        
    def step(self,action):
        #design of the training will need to be period of time (30s-1min sim time) where aagent tries to acheive command, then reset position and command
        #during each period T agent can continuously control pitch, roll, throttle (leave rudder/yaw out for now and just do uncoordinated)
        #if altitude change by more than 1500 feet or heading change by more than 90 degrees, or speed change by more than 50kts then fail
        #want to sample for reward and updating control input every X sim seconds (start with T/10)
        #what/how does step work then, is it every 6 seconds or an entire period?  Each step should be a period or a full contorl/reward interval
        #action to be a numpy 3-vector pitch commmand, roll command, throttle command
          
        #self.state.data[0,:]=action[0]
        state=self.state   
        XPaction(action)
        observation=self._get_obs()
        reward=np.sqrt((self.state.data[3]-self.command[1])**2+(self.state.data[4]-self.command[0])**2+(self.state.data[5]-120.)**2)
        done=False
        truncated=False
        if (self.state.data[3]>5500 or self.state.data[3]<2500 or self.state.data[4]>270 or self.state.data[4]<090 or 
            self.state.data[5]>170 or self.state.data[5]<70 ):
            truncated= True
            reward=-5000
        state=self.state
 
        return self.state, reward, done, truncated, {}
    
    
    def close(self):
        XPluginStop