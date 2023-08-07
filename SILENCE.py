from relicenser import get_compatible_licenses
from remediator import get_remediation
import argparse
import logging
logger = logging.getLogger(__name__)
def SILENCE():

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=False)
    parser.add_argument("-v", "--version", type=str, required=False)
    parser.add_argument(
        "--mongo_uri", type=str, required=False, default="mongodb://localhost:27017/"
    )
    
    args = parser.parse_args()

    logging.basicConfig(
        filename="SILENCE.log",
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    compats = get_compatible_licenses(args.mongo_uri, args.name, args.version)
    remed = get_remediation(args.mongo_uri, args.name, args.version)

    
    print(f"Possible Remediations for {args.name} {args.version}:")
    print("1. Change project license to "+ ", ".join(compats[:3]))
    for i, remediation in enumerate(remed["changes"]):
        print(f"{i+2}. Or make the following dependency changes :")
        for j,operation in enumerate(remediation):
            print("    "+chr(ord("a")+j) + ") "+ operation + ";")
    
    return compats, remed    


if __name__ =="__main__":
    SILENCE()
    