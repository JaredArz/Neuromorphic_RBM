# ===========================================================
#   Various resistance values for 
#   memristive devices from the literature (references included)
#   which have been used to implement cross bar arrays.
# ===========================================================
from dataclasses import dataclass

#   add slots=True to dataclass if python 3.11
@dataclass()
class RRAM_dev:
    LRS   : float
    HRS   : float
    device_type: str
    ref   : str
    def __str__(self):
        return f"{self.ref}"

MTJ_INC   = RRAM_dev(1000,3000,
                     "MTJ",
                     "N/A")

#NOTE: was using this when it says 1e14
HfHfO2  = RRAM_dev(1e5,1e6,
                    "Memristor",
                    "intrinsic switching variability")
#===================== amp values ============================
#   known-good values [end points of highest solution band]:
#   harder problems may be more susceptible to differences in this scale value
#               RRAM                        MRAM
#   Max Sat    [0.75e14 1.25e14]      [1.25e12]
#   Max Cut    [1e15]      [1.5e13 1e14]
#   Ind Set    [1e14]      [1e12 ** bad results max 70]
#=============================================================


'''
ZnO       = RRAM_dev(2*10e-1 ,2*10e6 ,1    ,"Kim 2009")
MnO2      = RRAM_dev(2*10e-1 ,10e4   ,1    ,"Yang 2009")
MnO_Ta2O5 = RRAM_dev(5*10e3  ,10e9   ,1    ,"Hu Q 2018")
test2     = RRAM_dev(1000    ,7000   ,3.5e7 ,"N/A")
'''
