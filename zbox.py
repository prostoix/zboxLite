#########################################
# MISC
#########################################
from subprocess import call
import time

#########################################
# GPIO
#########################################
from pyA20.gpio import gpio
from pyA20.gpio import connector
from pyA20.gpio import port

button_up   = connector.gpio1p11
button_ok   = connector.gpio1p13
button_down = connector.gpio1p15

gpio.init()
gpio.setcfg(button_up,   gpio.INPUT)
gpio.setcfg(button_down, gpio.INPUT)
gpio.setcfg(button_ok,   gpio.INPUT)
gpio.pullup(button_up,   gpio.PULLUP)
gpio.pullup(button_down, gpio.PULLUP)
gpio.pullup(button_ok,   gpio.PULLUP)

from pyA20.gpio import gpio
from pyA20.gpio import connector
from pyA20.gpio import port

lastbuttontime = 0



#########################################
# OLED
#########################################
import smbus
from ssd1306 import SSD1306_Display
from PIL import Image, ImageDraw, ImageFont
font0 = ImageFont.truetype(font="lsansd.ttf", size=12, index=0, encoding='')
font1 = ImageFont.truetype(font="lsans.ttf" , size=12, index=0, encoding='')
font2 = ImageFont.truetype(font="lsans.ttf" , size=10, index=0, encoding='')
dis = SSD1306_Display(0)
dis.initDisplay()


def display(t1,t2,t3,t4,t5):
	i = Image.new("1", (128,64))
	d = ImageDraw.Draw(i, mode="1")

	d.rectangle((0,(4*12)+1,127,(4*12)+12), fill=1, outline=1)

	d.text((0, 0), t1, fill=1, font=font0)
	d.text((0,12), t2, fill=1, font=font1)
	d.text((0,24), t3, fill=1, font=font1)
	d.text((0,36), t4, fill=1, font=font2)
	d.text((0,48), t5, fill=0, font=font0)
	dis.writeBuffer(dis.img2buffer(i.getdata()))
	dis.displayBuffer()
	time.sleep(0.002)

mymenu = ["Select Soundfont",
	  "Select Preset",
	  "Back",
	  "",
	  "Power off"]

def displaymenu():
	global myoption

	optionselected=[1,1,1,1,1]
	optionselected[myoption]=0

	i = Image.new("1", (128,64))
	d = ImageDraw.Draw(i, mode="1")

	d.rectangle((0,(myoption*12)+1,127,(myoption*12)+12), fill=1, outline=1)

	d.text((0,0) , mymenu[0], fill=optionselected[0], font=font0)
	d.text((0,12), mymenu[1], fill=optionselected[1], font=font0)
	d.text((0,24), mymenu[2], fill=optionselected[2], font=font0)
	d.text((0,36), mymenu[3], fill=optionselected[3], font=font0)
	d.text((0,48), mymenu[4], fill=optionselected[4], font=font0)


	dis.writeBuffer(dis.img2buffer(i.getdata()))
	dis.displayBuffer()
	time.sleep(0.002)





#########################################
# Files
#########################################
	
import glob
import os

os.chdir("sf2")
lista_sf2=sorted(glob.glob("*.sf2"))
max_options=len(lista_sf2)-1

myoption=0
mysf2=0
# Mode types: 1-SoundFont, 2-Preset
mymode=1 
menumode=False
text_mode=["Menu","SoundFont","Preset"]
max_mode=2
txt_preset=""
lista_presets=""

mymenu_select=0




#########################################
# Fluidsynth and Audio Engine
#########################################
import fluidsynth

from pyalsa.alsaseq import *

# Start the midi alsa-Seq to connect ports.
sequencer = Sequencer(name='default',
                      clientname='aconnect.py',
                      streams=SEQ_OPEN_DUPLEX,
                      mode=SEQ_BLOCK)

# Create and start the synthesizer with the selected options.
fs = fluidsynth.Synth(gain=0.1, polyphony=96, channels=16)
fs.start()
fs.start_midi()  # Default is alsa_seq

# Test the get_gain and set a new gain:
print "Current gain: " + str(fs.get_gain())
fs.set_gain(0.3)
print "Updated gain: " + str(fs.get_gain())

global sfid
sfid=0

preset = 0
bank = 0
channel = 0

connectionlist = sequencer.connection_list()
exclusive = 0
convert_time = 0
convert_real = 0
queue = 0

# Print port list
print "Port list:"
for el in connectionlist:
    print el

# Locate Fluidsynth and set the destination port.
for el in connectionlist:
    if 'FLUID' in el[0]:
        dest = (el[1], 0)
        print 'Connected to ' + el[0]

# Locate USB MIDI IN and set the sender port.
for el in connectionlist:
    if 'System' not in el[0]:
        if 'FLUID' not in el[0]:
            if 'aconnect' not in el[0]:
                sender= (el[1], 0)
                print 'Connected to ' + el[0]
                break


sequencer.connect_ports(sender, dest, queue, exclusive, convert_time, convert_real)


#########################################
# Funcs
#########################################
now=0
skipload=False
max_preset=0

def load_action():
	global sfid, preset, bank, mymode, menumode, myoption, mysf2, max_options, txt_preset
	global lastbuttontime, now, skipload, max_preset

        lastbuttontime = now

        if myoption>max_options:
	    myoption=0
        if myoption<0:
	    myoption=max_options

	if menumode:
	    displaymenu()
	    return

	elif mymode==1:
	    mysf2=myoption
	    if len(lista_sf2)!=0:
		    display(str(mysf2)+" Loading...",lista_sf2[mysf2],"","","")
	    else:
		    skipload=True
	    if not skipload:
	        preset=0
	        if sfid > 0:
		    fs.sfunload(sfid)
		sfid = fs.sfload(lista_sf2[mysf2])
	        fs.program_select(channel, sfid, bank, 0)
	    skipload=False
	    if sfid>0:
		    if len(lista_sf2)>0:
		        inst = fs.get_instrument_list(sfid,lista_sf2[mysf2])
		        if len(inst) >0:
			        txt_preset=inst[str(bank).zfill(3) + '-' + str(preset).zfill(3)]
		        max_preset=len(inst)-2
		    else:
		        inst=0
		        txt_preset="VOID"
		        max_preset=0
	    else:
		    max_preset=0
		    txt_preset="VOID"
		    inst=0




	    if max_preset<0:
		max_preset=0
	    if max_preset>127:
		max_preset=127
	    txt_menu="Select SoundFont"

	elif mymode==2:
	    preset=myoption
	    inst = fs.get_instrument_list(sfid,lista_sf2[mysf2])
	    txt_preset=inst[str(bank).zfill(3) + '-' + str(preset).zfill(3)]
	    txt_menu="Select Preset"
	    fs.program_select(channel, sfid, bank, preset)

        if len(lista_sf2)!=0:
		display(str(mysf2)+" Ready.",lista_sf2[mysf2],txt_preset,txt_menu," <<<     MENU    >>> ")
	else:
		display(str(mysf2)+" Not Ready.","VOID",txt_preset,txt_menu," <<<     MENU    >>> ")

display("OK","","","","")
load_action() # Load first SF2 file on folder

print "Let's go"

#########################################
# Loop
#########################################

while True:
    now = time.time()

    if not gpio.input(button_down) and (now - lastbuttontime) > 0.3:
	    myoption=myoption-1
	    load_action()

    elif not gpio.input(button_up) and (now - lastbuttontime) > 0.3:
	    myoption=myoption+1
	    load_action()

    elif not gpio.input(button_ok) and (now - lastbuttontime) > 0.3:
	    lastbuttontime = now
	    if menumode:
		menumode=False
	        if myoption==0:
		    mymode=1
		    myoption=mysf2
		    max_options=len(lista_sf2)-1
		    skipload=True
		    load_action()

	        elif myoption==1:
		    mymode=2
		    myoption=preset
		    load_action()
		    max_options=max_preset

	        elif myoption==2:

		    if mymode==1:
		        myoption=mysf2
		        max_options=len(lista_sf2)-1
		        skipload=True
		        load_action()
		    elif mymode==2:
			myoptions=preset	
			max_options=max_preset
		        load_action()

	        elif myoption==4:
	    	    display("","","","","")
		    break
	    else:
	        menumode=True
	        max_options=len(mymenu)-1
	        myoption=0
	        displaymenu()



print "stopping..."
fs.stop_midi()
fs.delete()
display("Please wait.","Closing system...","","","")
call("sudo poweroff", shell=True)

