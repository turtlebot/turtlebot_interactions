# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the Willow Garage nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import roslib
roslib.load_manifest('turtlebot_dashboard')

import wx
import rospy
import string
import turtlebot_node.srv 

from status_control import StatusControl

from os import path

breaker_prefixes = ("digitalone", "digitaltwo", "digitalthree")

class BreakerControl(StatusControl):
  def __init__(self, parent, id, breaker_index, breaker_name, icons_path):
    StatusControl.__init__(self, parent, id, icons_path, breaker_prefixes[breaker_index], True)
    
    self.Bind(wx.EVT_BUTTON, self.on_click)
    self._index = breaker_index
    self._name = breaker_name
    self.raw_byte = 0
    self._breaker_state = 0
    self._power_control = rospy.ServiceProxy('turtlebot_node/set_digital_output', turtlebot_node.srv.SetDigitalOutputs)
    self.digital_outs =[0,0,0]


    
  def on_click(self, evt):
    self.control(0)    
    return True
    
  def control(self, cmd):
    if (not self._breaker_state):
      wx.MessageBox("Cannot control breakers until we have received a power board state message", "Error", wx.OK|wx.ICON_ERROR)
      return False
        
    try:
      tmp = self._raw_byte
      for i in range(0,3):
        self.digital_outs[i]=tmp%2
        tmp = tmp >> 1
      self.digital_outs[self._index] = not self.digital_outs[self._index] 
      power_cmd = turtlebot_node.srv.SetDigitalOutputsRequest(self.digital_outs[0], self.digital_outs[1], self.digital_outs[2])
      #print power_cmd
      self._power_control(power_cmd)
      
      return True
    except rospy.ServiceException, e:
      wx.MessageBox("Service call failed with error: %s"%(e), "Error", wx.OK|wx.ICON_ERROR)
      return False
      
    return False
  
    
  def set_breaker_state(self, msg):
    self._breaker_state = True
    self._raw_byte = string.atoi(msg['Raw Byte'])
    tmp = self._raw_byte
    for i in range(0,3):
      self.digital_outs[i]=tmp%2
      tmp = tmp >> 1

    if(self.digital_outs[self._index]==0):
      self.set_error()
      status_msg = "Disabled"
    else:
      self.set_ok()
      status_msg = "Enabled"

    
  def reset(self):
    self.set_stale()
    self.SetToolTip(wx.ToolTip("%s: Stale"%(self._name)))
