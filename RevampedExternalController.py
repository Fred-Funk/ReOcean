#Importing relevant libraries
import curses
import serial
import time

secs= 0.15 #timeout before sending null
#Initialize Serial object
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM28'
ser.open()
ser.timeout= secs

# get the curses screen window
screen = curses.initscr()
screen.timeout(0)
# turn off input echoing
curses.noecho()
 
# respond to keys immediately (don't wait for enter)
curses.cbreak()
 
# map arrow keys to special values
screen.keypad(True)

#Automatic Control
def Autocontrol(screen, serial):
    #Start a counter
    counter =0
    #Get character read from screen
    while True:
        char = screen.getch()
        #Send kill signal if p is pressed
        if char == ord('p'):
            ser.write(b'p')
            return "quit"
        #Just quit if 0 is pressed
        elif char == ord('0'):
            return "quit"
        elif char == ord('2'): 
            #Turn to manual control
            ser.write(b'2')
            screen.addstr(0, 0, 'Manual     ')        
            return "manual"
        #Information retrieval
        try:
            counter+=1
            #Convert byte to string
            line= ser.readline().decode()
            line= line.split(',')
            #Erase the screen every 100 times
            if counter%100 == 0:
                screen.erase()
            screen.addstr(0, 0, 'Auto     ')                 
            screen.addstr(1, 0, line[0])
            screen.addstr(2, 0, line[1])
            screen.addstr(3, 0, line[2])
            screen.addstr(4, 0, line[3])       
            screen.addstr(5, 0, line[4])
            screen.addstr(6, 0, line[5])
        except:
            pass

#Manual control
def Remotecontrol(screen, ser):
    while True:
        #Send kill signal if p ispressed
        char = screen.getch()
        if char == ord('p'):
            ser.write(b'p')
            return "quit"
         #Just quit if 0 is pressed    
        elif char == ord('0'):
            return "quit"            
        elif char == ord('1'): 
            #speed 1
            ser.write(b'1')
            screen.addstr(0, 0, 'Auto     ')
            return "auto"            
         elif char == ord('t'): 
            #speed 1
            ser.write(b't')
            screen.addstr(0, 0, 'speed 1     ')
            #speed 2
        elif char == ord('y'):
            ser.write(b'y')
            screen.addstr(0, 0, 'speed 2     ')
        elif char == ord('u'):
            #speed 3
            ser.write(b'u')
            screen.addstr(0, 0, 'speed 3      ')
        elif char == curses.KEY_RIGHT:
            screen.addstr(0, 0, 'right      ')
            ser.write(b'l')
        elif char == curses.KEY_LEFT:
            screen.addstr(0, 0, 'left      ')
            ser.write(b'j')       
        elif char == curses.KEY_UP:
            screen.addstr(0, 0, 'up      ')
            ser.write(b'i')
        elif char == curses.KEY_DOWN:
            screen.addstr(0, 0, 'down ')
            ser.write(b'k')
        elif char == ord('b'): 
            #speed 1
            ser.write(b'b')
            screen.addstr(0, 0, 'speed 1     ')
        elif char == ord('n'):
            #speed 2
            ser.write(b'n')
            screen.addstr(0, 0, 'speed 2     ')
        elif char == ord('m'):
            #speed 3
            ser.write(b'm')
            screen.addstr(0, 0, 'speed 3      ')
        elif char == ord('a'):
            ser.write(b'a')
            screen.addstr(0, 0, 'left     ')
        elif char == ord('d'):
            ser.write(b'd')
            screen.addstr(0, 0, 'right     ')
        elif char == ord('s'):
            ser.write(b's')
            screen.addstr(0, 0, 'down     ')
        elif char == ord('w'):
            ser.write(b'w')
            screen.addstr(0, 0, 'up     ')
        #Flip the left servo
        elif char == ord('z'):
            ser.write(b'z')
            screen.addstr(0, 0, 'L toggle     ')
        #Flip the right servo
        elif char == ord('x'):
            ser.write(b'x')
            screen.addstr(0, 0, 'R toggle     ')
        #Flip both servos
        elif char == ord('c'):
            ser.write(b'c')
            screen.addstr(0, 0, 'B toggle     ')
try:
    while True:
        if (Remotecontrol(screen, ser) == 'quit'):
            break
        if (Autocontrol(screen, ser) == 'quit'):
            break
 

finally:
    # shut down cleanly
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()