import argparse
import math



parser = argparse.ArgumentParser(description='lab1')
parser.add_argument("-t", help = "time tfp", required = True)
parser.add_argument('-o', help='overshoot ', required=False)
parser.add_argument('-g', help='gain ', required=False)
args = vars(parser.parse_args())


if __name__ == "__main__": 

    zeta = math.log(args.o) / math.sqrt(math.pi**2 + math.log(args.o))
    natural_freq = math.pi / (args.t * math.sqrt(1-zeta**2))
    tau = 1 / (2 * zeta * natural_freq)
    k1 = (natural_freq**2 * tau) / args.g


    print(f"{args.t=}")
    print(f"{args.o=}")
    print(f"{zeta=}")