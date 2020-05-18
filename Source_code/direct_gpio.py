from migen import *
from litex.boards.platforms.arty import *

class Blinky(Module):
    def __init__(self, platform, maxperiod):
        #in order to use the gpio pins we need to first request our device
        self.gpio = gpio = platform.request("gpio")
        
        counter = Signal(max=maxperiod+1)
        period = Signal(max=maxperiod+1)
        self.comb += period.eq(maxperiod)
        self.sync += If(counter == 0,
                        #then access the signals it provides using this syntax
                        gpio.pin0.eq(~gpio.pin0),
                        gpio.pin1.eq(~gpio.pin0),
                        counter.eq(period)
        ).Else(
            counter.eq(counter -1)
        )

#------------------------------------------------------

#this part is standard; we define a platform class
plat = Platform()

#now, in order to use gpio pins that are not defined in the _io table,
#but in the _connector table, we need to write our own device to use them
gpio_device= [
    ("gpio", 0,
    Subsignal("pin0", Pins("ck_io:ck_io0")),
     Subsignal("pin1", Pins("ck_io:ck_io1")),
     IOStandard("LVCMOS33")
    )
]
#all the pin definitions are located in the 'litex-boards/litex_boards/platforms/arty.py' file

#now we need to add our device to the platform
plat.add_extension(gpio_device)

blinky = Blinky(plat, 100000000)
plat.build(blinky)
