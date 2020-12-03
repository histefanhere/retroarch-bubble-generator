import os

# Utility wrapper functions for os.path and other various os functionalities
def get_path(*paths):
    return os.path.join(*paths)

def is_folder(*paths):
    return os.path.isdir(get_path(*paths))

def is_file(*paths):
    return not is_folder(*paths)

def get_files(*paths):
    """ Get all the files present in *paths """
    everything = os.listdir(get_path(*paths))
    return list(filter(lambda x: is_file(*paths, x), everything))

def get_folders(*paths):
    """ Get all the folders present in *paths """
    everything = os.listdir(get_path(*paths))
    return list(filter(lambda x: is_folder(*paths, x), everything))


def choose(choices, title_message, input_message):
    """ Given a list of choices, the user must either choose an index of an item from the list
    or the fullname of an item in the list. """

    print(title_message)
    for i, choice in enumerate(choices):
        print(f"{i} : {choice}")

    inp = input(input_message)

    # First see if it's one of the choices directly
    if inp in choices:
        return inp
    else:
        try:
            inp = int(inp)
        except ValueError:
            # They gave us a string, but it's not in the list
            print("ERROR: Unknown Input!")
            exit()
        else:
            if inp in range(len(choices)):
                return choices[inp]
            else:
                # It's a number, but not in range
                print("ERROR: Invalid Input!")
                exit()
