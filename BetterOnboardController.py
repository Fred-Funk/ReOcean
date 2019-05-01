#Takes data from radio and removes the newline character
def dataclean(input):
  output = input[:-1]
  return output
#Takes two bearings and finds the smallest distance between them
def error(input, target):
  if (input>target):
    if (input-target >= 1800):
      return(input-3600-target)
    else:
      return(input-target)
  else:
    if(target-input >= 1800):
      return(3600-target+input)
    else:
        return(input-target)
#Takes PID output and converts to voltages        
def normalize(input):
  return input/3000*1.4

#Takes voltage and min caps it at 7.4
def minbound(input):
  if input< 7.4:
    return 7.4
  else:
    return input
#Takes voltage and max caps at 9
def maxbound(input):
  if input>9:
    return 9
  else:
    return input    
#Returns the error messagw
def error_handling():
    return 'Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno)

#Importing libraries
import sys
sys.path.append('/home/debian/.local/lib/python3.5/site-packages/') #Add path to BBB
import serial
import time
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
from simple_pid import PID 

#Turning on LED
GPIO.setup("P8_8", GPIO.OUT)
GPIO.output("P8_8", GPIO.HIGH)

#Set up remote control radio serial channel 
serComm = serial.Serial()
serComm.baudrate = 9600
serComm.port = '/dev/ttyUSB0'
serComm.timeout= 0.5
#Set up magnetometer serial channel
serMag = serial.Serial()
serMag.baudrate = 9600
serMag.port = '/dev/ttyO1'
serMag.timeout = 0.5
serMag.open()

rest = 7.5 #Motor resting voltage
secs = 0.150 #Time to hold motors at constage voltage
center= 7 #Servo center position PWM signal
righttoggle = 6 #Servo right position PWM signal
lefttoggle = 8 #Servo left position PWMN signal
speed = 8.3 #Initial voltage 
left = "P9_14" #Pin for left motor
right = "P9_16" #Pin for right motor
servo= "P8_13" #Pin for servo
servoToggle= True #Initial toggle state for servo
target = 1800 #Hard coded target bearing for testing

#Keep on trying to start the motors and open the radio channel
while True:
  try:
    PWM.start(left, rest, 50, 0)
    PWM.start(right, rest, 50, 0)
    print("Trying")
    serComm.open()
  except:
    time.sleep(secs)
  else:
    break

#Once radio channel is connected read commands from radio
try:
  while True:
    letter = serComm.read()
    print("Letter Read")

    #Quit sequence
    if letter == b'p':
      PWM.stop(left)
      PWM.stop(right)
      PWM.cleanup()
      break

    #Autonomous sequence
    elif letter == b'1':
    
      pid = PID(8, 0.3, 0.001, setpoint=0) #PID
      while True:
        print("Automode")
        speed = 8.3
        letter = serComm.read()
        print("Test")
        
        #Quitting Autonomous
        if letter == b'2':
          serComm.reset_input_buffer()
          break

        #Reading magnetometer
        bearing = serMag.readline()
        print(bearing)
        bearing = dataclean(bearing)
        bearing = (str(bearing, "utf-8"))
        bearing = int(bearing)
        #Calculate input to PID
        PIDerror =error(bearing, target)
        #Get output of PID
        Motordiff = pid(PIDerror)

        #Calculate PWM signal needed to send to motors
        speedspecial = abs(normalize(Motordiff))+7.5
        speedspecial = maxbound(speedspecial)
        #If close enough to bearing, start driving forward instead of spot turning
        if abs(error(bearing, target))<100:
          if(normalize(Motordiff)>0):
            PWM.set_duty_cycle(left, speed)
            PWM.set_duty_cycle(right, -speedspecial+speed+7.5)
            message = 'Drive Forward slight Right          '
            messageR= 'Right Motor: ' +str( -speedspecial+speed+7.5)
            messageL= 'Left Motor: ' + str(speed)
            time.sleep(secs)
          else:
            PWM.set_duty_cycle(right, speed)
            PWM.set_duty_cycle(left, -speedspecial+speed+7.5)
            message = 'Drive Forward slight Left          '
            messageR= 'Right Motor: ' +str(speed)
            messageL= 'Left Motor: ' + str(-speedspecial+speed+7.5)
            time.sleep(secs)
        #Spot turning
        elif (normalize(Motordiff)>0):
        #If positive turn right
          speedspecial = minbound(speedspecial)  
          PWM.set_duty_cycle(left, speedspecial)
          PWM.set_duty_cycle(right, rest)
          message = 'Drive Right                          ' 
          messageR= 'Right Motor: ' +str(rest)
          messageL= 'Left Motor: ' + str(speedspecial)         
          time.sleep(secs)
        else:
          speedspecial = minbound(speedspecial)
          PWM.set_duty_cycle(right, speedspecial)
          PWM.set_duty_cycle(left, rest)
          message = 'Drive Left                      '          
          time.sleep(secs)
          messageR= 'Right Motor: ' +str(speedspecial)
          messageL= 'Left Motor: ' + str(rest)
        print(speedspecial)
        #Send data to controller
        serComm.write((str(speedspecial)+"             ,"+str(bearing)+"             ,"+ str(Motordiff)+"            ,"+messageL+"        ,"+ messageR+"      ,"+message).encode())       
        serMag.reset_input_buffer()
    elif letter == b't': 
      #speed 1
      speed = 8.3
      serComm.reset_input_buffer()
      print("t")
    elif letter == b'y': 
      #speed 2
      speed = 9
      serComm.reset_input_buffer()
      print("y")
    elif letter == b'u': 
      #speed 3
      speed = 10
      serComm.reset_input_buffer()
      print("u")
    elif letter == b'a': 
      #turn left by throttling right
      PWM.set_duty_cycle(right, speed)
      PWM.set_duty_cycle(left, rest)
      time.sleep(secs)
      serComm.reset_input_buffer()
      print("a")
    elif letter == b's': 
      #Go backwards
      PWM.set_duty_cycle(left, 15-speed)
      PWM.set_duty_cycle(right, 15-speed)
      time.sleep(secs)
      serComm.reset_input_buffer()
      print("s")
    elif letter == b'd': 
      #turn right by throttling left
      PWM.set_duty_cycle(left, speed)
      PWM.set_duty_cycle(right, rest)
      time.sleep(secs)
      serComm.reset_input_buffer()
      print("d")
    elif letter == b'w': 
      #Go forwrd
      PWM.set_duty_cycle(right, speed)
      PWM.set_duty_cycle(left, speed)
      time.sleep(secs)
      serComm.reset_input_buffer()
      print("w")

      #Toggle the servo
    elif  letter == b'z' or letter == b'c':
      if servoToggle == True:
        PWM.start(servo, righttoggle, 50, 0)
        servoToggle = False
        print("Flip Left")
      else:
        PWM.start(servo, lefttoggle, 50, 0)
        servoToggle = True
        print("Flip Right")
    else:
      PWM.set_duty_cycle(left, rest)
      PWM.set_duty_cycle(right, rest)
      print("rest")
#If there's an error shut off motors and print the error
except:
  PWM.start(left, rest, 50, 0)
  PWM.start(right, rest, 50, 0)
  print(error_handling())



