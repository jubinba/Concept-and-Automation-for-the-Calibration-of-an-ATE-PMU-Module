import serial
from serial.tools import list_ports
from time import sleep

class communicator():
    def __init__(self, verbose:bool=False):
        self.port = self.find_device(verbose)
        self.s = serial.Serial(self.port, 115200, timeout=5)
        self.verbose = verbose
        self.com_setup()
        self.com_delay = 0
        self.rx_delay = 0.1
    
    def find_device(self, verbose: bool) -> str:
        ports = list_ports.comports()
        possible_devices = list()
        i = 0
        
        if verbose:
            print("Available COMs:")
        
        for p in ports:
            if "CH340" in p.description:
                possible_devices.append(p.device)
                if verbose:
                    print("%i >" %i, end='')
                i += 1
            if verbose: print("\t%-5s: %-30s [%s]" %(p.device, p.description, p.hwid))

        if not verbose and len(possible_devices) != 1:
            return None
        elif len(possible_devices) == 0:
            print("No usable device found")
            return None
        elif len(possible_devices) > 1:
            print("tpye Nr. to use:")
            return possible_devices[int(input())]
        else:
            return possible_devices[0]
        
    def com_setup(self):
        print_str = str()
        self.s.flushInput()
        self.s.flushOutput()
        self.s.write(b"restart\n")
        sleep(1)
        
        print_str += self.s.read_all().decode()
        self.s.write(b"print_mode -m RAW\n")
        sleep(0.1)
        print_str += self.s.read_all().decode()
        
        if self.verbose:
            print(print_str)
            
    
    def command(self, command_string:str, read:bool=False) -> int:
        self.s.flushInput()
        tx_str = command_string + "\n"
        
        sleep(self.com_delay)
        
        self.s.write(tx_str.encode())
        
        if read is False:
            return
        
        sleep(self.rx_delay)
        
        self.s.read_until(b"r[")
        raw_data_str = self.s.read_until(b"]").decode()
        if self.verbose:
            print(raw_data_str)

        if raw_data_str.endswith("]") == -1:
            return None
        else:
            raw_data_str = raw_data_str[:-1]

        data, length = raw_data_str.split("#")
        data_mask = (1<<int(length,16))-1
        data = int(data,16)
        
        return data & data_mask
    
    def __del__(self):
        self.s.close()

    
    