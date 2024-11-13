from . import bit_coder
from . import communicator
from . import pmu_def
import pandas as pd
from time import sleep

class pmu():
    def __init__(self) -> None:
        self.c = communicator.communicator(False)
        self.channels = [pmu_ch(self, i) for i in range(4)]
        
    def decode_pmu_reg(self):
        pmu_reg_list = list()
        for i, ch in enumerate(self.channels):
            pmu_reg_list.append(pd.Series(ch.decode_pmu_reg(), name=i))
        
        return pd.DataFrame(pmu_reg_list)
    
    def decode_sys_ctrl(self):
        return bit_coder.decode(self.sys_ctrl, pmu_def.pmu_SCR.encoding)
    
    def decode_cmp_sts(self):
        return bit_coder.decode(self.sys_ctrl, pmu_def.pmu_CSR.encoding)
    
    def decode_alm_sts(self):
        return bit_coder.decode(self.sys_ctrl, pmu_def.pmu_ASR.encoding)
    
    @property
    def sys_ctrl(self):
        return self.c.command("pmu_rREG -r SCR" ,True)
    
    @sys_ctrl.setter
    def sys_ctrl(self, val):
        self.c.command("pmu_wSCR -d %i" %(val))
    
    def change_sys_ctrl(self, reg_dict):
        sys_ctrl_val = self.sys_ctrl
    
        for name, value in reg_dict.items():
            sys_ctrl_val = bit_coder.modify(
                value,
                name,
                sys_ctrl_val,
                pmu_def.pmu_SCR.encoding
            )
        self.c.command("pmu_wSCR -d %i" %(sys_ctrl_val))
    
    @property
    def cmp_sts(self):
        return self.c.command("pmu_rREG -r CSR" ,True)
    
    @property
    def alm_sts(self):
        return self.c.command("pmu_rREG -r ASR" ,True)
    
    def read_dac_regs(self, reg="X1"):
        ret_data = list()
        for i, ch in enumerate(self.channels):
            dacs_ch_data = dict()
            for dac_reg in pmu_def.DAC_REG_TABLE.keys():
                if dac_reg == "Offset" and reg != "X1":
                    continue
            
                dacs_ch_data[dac_reg] = ch.read_dac(dac_reg, reg)
            ret_data.append(pd.Series(dacs_ch_data, name=i))
        
        return pd.DataFrame(ret_data)

    def write_all_PMU_REGS(self, data):
        self.c.command("pmu_wPMU -c 0xF -d %i" % (data))
        
    def reset(self):
        self.c.command("pmu_reset")
        sleep(0.1)
        self.c.command("pmu_release")
        
    def mem_write_byte(self, adr, data):
        self.c.command("mem_write -a %i -d %i" %(adr, data&0xff))
        
    def mem_write_data(self, data_dict, word_size=16):
        self.c.command("pmu_reset")
        
        byte_list = range(word_size//8)
        
        for adr, data in data_dict.items():
            for byte_pos in byte_list[::-1]:
                self.c.command("mem_write -a %i -d %i" %(
                    adr+byte_pos,
                    data&0xff))
                sleep(0.01)
                data = data >> 8
        
        self.c.command("pmu_release")
        
    def mem_read_data(self, adr_list, word_Size=16):
        self.c.command("pmu_reset")
        
        ret_dict = dict()
        
        for adr in adr_list:
            ret_dict[adr] = self.c.command("mem_read -a %i -l %i" 
                                %(adr, word_Size),
                                True)
        
        
        self.c.command("pmu_release")
        
        return ret_dict
                


class pmu_ch():
    def __init__(self, pmu_class, channel) -> None:
        self.__parent = pmu_class
        self.__channel = 1 << channel
    
    @property
    def channel(self):
        return self.__channel
    
    @property
    def pmu_reg(self):
        return self.__parent.c.command("pmu_rPMU -c %i" % self.channel, True)
    
    @pmu_reg.setter
    def pmu_reg(self, value):
        self.__parent.c.command("pmu_wPMU -c %i -d %i" % (self.channel, value))
    
    def change_pmu_reg(self, reg_dict):
    #name, value):
        pmu_reg_val = self.pmu_reg
        for name, value in reg_dict.items():
            pmu_reg_val = bit_coder.modify(
                value,
                name,
                pmu_reg_val,
                pmu_def.pmu_PMU.encoding
            )
        pmu_reg_val |= 0x7f
        pmu_reg_val -= 0x7f

        self.__parent.c.command("pmu_wPMU -c %i -d %i" %(self.channel, pmu_reg_val))

    def decode_pmu_reg(self):
        return bit_coder.decode(self.pmu_reg, pmu_def.pmu_PMU.encoding)
    
    def write_dac(self, data, dac_reg, reg="X1"):
        dac_adr = pmu_def.DAC_REG_TABLE[dac_reg]
        
        self.__parent.c.command("pmu_wDAC -c %i -a %i -r %s -d %i" %(
            self.channel,
            dac_adr,
            reg,
            data
            ))
        
    def read_dac(self, dac_reg, reg="X1"):
        dac_adr = pmu_def.DAC_REG_TABLE[dac_reg]
        
        dac_val = self.__parent.c.command("pmu_rDAC -c %i -a %i -r %s" %(
                                    self.channel,
                                    dac_adr,
                                    reg), True)
        return dac_val & 0xFFFF
    
    
