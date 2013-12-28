#!/usr/bin/env python
#-*-coding:utf-8-*-
from time import sleep,strftime,localtime
class Waiter:
   """
   no thind to do
   """
   def __init__(self,TIME):
      """
	  time by second.
      """
      self.TIME=TIME
      
   def Sleep(self):
       sleep(self.TIME)


if __name__=='__main__':
   TIME=10
   sleeper=Waiter(TIME)
   print "I will going to sleep %s seconds" %  TIME
   sleeper.Sleep()
