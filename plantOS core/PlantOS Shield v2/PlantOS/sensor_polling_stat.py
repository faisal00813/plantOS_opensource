#!/usr/bin/python

import io         # used to create file streams
import fcntl      # used to access I2C parameters like addresses
import time       # used for sleep delay and timestamps
import string     # helps parse strings
import smbus
import Adafruit_DHT
import numpy

#
#   Atlas Scientific
#

class AtlasI2C:
    long_timeout = 1.5         	# the timeout needed to query readings and calibrations
    short_timeout = 0.5         	# timeout for regular commands
    default_bus = 1         	# the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
    default_address = 99     	# the default address for the sensor
    current_addr = default_address
        
    def __init__(self, address=default_address, bus=default_bus):
        # open two file streams, one for reading and one for writing
        # the specific I2C channel is selected with bus
        # it is usually 1, except for older revisions where its 0
        # wb and rb indicate binary read and write
        self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)
                
        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)
    
    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self.current_addr = addr
        
    def write(self, cmd):
        # appends the null character and sends the string over I2C
        cmd += "\00"
        self.file_write.write(cmd)
        
    def read(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C, then parses and displays the result
        res = self.file_read.read(num_of_bytes)         # read from the board
        response = filter(lambda x: x != '\x00', res)     # remove the null characters to get the response
        if ord(response[0]) == 1:             # if the response isn't an error
            # change MSB to 0 for all received characters except the first and get a list of characters
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            # NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
            if self.current_addr == 99: # pH sensor
                return "pH: " + ''.join(char_list)     # convert the char list to a string and returns it
            elif self.current_addr == 100: # EC sensor
                temp_string=''.join(char_list)
                #print 'EC: ' + string.split(temp_string, ",")[0]
                #print 'TDS: ' + string.split(temp_string, ",")[1]
                #print 'Salinity: ' + string.split(temp_string, ",")[2]
                #return "Gravity: " + string.split(temp_string, ",")[3]     # convert the char list to a string and returns it
                return "EC: " + string.split(temp_string, ",")[0] + "\nTDS: " + string.split(temp_string, ",")[1] + "\nSalinity: " + string.split(temp_string, ",")[2] + "\nGravity: " + string.split(temp_string, ",")[3]     # convert the char list to a string and returns it
            elif self.current_addr == 102: # RTD sensor
                return "Soluble Temperature: " + ''.join(char_list) + " C"     # convert the char list to a string and returns it
        else:
            return "Error " + str(ord(response[0]))
    
    def query(self, string):
        # write a command to the board, wait the correct timeout, and read the response
        self.write(string)
            
        # the read and calibration commands require a longer timeout
        if((string.upper().startswith("R")) or
            (string.upper().startswith("CAL"))):
            time.sleep(self.long_timeout)
        elif string.upper().startswith("SLEEP"):
            return "sleep mode"
        else:
            time.sleep(self.short_timeout)
                
        return self.read()
        
    def close(self):
        self.file_read.close()
        self.file_write.close()
        
    def list_i2c_devices(self):
        prev_addr = self.current_addr # save the current address so we can restore it after
        i2c_devices = []
        for i in range (0,128):
            try:
                self.set_i2c_address(i)
                self.read()
                i2c_devices.append(i)
            except IOError:
                pass
        self.set_i2c_address(prev_addr) # restore the address we were using
        return i2c_devices

#
#   BH1750
#

class BH1750():
    # define constants
    default_address = 0x23              # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
    default_bus = 1                     # the default address for the sensor
    POWER_DOWN = 0x00                   # No active state
    POWER_ON = 0x01                     # Power on
    RESET = 0x07                        # Reset data register value
    CONTINUOUS_LOW_RES_MODE = 0x13      # Start measurement at 4lx resolution. Time typically 16ms
    CONTINUOUS_HIGH_RES_MODE_1 = 0x10   # Start measurement at 1lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11   # Start measurement at 0.5lx resolution. Time typically 120ms
    ONE_TIME_HIGH_RES_MODE_1 = 0x20     # Start measurement at 1lx resolution. Time typically 120ms. Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_2 = 0x21     # Start measurement at 0.5lx resolution. Time typically 120ms. Device is automatically set to Power Down after measurement.
    ONE_TIME_LOW_RES_MODE = 0x23        # Start measurement at 1lx resolution. Time typically 120ms. Device is automatically set to Power Down after measurement.
    
    def __init__(self):
        self.bus = smbus.SMBus(1)
    
    def convertToNumber(self, data):
        return ((data[1]+(256*data[0]))/1.2)

    def readLight(self, addr=default_address):
        data=self.bus.read_i2c_block_data(addr,self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convertToNumber(data)

#
#   Main
#


def main():
    # Sensor Objects Definition
    device = AtlasI2C()             # Atlas Scientific sensors (ph,ec, rtd)
    device1 = BH1750()              # BH1750 light sensor
    device2 = Adafruit_DHT.DHT22    # DHT22 temperature and humidity sensor
    pin = 24                        # DHT22 data pin
    gcp_timer = 1 * 60              # 5 minutes for GCP Pub/Sub
    poll_timer = 10                 # 10 seconds per sensor reading
    
    
    # initialize sensors (remove first light intensity error)
    device1.readLight()
    humidity, temperature = Adafruit_DHT.read_retry(device2, pin)
    stat_dht22_temp = [float(temperature)] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    stat_dht22_humid = [float(humidity)] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    
    device.set_i2c_address(99)  # (99 pH)
    temp = device.query("R")
    stat_atlas_ph = [float(string.split(temp, ": ")[1])] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    device.set_i2c_address(100) # (100 EC)
    temp = device.query("R")
    temp1 = string.split(temp, ": ")[1] #EC
    stat_atlas_ec = [float(string.split(temp1, "\n")[0])] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    temp1 = string.split(temp, ": ")[2] #TDS
    stat_atlas_tds = [float(string.split(temp1, "\n")[0])] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    temp1 = string.split(temp, ": ")[3] #Salinity
    stat_atlas_sal = [float(string.split(temp1, "\n")[0])] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    temp1 = string.split(temp, ": ")[4] #Gravity
    stat_atlas_gra = [float(string.split(temp1, "\n")[0])] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    device.set_i2c_address(102) # (102 RTD)
    temp = device.query("R")
    temp = string.split(temp, ": ")[1]
    stat_atlas_rtd = [float(string.split(temp, " C")[0])] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    stat_bh1750_lux = [float(str(device1.readLight()))] * ((gcp_timer/poll_timer)-1) # initialize local statistic
    
    # set up numpy arrays
    stat_dht22_temp = numpy.array(stat_dht22_temp)
    stat_dht22_humid = numpy.array(stat_dht22_humid)
    stat_atlas_ph = numpy.array(stat_atlas_ph)
    stat_atlas_ec = numpy.array(stat_atlas_ec)
    stat_atlas_tds = numpy.array(stat_atlas_tds)
    stat_atlas_sal = numpy.array(stat_atlas_sal)
    stat_atlas_gra = numpy.array(stat_atlas_gra)
    stat_atlas_rtd = numpy.array(stat_atlas_rtd)
    stat_bh1750_lux = numpy.array(stat_bh1750_lux)
    
    # main loop
    while True:
        input = raw_input("Enter command: ")
                
        if input.upper().startswith("LIST_ADDR"):
            devices = device.list_i2c_devices() # obtain I2C devices address that are connected to the shield
            for i in range(len (devices)):
                print devices[i]
                
        # continuous polling command automatically polls the board
        elif input.upper().startswith("POLL"):
            # Setup sensor polling timer and GCP PubSub timer
            poll_time = time.time()
            gcp_time = time.time()
            try:
                while True:
                    # Sensor Polling Task
                    if (time.time() - poll_time) >= poll_timer:
                        # reset sensor poll timer
                        poll_time = time.time()
                        humidity = None
                        temperature = None
                        humidity, temperature = Adafruit_DHT.read_retry(device2, pin) # DHT22
                        if humidity is not None and temperature is not None:
                            print('Ambient Temperature: {0:0.1f} C  \nAmbient Humidity: {1:0.1f} %'.format(temperature, humidity))
                            stat_dht22_temp = numpy.append(stat_dht22_temp, float(temperature)) #local statistic
                            stat_dht22_humid = numpy.append(stat_dht22_humid, float(humidity)) #local statistic
                        else:
                            stat_dht22_temp = numpy.median(stat_dht22_temp)
                            stat_dht22_humid = numpy.median(stat_dht22_humid)
                        
                        device.set_i2c_address(99)  # (99 pH)
                        temp = device.query("R")
                        print(temp)
                        stat_temporary = None
                        stat_temporary = numpy.append(stat_atlas_ph, float(string.split(temp, ": ")[1]))    #local statistic
                        if stat_temporary is not None:
                            stat_atlas_ph = stat_temporary
                        else:
                            stat_atlas_ph = numpy.median(stat_atlas_ph)
                        device.set_i2c_address(100) # (100 EC)
                        temp = device.query("R")
                        print(temp)
                        temp1 = string.split(temp, ": ")[1] #get EC
                        stat_temporary = None
                        stat_temporary = numpy.append(stat_atlas_ec, float(string.split(temp1, "\n")[0])) #local statistic
                        if stat_temporary is not None:
                            stat_atlas_ec = stat_temporary
                        else:
                            stat_atlas_ec = numpy.median(stat_atlas_ec)
                        temp1 = string.split(temp, ": ")[2] #get TDS
                        stat_temporary = None
                        stat_temporary = numpy.append(stat_atlas_tds, float(string.split(temp1, "\n")[0])) #local statistic
                        if stat_temporary is not None:
                            stat_atlas_tds = stat_temporary
                        else:
                            stat_atlas_tds = numpy.median(stat_atlas_tds)
                        temp1 = string.split(temp, ": ")[3] #get Salinity
                        stat_temporary = None
                        stat_temporary = numpy.append(stat_atlas_sal, float(string.split(temp1, "\n")[0])) #local statistic
                        if stat_temporary is not None:
                            stat_atlas_sal = stat_temporary
                        else:
                            stat_atlas_sal = numpy.median(stat_atlas_sal)
                        temp1 = string.split(temp, ": ")[4] #get Gravity
                        stat_temporary = None
                        stat_temporary = numpy.append(stat_atlas_gra, float(string.split(temp1, "\n")[0])) #local statistic
                        if stat_temporary is not None:
                            stat_atlas_gra = stat_temporary
                        else:
                            stat_atlas_gra = numpy.median(stat_atlas_gra)
                        device.set_i2c_address(102) # (102 RTD)
                        temp = device.query("R")
                        print(temp)
                        temp = string.split(temp, ": ")[1]
                        stat_temporary = None
                        stat_temporary = numpy.append(stat_atlas_rtd, float(string.split(temp, " C")[0])) #local statistic
                        if stat_temporary is not None:
                            stat_atlas_rtd = stat_temporary
                        else:
                            stat_atlas_rtd = numpy.median(stat_atlas_rtd)
                        temp = str(device1.readLight()) # BH1750
                        print 'Light Intensity: ' + temp + ' lx'
                        if temp is not None:
                            stat_bh1750_lux = numpy.append(stat_bh1750_lux, float(str(device1.readLight()))) #local statistic
                        else:
                            stat_bh1750_lux = numpy.median(stat_bh1750_lux)
                        # local statistic routine
                        # compute mean
                        print 'Local Statistic at ' + (time.strftime('%d/%m/%Y %H:%M:%S'))
                        print '[Average] Ambient Temperature: ' + str(numpy.mean(stat_dht22_temp)) + ' C'
                        print '[Average] Ambient Humidity: ' + str(numpy.mean(stat_dht22_humid)) + ' %'
                        print '[Average] pH: ' + str(numpy.mean(stat_atlas_ph))
                        print '[Average] EC: ' + str(numpy.mean(stat_atlas_ec))
                        print '[Average] TDS: ' + str(numpy.mean(stat_atlas_tds))
                        print '[Average] Salinity: ' + str(numpy.mean(stat_atlas_sal))
                        print '[Average] Gravity: ' + str(numpy.mean(stat_atlas_gra))
                        print '[Average] RTD: ' + str(numpy.mean(stat_atlas_rtd))
                        print '[Average] Light Intensity: ' + str(numpy.mean(stat_bh1750_lux)) + ' lx'
                        # compute median
                        print '[Median] Ambient Temperature: ' + str(numpy.median(stat_dht22_temp)) + ' C'
                        print '[Median] Ambient Humidity: ' + str(numpy.median(stat_dht22_humid)) + ' %'
                        print '[Median] pH: ' + str(numpy.median(stat_atlas_ph))
                        print '[Median] EC: ' + str(numpy.median(stat_atlas_ec))
                        print '[Median] TDS: ' + str(numpy.median(stat_atlas_tds))
                        print '[Median] Salinity: ' + str(numpy.median(stat_atlas_sal))
                        print '[Median] Gravity: ' + str(numpy.median(stat_atlas_gra))
                        print '[Median] RTD: ' + str(numpy.median(stat_atlas_rtd))
                        print '[Median] Light Intensity: ' + str(numpy.median(stat_bh1750_lux)) + ' lx'
                        # truncate local statistic arrays
                        stat_dht22_temp = numpy.delete(stat_dht22_temp, 0)
                        stat_dht22_humid = numpy.delete(stat_dht22_humid, 0)
                        stat_atlas_ph = numpy.delete(stat_atlas_ph, 0)
                        stat_atlas_ec = numpy.delete(stat_atlas_ec, 0)
                        stat_atlas_tds = numpy.delete(stat_atlas_tds, 0)
                        stat_atlas_sal = numpy.delete(stat_atlas_sal, 0)
                        stat_atlas_gra = numpy.delete(stat_atlas_gra, 0)
                        stat_atlas_rtd = numpy.delete(stat_atlas_rtd, 0)
                        stat_bh1750_lux = numpy.delete(stat_bh1750_lux, 0)
                    else:
                        time.sleep(0.50) #sleep 500ms
            except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
                    print("Continuous polling stopped")
                        
        # if not a special keyword, pass commands straight to board
        else:
            if len(input) == 0:
                print "Please input valid command."
            else:
                try:
                    print(device.query(input))
                except IOError:
                    print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")


if __name__ == '__main__':
    main()
