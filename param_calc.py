import argparse
import math




parser = argparse.ArgumentParser(description='lab1')
parser.add_argument('-o', help='overshoot ', required=True)
parser.add_argument('-t','--tp', help='Time to first peak', required=True)
args = vars(parser.parse_args())

pi = 3.14159
e = 2.17828

def calc_damping(OS): 
    num = math.log(OS/100, e)
    denom = math.sqrt(pi**2 + (math.log(OS/100, e))**2)

    return num / denom
    

def calc_frequency(OS);




def calc_freq: 
    pass


def calc_k1:
    pass




if __name__ == "__main__": 



