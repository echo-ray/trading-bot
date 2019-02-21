from argparse import ArgumentParser
import json

parser = ArgumentParser()
parser.add_argument("-c", "--credentials", dest="credentials",
                    help="credentials directory", default="credentials")

parser.add_argument("-p", "--pair", dest="pair",
                    help="pair to trade")

parser.add_argument("-str", "--strategy", dest="strategy",
                    help="filename of the strategy", default="default")

parser.add_argument("-s", "--steps", dest="steps",
                    help="number of steps to execute", default=None, type=int)

parser.add_argument("-stp", "--current-step", dest="current_step",
                    help="current step to start")

parser.add_argument("-r", "--real", dest="real", action="store_true",
                    help="make real trades", default=False)

parser.add_argument("-log", "--log", dest="log", action="store_true",
                    help="log prices", default=False)

parser.add_argument("-logc", "--logc", dest="combiner_log", action="store_true",
                    help="log combiner meta data", default=False)

parser.add_argument('-exc', action='append', dest='exchanges',
                    default=[],
                    help='exchanges list',
                    )

parser.add_argument("-d", "--diff", dest="diff",
                    help="diff between prices to execute step", default=None)

parser.add_argument("-qty", "--quantity", dest="quantity",
                    help="asset quantity to trade", default="1")

parser.add_argument("-fromside", "--buyside", dest="buy_side",
                    help="buy side", default=None)

parser.add_argument("-toside", "--sellside", dest="sell_side",
                    help="sell side", default=None)


args, extra = parser.parse_known_args()


class Config:
    def credentials(self, filename):
        with open(args.credentials+"/"+filename) as f:
            creds = json.load(f)
        return creds

    def load_json(self, filename):
        with open(filename) as f:
            conf = json.load(f)
        return conf

    @staticmethod
    def get_args():
        return args

    @staticmethod
    def print_help(file):
        parser.print_help(file)
