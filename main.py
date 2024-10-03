from src.controller.get_cordinate import CordinateCheck
from src.controller.rstp import RSTP
import argparse

def main(class_name, path_file):
    if class_name == 'CordinateCheck':
        cordinate_check = CordinateCheck()
        cordinate_check.proccess(path_file)
    elif class_name == 'RSTP':
        rstp = RSTP()
        rstp.get_cordinate(path_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download file using specified class.")
    parser.add_argument("-n", "--name", type=str, required=True, help="Nama class yang ingin digunakan.")
    parser.add_argument("-f", "--file", type=str, required=False, help="File yang ingin di download.")

    args = parser.parse_args()
    main(args.name, args.file)