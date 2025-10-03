import argparse
import math



parser = argparse.ArgumentParser(description='lab1')
parser.add_argument("-t", help = "time tfp", required = True, type= float)
parser.add_argument('-o', help='overshoot ', required=False, type = float)
parser.add_argument('-g', help='gain ', required=False, type = float)
args = vars(parser.parse_args())


if __name__ == "__main__": 

    zeta = math.log(args.get('o')) / math.sqrt(math.pi**2 + math.log(args.get('o')) ** 2)
    natural_freq = math.pi / (args.get('t') * math.sqrt(1-zeta**2))
    tau = 1 / (2 * zeta * natural_freq)
    k1 = (natural_freq**2 * tau) / args.get('g')


    print(f"{args.get('t')=}")
    print(f"{args.get('o')=}")
    print(f"{zeta=}")
    print(f"{natural_freq=}")
    print(f"{tau=}")
    print(f"{k1=}")