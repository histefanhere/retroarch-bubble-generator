import yaml, os, subprocess, shlex, shutil
from PIL import Image

import utility as u

# TODO: Use `shlex.quote` as much as I can, but it seems to be using single quotes instead of double quotes?

# TODO: These should use the settings set in `settings.yaml`
def get_core(core):
    return f"app0:{core}_libretro.self"

def get_rom(system, filename):
    return f"ux0:ROMS/{system}/{filename}"

# Read the settings
with open('settings.yaml') as file:
    settings = yaml.safe_load(file)

# The relative path to the folder with all the systems and their images from the python script
# as configured in the settings
images_path = settings['paths']['images']

systems_in_settings = settings['systems'].keys()
systems_in_images = u.get_folders(images_path)

# This is a variable we'll need MUCH later
image_files = u.get_files(images_path)

print(f"systems detected in settings: {', '.join(systems_in_settings)}")
print(f"systems detected in images folder: {', '.join(systems_in_images)}")
print(" ")
systems = list(x for x in systems_in_settings if x in systems_in_images)

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

print(f"Chosen \"{system_name}\" ({system}) using core \"{system_core}\"")
input("(press enter to continue)\n")


system_files = u.get_files(system_path)
games = u.get_folders(system_path)

game = u.choose(
    games,
    title_message="Available games",
    input_message="Choose one of the above games: "
)

game_path = u.get_path(system_path, game)
game_files = u.get_files(game_path)

print(f"Chosen \"{game}\"")
input("(press enter to continue)\n")


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
    print('ERROR: Sorry, that game folder doesn\'t contain an icon0.png!')
    exit()

if 'startup.png' in game_files:
    images['startup'] = u.get_path(game_path, 'startup.png')
elif 'startup.png' in system_files:
    images['startup'] = u.get_path(system_path, 'startup.png')
elif 'startup.png' in image_files:
    images['startup'] = u.get_path(images_path, 'startup.png')
else:
    # Couldn't find startup ANYWHERE
    print("ERROR: Failed to find startup.png file")
    exit()

if 'bg.png' in game_files:
    images['bg'] = u.get_path(game_path, 'bg.png')
elif 'bg.png' in system_files:
    images['bg'] = u.get_path(system_path, 'bg.png')
elif 'bg.png' in image_files:
    images['bg'] = u.get_path(images_path, 'bg.png')
else:
    # Couldn't find bg ANYWHERE
    print("ERROR: Failed to find bg.png file")
    exit()


# We have the path of all 3 images in `images` - now we need to be SURE they're all the correct size
# And the correct colour pallete
# icon0.png   - 128 x 128
# startup.png - 280 x 158
# bg.png      - 840 x 500

def make_correct_format(filepath, filename, size):
    image = Image.open(filepath)

    new_image = image.resize(size)
    new_image.save(filepath)
    
    # TODO: Get shlex to work here
    compress_command = "pngquant --force 256 -o content/{} \"{}\"".format(
        filename,
        filepath
    )
    # compress_command += " --verbose"

    # TODO: Does this need to be a shell?
    subprocess.run(shlex.split(compress_command), shell=True)

    # Replace the original file with the new smaller and compressed image
    shutil.copyfile("content/{}".format(filename), filepath)

# TODO: Put this in a list / object
# TODO: This should be done much later so nothing is changed until the user confirms everything
make_correct_format(images['icon0'], 'icon0.png', (128, 128))
make_correct_format(images['startup'], 'startup.png', (280, 158))
make_correct_format(images['bg'], 'bg.png', (840, 500))

# For the convience of the user, and for error prevention, we store the title ID they choose in a file
if not os.path.exists('title_ids.yaml'):
    with open('title_ids.yaml', 'w+') as file:
        file.write('')

with open('title_ids.yaml') as file:
    title_ids = yaml.safe_load(file)
    if title_ids is None:
        title_ids = {}

inv = {game: id for id, game in title_ids.items()}
if game in inv:
    print(f"Detected a previously title ID for this game: {inv[game]}")
    choice = input("Do you wish to continue using this id for the game or create a new one? ('yes' for yes or anything else for no): ")

    if len(choice) >= 1 and choice[0] == 'y':
        new_id = False
        title_id = inv[game]
    else:
        new_id = True
else:
    print("No previously generated title ID was detected")
    new_id = True

if new_id:
    # TODO: Error check this
    title_id = input("What title ID would you like for the game? (NOTE: only UPPERCASE letters or numbers): ")

    if title_id in title_ids.keys():
        collision = title_ids[title_id]
        print(f"ERROR: This title ID already exists in title_ids.yaml for the game {collision}")
        exit()


title_ids[title_id] = game
with open('title_ids.yaml', 'w') as file:
    yaml.dump(title_ids, file)

# TODO: Confirm everything the user has done till now
# - all core and rom paths, etc
input("are you happy with what you've done till now? Cause we'll generate stuff now")

# Make the `core.txt` and `rom.txt` files necessary to boot
with open('content/core.txt', 'w+') as file:
    file.write(get_core(system_core))
with open('content/rom.txt', 'w+') as file:
    filename = system_format.replace('$title', game)
    file.write(get_rom(system, filename))

# TODO: Delete the core.txt and rom.txt files

mksfoex_command = "vita-mksfoex -s TITLE_ID={} \"{}\" content/param.sfo".format(
    title_id,
    game
)
subprocess.run(shlex.split(mksfoex_command))

# We need to create the output VPKS folder if it doesn't already exist
if 'VPKS' not in u.get_folders('.'):
    os.mkdir('VPKS')

# TODO: Remove `shlex.quote` here?
pack_vpk_command = ("vita-pack-vpk -s content/param.sfo -b content/eboot.bin \"{}\"" + \
    " -a {}=sce_sys/icon0.png" + \
    " -a {}=sce_sys/livearea/contents/startup.png" + \
    " -a {}=sce_sys/livearea/contents/bg.png").format(
        "VPKS/" + game + ".vpk",
        shlex.quote('content/icon0.png'),
        shlex.quote('content/startup.png'),
        shlex.quote('content/bg.png')
    )
pack_vpk_command += " -a content/template.xml=sce_sys/livearea/contents/template.xml" + \
    " -a content/core.txt=core.txt" + \
    " -a content/rom.txt=rom.txt"    

subprocess.run(shlex.split(pack_vpk_command))

# TODO: Print out that everything was successful and path to output VPK file