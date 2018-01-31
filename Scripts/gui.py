import sys

if(sys.version_info[0]<3):
    from Tkinter import *
else:
    from tkinter import *
    
import RPi.GPIO as pi
import math
#import tkSimpleDialog

class LED(Frame):
    """A Tkinter LED Widget.
    a = LED(root,10)
    a.set(True)
    current_state = a.get()"""
    OFF_STATE = 0
    ON_STATE = 1
    
    def __init__(self,master, gpi = 0, size=20,**kw):
        self.gpi = gpi
        self.size = size
        Frame.__init__(self,master,width=size,height=size)
        self.configure(**kw)
        self.state = LED.OFF_STATE
        self.c = Canvas(self,width=self['width'],height=self['height'])
        self.c.grid()
        self.led = self._drawcircle((self.size/2)+1,(self.size/2)+1,(self.size-1)/2)
    def _drawcircle(self,x,y,rad):
        """Draws the circle initially"""
        if(self.gpi >0):
            color="blue"
        elif(self.gpi == -1 or self.gpi == -2):
            color = "yellow"
        elif(self.gpi == -3 or self.gpi == -5):
            color = "red"
        else:
            color = "black"
        return self.c.create_oval(x-rad,y-rad,x+rad,y+rad,width=rad/5,fill=color,outline='black')
    def _change_color(self):
        """Updates the LED colour"""
        if (self.state == LED.ON_STATE and self.gpi >0):
            color="green"
        elif(self.state ==LED.OFF_STATE and self.gpi> 0):
            color="blue"
        elif(self.gpi == -1 or self.gpi == -2):
            color = "yellow"
        elif(self.gpi == -3 or self.gpi == -5):
            color = "red"
        else:
            color = "black"
        self.c.itemconfig(self.led, fill=color)
    def set(self,state):
        """Set the state of the LED to be True or False"""
        self.state = state
        self._change_color()
    def get(self):
        """Returns the current state of the LED"""
        return self.state

## Future Functionality
##class gpioEdit(tkSimpleDialog.Dialog):
##    """Dialog to be expanded to support advanced gpio features like
##       - Pull Up / Pull Down Resistor Config
##       - Debounce"""
##    def __init__(self, master,gpio):
##        top = self.top = Toplevel(master)
##        if gpio.isInput():
##            title = "Edit Input: %s" %(str(gpio.name))
##        else:
##            title = "Edit Output: %s" %(str(gpio.name))
##        l = Label(top,text=title)
##        b = Button(top, text="Submit", command=self.submit)
##
##        l.grid(row=0)
##        b.grid(row=1)
##
##    def submit(self):
##        print("Submitted")
##        self.top.destroy()



class GPIO(Frame):
    """Each GPIO class draws a Tkinter frame containing:
    - A Label to show the GPIO Port Name
    - A data direction spin box to select pin as input or output
    - A checkbox to set an output pin on or off
    - An LED widget to show the pin's current state
    - A Label to indicate the GPIOs current function"""
    gpio_modes = ("Passive","Input","Output")
    
    def __init__(self,parent,pin=0,name=None,gpi = 0,  cl = 0,**kw):
        self.pin = pin
        self.gpi = gpi
        if name == None:
            if (self.gpi > 0):
                self.name = "   Pin %02d(GPIO %02d)  " %(self.pin, self.gpi)
            else:
                self.name = "          PIN %02d         " % (self.pin)
        Frame.__init__(self,parent,width = 50,height=20,relief=SUNKEN, bd=1)
        self.parent = parent
        self.configure(**kw)
        self.state = False
        self.cmdState = IntVar()
        self.Label = Label(self,text=self.name)
        if(gpi >0):
            self.mode_sel = Spinbox(self,values=self.gpio_modes,wrap=True,command=self.setMode)
            self.set_state = Checkbutton(self,text="HIGH/LOW",variable=self.cmdState,command=self.toggleCmdState)
        elif(gpi ==-3):
            self.mode_sel = Spinbox(self, values = "Power_3V3", wrap = True)
            self.set_state = Checkbutton(self,text="                ",variable=self.cmdState)
        elif(gpi == -5):
            self.mode_sel = Spinbox(self, values = "Power_5V", wrap = True)
            self.set_state = Checkbutton(self,text="                ",variable=self.cmdState)
        elif(gpi == -1):
            self.mode_sel = Spinbox(self, values = "ID_SD", wrap = True)
            self.set_state = Checkbutton(self,text="HIGH/LOW",variable=self.cmdState)
        elif(gpi == -2):
            self.mode_sel = Spinbox(self, values = "ID_SC", wrap = True)
            self.set_state = Checkbutton(self,text="HIGH/LOW",variable=self.cmdState)
        else:
            self.mode_sel = Spinbox(self, values = "Ground", wrap = True)
            self.set_state = Checkbutton(self,text="                ",variable=self.cmdState)
        
        self.led = LED(self, gpi ,20)
        if cl == 0:
            self.Label.grid(column=0,row=0)
            self.mode_sel.grid(column=1,row=0)
            self.set_state.grid(column=2,row=0)
            self.led.grid(column=3,row=0)
        else:
            self.Label.grid(column=1,row=0)
            self.mode_sel.grid(column=2,row=0)
            self.set_state.grid(column=3,row=0)
            self.led.grid(column = 0, row = 0)
        self.current_mode = StringVar()
        self.set_state.config(state=DISABLED)
        function = self.getPinFunctionName()
        if function not in ['Input','Output', 'Unknown']:
            self.mode_sel.delete(0,'end')
            self.mode_sel.insert(0,function)
            self.mode_sel['state'] = DISABLED
            

    def isInput(self):
        """Returns True if the current pin is an input"""
        return (self.mode_sel.get() == "Input")

    def setMode(self):
        """Sets the GPIO port to be either an input or output
            Depending on the value in the spinbox, doesn't work for non-gpio"""
        if(self.gpi >0):
            if (self.mode_sel.get() == "Input"):
                self.set_state.config(state=DISABLED)
                pi.setup(self.gpi,pi.IN)
            elif (self.mode_sel.get() == "Passive"):
                self.set_state.config(state=DISABLED)
                pi.cleanup(self.gpi)
            else:
                self.set_state.config(state=NORMAL)
                pi.setup(self.gpi,pi.OUT)
                self.updateInput()

    def getPinFunctionName(self):
            pin = self.pin
            functions = {pi.IN:'Input',
                         pi.OUT:'Output',
                         pi.I2C:'I2C',
                         pi.SPI:'SPI',
                         pi.HARD_PWM:'HARD_PWM',
                         pi.SERIAL:'Serial',
                         pi.UNKNOWN:'Unknown'}                     
            return functions[pi.gpio_function(pin)]
 

    def toggleCmdState(self):
        """Reads the current state of the checkbox, updates LED widget
        and sets the gpio port state."""
        if(self.gpi > 0):
            self.state = self.cmdState.get()
            self.updateLED()
            self.updatePin()

    def updatePin(self):
        """Sets the GPIO port state to the current state"""
        if(self.gpi > 0):
            pi.output(self.gpi,self.state)

    def updateLED(self):
        """Refreshes the LED widget depending on the current state"""
        self.led.set(self.state)

    def updateInput(self):
        """Updates the current state if the pin is an input and sets the LED"""
        if self.isInput():
            state = pi.input(self.gpi)
            self.state = state
            self.updateLED()
        

class App(Frame):
    def __init__(self,parent=None, **kw):
        Frame.__init__(self,parent,**kw)
        self.parent = parent
        pi.setmode(pi.BCM)
        self.ports = []
        ## Get the RPI Hardware dependant list of GPIO
        gpio = self.getRPIVersionGPIO()
        for num,(gp,r,c,p) in enumerate(gpio):
                self.ports.append(GPIO(self,pin=p, gpi = gp, cl = c))
                self.ports[-1].grid(row=r,column=c)
        self.confirm = Button(self, text = "Confirm", command = self.update, width = 20, height = 5, padx = 5)
        self.confirm.grid(row =21, column = 0)
        self.verify = Button(self, text = "Verify",command = self.verification, width = 20, height = 5, padx = 5)
        self.verify.grid(row =21, column = 1)
        #self.update()
        print("initialized.")

        
    def verification(self):
        counter = 0
        for elements in self.ports:
            
            print(counter)
    def onClose(self):
        """This is used to run the Rpi.GPIO cleanup() method to return pins to be an input
        and then destory the app and its parent."""
        try:
            pi.cleanup()
        except RuntimeWarning as e:
            print(e)
        self.destroy()
        self.parent.destroy()

    def readStates(self):
        """Cycles through the assigned ports and updates them based on the GPIO input"""
        for port in self.ports:
            port.updateInput()
                    
    def update(self):
        
        """Runs to update the state of the GPIO inputs"""
        self.readStates()
        
    def getRPIVersionGPIO(self):
        """Returns the GPIO hardware config for different Pi versions
           Currently supports layout 3"""
        gpio1 = ((0,0,0,0),
                (1,1,0,0),
                (4,2,0,0),
                (17,3,0,0),
                (21,4,0,0),
                (22,5,0,0),
                (10,6,0,0),
                (9,7,0,0),
                (11,8,0,0),
                (14,0,1,0),
                (15,1,1,0),
                (18,2,1,0),
                (23,3,1,0),
                (24,4,1,0),
                (25,5,1,0),
                (8,6,1,0),
                (7,7,1,0))
        gpio2 = ((2,0,0),
                (3,1,0),
                (4,2,0),
                (17,3,0),
                (27,4,0),
                (22,5,0),
                (10,6,0),
                (9,7,0),
                (11,8,0),
                (14,0,1),
                (15,1,1),
                (18,2,1),
                (23,3,1),
                (24,4,1),
                (25,5,1),
                (8,6,1),
                (7,7,1))
        #(gp,r,c,p)
        gpio3 = ((-3,0,0,1),
                (-5,0,1,2),
                (2,1,0,3),
                (-5,1,1,4),
                (3,2,0,5),
                (0,2,1,6),
                (4,3,0,7),
                (14,3,1,8),
                (0,4,0,9),
                (15,4,1,10),
                (17,5,0,11),
                (18,5,1,12),
                (27,6,0,13),
                (0,6,1,14),
                (22,7,0,15),
                (23,7,1,16),
                (-3,8,0,17),
                (24,8,1,18),
                (10,9,0,19),
                (0,9,1,20),
                (9,10,0,21),
                (25,10,1,22),
                (11,11,0,23),
                (8,11,1,24),
                (0,12,0,25),
                (7,12,1,26),
                (-1,13,0,27),
                (-2,13,1,28),
                (5,14,0,29),
                (0,14,1,30),
                (6,15,0,31),
                (12,15,1,32),
                (13,16,0,33),
                (0,16,1,34),
                (19,17,0,35),
                (16,17,1,36),
                (26,18,0,37),
                (20,18,1,38),
                (0,19,0,39),
                (21,19,1,40))
        if pi.RPI_REVISION == 3:
            gpio = gpio3
            self.parent.title('Raspberry Pi GPIO - A+/B+/2B+/3')
        elif pi.RPI_REVISION == 2:
            gpio = gpio2
            self.parent.title('Raspberry Pi GPIO - A/B Rev2')
        elif pi.RPI_REVISION == 1:
            self.parent.title('Raspberry Pi GPIO - A/B')
            gpio = gpio1
        else:
            self.parent.title('Raspberry Pi GPIO - Unknown Version')
            ##Assume same config as A+/B+/2B+
            gpio = gpio3
        return gpio
        
def main():
    root = Tk()
    root.title("Raspberry Pi GPIO")
    a = App(root)
    a.grid()
    """When the window is closed, run the onClose function."""
    root.protocol("WM_DELETE_WINDOW",a.onClose)
    #root.resizable(False,False)
    root.mainloop()
   

if __name__ == '__main__':
    main()
