from api.server.library import paths
import os.path as path


def create_sms_file(filename, content):
    sms_dir = paths.get_sms_codes_dir()
    sms_file = sms_dir + filename + ".txt"
    try:
        with open(sms_file, "w+") as sf:
            sf.write(content)
    except Exception as e:
        print("Error during writing sms code into the file {:s}".format(str(e)))


def get_code(filename):
    sms_dir = paths.get_sms_codes_dir()
    sms_file = sms_dir + filename + ".txt"
    if path.exists(sms_file) and path.isfile(sms_file):
        try:
            with open(sms_file, "r") as sf:
                sms_code = sf.readline()
                return sms_code
        except Exception as e:
            print("error during returning sms code {:s}".format(str(e)))
    else:
        print("{} doesn't exist or not a file type".format(sms_file))