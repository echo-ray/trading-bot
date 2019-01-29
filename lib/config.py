from argparse import ArgumentParser
import json

parser = ArgumentParser(add_help=False)
parser.add_argument("-c", "--credentials", dest="credentials",
                    help="credentials directory", metavar="CREDS", default="credentials")

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
