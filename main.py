import yaml, os, subprocess, shlex, shutil, sys, argparse
from PIL import Image

import utility as u


####################
# PART 0: SETTING UP
####################

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--no-confirm", help="don't require any final confirmation", action="store_true")
parser.add_argument("system", nargs="?", default=None, help="quoted console of desired ROM")
parser.add_argument("rom", nargs="?", default=None, help="quoted ROM name")
# I DON'T want to be able to supply a ROM ID from the command line
# parser.add_argument("-i", "--id", help="title ID of the ROM")

args = parser.parse_args()

# If any command line parameter is set, then we're clearly using the command line
cli = args.system or args.rom

# If we're using the command line and both the system and ROM aren't set, then we're missing information
if cli and not (args.system and args.rom):
    sys.exit("Insufficient CLI arguments - provide both a system and a ROM.")


# Read the settings
with open('settings.yaml') as file:
    settings = yaml.safe_load(file)

# The relative path to the folder with all the systems and their images from the python script
# as configured in the settings
images_path = settings['paths']['images']
image_files = u.get_files(images_path)

#######################
# Part 1: PICK A SYSTEM
#######################

systems_in_settings = settings['systems'].keys()
systems_in_images = u.get_folders(images_path)
systems = list(x for x in systems_in_settings if x in systems_in_images)

if cli:
    def validate_system(system):
        return system in systems

    system = args.system
    
    if not validate_system(system):
        sys.exit("Invalid system argument, folder not found")

else:
    print(f"systems detected in settings: {', '.join(systems_in_settings)}")
    print(f"systems detected in images folder: {', '.join(systems_in_images)}")
    print(" ")

    system = u.choose(
        systems,
        title_message="Available systems",
        input_message="Choose one of the above systems: "
    )

system_name = settings['systems'][system]['name']
system_core = settings['systems'][system]['core']
system_format = settings['systems'][system]['format']
# This is a variable we'll need MUCH later
system_path = u.get_path(images_path, system)

if not cli:
    print(f"Chosen \"{system_name}\" ({system}) using core \"{system_core}\"")
    input("(press enter to continue or Ctrl+C to cancel)\n")


#####################
# PART 2: PICK A GAME
#####################

system_files = u.get_files(system_path)
games = u.get_folders(system_path)

if cli:
    def validate_rom(rom):
        return rom in games

    game = args.rom

    if not validate_rom(game):
        sys.exit("Invaild ROM argument, folder not found")

else:
    game = u.choose(
        games,
        title_message="Available games",
        input_message="Choose one of the above games: "
    )

game_path = u.get_path(system_path, game)
game_files = u.get_files(game_path)

if not cli:
    print(f"Chosen \"{game}\"")
    input("(press enter to continue or Ctrl+C to cancel)\n")


#####################
# PART 3: FIND IMAGES
#####################

# Now that we know what they want, lets see if we can find all the necessary files
images = {
    "icon0": None,
    "startup": None,
    "bg": None
}

if 'icon0.png' in game_files:
    images['icon0'] = u.get_path(game_path, 'icon0.png')
else:
    # Since icon0 is per-game, there's no where else this image can be.
    
    # the `tbs=iar:s` query parameter here means that only square images are shown
    search = 'https://google.com/images?q={game}+{system}+cover+art&tbs=iar:s'.format(
        game="+".join(game.split()),
        system="+".join(system.split())
    )

    sys.exit(f"That game folder doesn\'t contain an icon0.png!\nNeed inspiration? Try here: {search}")

if 'startup.png' in game_files:
    images['startup'] = u.get_path(game_path, 'startup.png')
elif 'startup.png' in system_files:
    images['startup'] = u.get_path(system_path, 'startup.png')
elif 'startup.png' in image_files:
    images['startup'] = u.get_path(images_path, 'startup.png')
else:
    # Couldn't find startup ANYWHERE
    sys.exit("Failed to find startup.png image")

if 'bg.png' in game_files:
    images['bg'] = u.get_path(game_path, 'bg.png')
elif 'bg.png' in system_files:
    images['bg'] = u.get_path(system_path, 'bg.png')
elif 'bg.png' in image_files:
    images['bg'] = u.get_path(images_path, 'bg.png')
else:
    # Couldn't find bg ANYWHERE
    sys.exit("Failed to find bg.png file")


#######################
# PART 4: PICK TITLE ID
#######################

# For the convience of the user, and for error prevention, we store the title ID they choose in a file
if not os.path.exists('title_ids.yaml'):
    with open('title_ids.yaml', 'w+') as file:
        file.write('')

with open('title_ids.yaml') as file:
    title_ids = yaml.safe_load(file)
    if title_ids is None:
        title_ids = {}

inv = {game: id for id, game in title_ids.items()}
if cli:
    # If we're in CLI mode then we HAVE to already have the title ID
    # If not, they need to go through the interactive interface
    if game in inv:
        title_id = inv[game]
    else:
        sys.exit("Failed to find previous title ID for this ROM - please re-run the script with no arguments and go through the interactive menu to assign a title ID")

else:
    # Script is being run interactively
    if game in inv:
        print(f"Detected a previously title ID for this game: {inv[game]}")
        choice = input("Do you wish to change it and create a new one or continue using the same ID? ('change' to create a new ID or leave blank to use the same one): ")

        if len(choice) >= 1 and choice[0].lower() == 'c':
            new_id = True
        else:
            new_id = False
            title_id = inv[game]
    else:
        print("No previously generated title ID was detected")
        new_id = True

    if new_id:
        title_id = input("What title ID would you like for the game? (NOTE: only UPPERCASE letters or numbers, EXACTLY 9 characters long): ")

        if title_id in title_ids.keys():
            collision = title_ids[title_id]
            sys.exit(f"This title ID already exists in title_ids.yaml for the game {collision}!")

# Check if the final title_id is valid
if len(title_id) != 9:
    sys.exit("The provided title ID is invalid! It has to be exactly 9 characters.")

def check_char(char):
    """ Given a single character from a title_id, this function checks if it's an uppercase letter or a number """
    return (ord(char) in range(ord('A'), ord('Z')+1)) or (ord(char) in range(ord('0'), ord('9')+1))
valid_title_id = all(map(check_char, title_id))
if not valid_title_id:
    sys.exit("The provided title ID is invalid! It can only contain UPPERCASE letters or numbers.")

title_ids[title_id] = game
with open('title_ids.yaml', 'w') as file:
    yaml.dump(title_ids, file)


######################
# PART 5: CONFIRMATION
######################

vita_core_path = settings['paths']['vita']['cores'].format(core=system_core)
rom_filename = system_format.format(title=game)
vita_rom_path = settings['paths']['vita']['roms'].format(system=system, filename=rom_filename)

if not (cli and args.no_confirm):
    print(" ")
    print("Here are all the final parameters:")

print("vita_core_path = {}".format(vita_core_path))
print("vita_rom_path  = {}".format(vita_rom_path))
print("title_id       = {}".format(title_id))
print("icon0          = {}".format(images['icon0']))
print("startup        = {}".format(images['startup']))
print("bg             = {}".format(images['bg']))
print("output         = {}".format(f"VPKS/{game}.vpk"))

if not (cli and args.no_confirm):
    print("Do you wish to proceed with generating the vpk file?")
    input("(press enter to continue or Ctrl+C to cancel)\n")


########################
# PART 6: CONVERT IMAGES
########################

# We have the path of all 3 images in `images` - now we need to be SURE they're all the correct size
# And the correct colour pallete
def make_correct_format(filepath, filename, size):
    image = Image.open(filepath)

    new_image = image.resize(size)
    new_image.save(filepath)
    
    compress_command = "pngquant --force 256 -o content/{} {}".format(
        shlex.quote(filename),
        shlex.quote(filepath)
    )
    # compress_command += " --verbose"

    subprocess.run(shlex.split(compress_command))

    # Replace the original file with the new smaller and compressed image
    # For storage space sake
    shutil.copyfile("content/{}".format(filename), filepath)

make_correct_format(images['icon0'], 'icon0.png', (128, 128))
make_correct_format(images['startup'], 'startup.png', (280, 158))
make_correct_format(images['bg'], 'bg.png', (840, 500))


####################
# PART 7: MAKE FILES
####################

# Make the `core.txt` and `rom.txt` files necessary to boot
with open('content/core.txt', 'w+') as file:
    file.write(vita_core_path)
with open('content/rom.txt', 'w+') as file:
    file.write(vita_rom_path)

mksfoex_command = "vita-mksfoex -s TITLE_ID={} {} content/param.sfo".format(
    shlex.quote(title_id),
    shlex.quote(game)
)
subprocess.run(shlex.split(mksfoex_command))

# We need to create the output VPKS folder if it doesn't already exist
if 'VPKS' not in u.get_folders('.'):
    os.mkdir('VPKS')

pack_vpk_command = \
    "vita-pack-vpk -s content/param.sfo -b content/eboot.bin VPKS/{}.vpk".format(shlex.quote(game)) + \
    " -a content/icon0.png=sce_sys/icon0.png" + \
    " -a content/startup.png=sce_sys/livearea/contents/startup.png" + \
    " -a content/bg.png=sce_sys/livearea/contents/bg.png" + \
    " -a content/template.xml=sce_sys/livearea/contents/template.xml" + \
    " -a content/core.txt=core.txt" + \
    " -a content/rom.txt=rom.txt"

subprocess.run(shlex.split(pack_vpk_command))

print("Successfully created VPKS/{}.vpk!".format(game))
