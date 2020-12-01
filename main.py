import yaml, os, subprocess, shlex, shutil
from PIL import Image

# TODO: Choose ID or name
# TODO: Choose ID for systems
# TODO: Only show the systems in settings and images if there's a difference

# TODO: Use `shlex.quote` as much as I can, but it seems to be using single quotes instead of double quotes?

def get_core(core):
    return f"app0:{core}.self"

def get_rom(system, filename):
    return f"ux0:ROMS/{system}/{filename}"



# Utility wrapper functions for os.path
def get_path(*paths):
    return os.path.join(*paths)

def is_folder(*paths):
    return os.path.isdir(get_path(*paths))

def is_file(*paths):
    return not is_folder(*paths)

# Read the settings
with open('settings.yaml') as file:
    settings = yaml.safe_load(file)

# The relative path to the folder with all the systems and their images from the python script
# as configured in the settings
images_path = settings['paths']['images']

systems_in_settings = settings['systems'].keys()
systems_in_images = os.listdir(images_path)
systems_in_images = list(x for x in systems_in_images if is_folder(images_path, x))

# This is a variable we'll need MUCH later
image_files = os.listdir(images_path)
image_files = list(filter(lambda x: is_file(images_path, x), image_files))

print(f"systems detected in settings: {', '.join(systems_in_settings)}")
print(f"systems detected in images folder: {', '.join(systems_in_images)}")

systems = list(x for x in systems_in_settings if x in systems_in_images)


print(f"\nsystems: {', '.join(systems)}")

system = input("Choose one of the above systems: ")
if system not in systems:
    print("Not a valid choice!")
    exit()


system_name = settings['systems'][system]['name']
system_core = settings['systems'][system]['core']
system_format = settings['systems'][system]['format']

print(f"Chosen {system_name} ({system}) using core {system_core}")
input("press enter to continue")


system_path = get_path(images_path, system)

system_files = os.listdir(system_path)
system_files = list(filter(lambda x: is_file(system_path, x), system_files))

games = os.listdir(system_path)
games = list(filter(lambda x: is_folder(system_path, x), games))


print("\nGames to choose from: ")
for i, game in enumerate(games):
    print(f"{i} : {game}")

game_i = input("Choose one of the above games: ")
try:
    game_i = int(game_i)
    if game_i not in range(len(games)):
        raise TypeError
except:
    print("Not a valid choice!")
    exit()

game = games[game_i]

game_path = get_path(system_path, game)

game_files = os.listdir(game_path)
game_files = list(filter(lambda x: is_file(game_path, x), game_files))

# Now that we know what they want, lets see if we can find all the necessary files
images = {
    "icon0": None,
    "startup": None,
    "bg": None
}

# TODO: Maybe `icon.png` doesn't have to be unique?
# (it probably does because otherwise how do we get the game name)
if 'icon0.png' in game_files:
    images['icon0'] = get_path(game_path, 'icon0.png')
else:
    # Since icon0 is per-game, there's no where else this image can be.
    print('Sorry, that game folder doesn\'t contain an icon0.png!')
    exit()


if 'startup.png' in game_files:
    images['startup'] = get_path(game_path, 'startup.png')
elif 'startup.png' in system_files:
    images['startup'] = get_path(system_path, 'startup.png')
elif 'startup.png' in image_files:
    images['startup'] = get_path(images_path, 'startup.png')
else:
    # Couldn't find startup ANYWHERE
    print("Failed to find startup.png file")
    exit()


if 'bg.png' in game_files:
    images['bg'] = get_path(game_path, 'bg.png')
elif 'bg.png' in system_files:
    images['bg'] = get_path(system_path, 'bg.png')
elif 'bg.png' in image_files:
    images['bg'] = get_path(images_path, 'bg.png')
else:
    # Couldn't find bg ANYWHERE
    print("Failed to find bg.png file")
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
    compress_command = "pngquant --force --verbose 256 -o content/{} \"{}\"".format(
        filename,
        filepath
    )

    print(compress_command)
    # TODO: Does this need to be a shell?
    subprocess.run(shlex.split(compress_command), shell=True)

    # Replace the original file with the new smaller and compressed image
    shutil.copyfile("content/{}".format(filename), filepath)

# TODO: Put this in a list / object
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

print(title_ids)

# TODO: Error check this
title_id = input("What title ID would you like for the game? (NOTE: only UPPERCASE letters or numbers): ")

if title_id in title_ids.keys():
    collision = title_ids[title_id]
    print(f"ERROR: This title ID already exists in title_ids.yaml for the game {collision}")
    # TODO: This shouldn't exit. Rather, it should ask if we're sure we want to do this
    # OR it should know that since the game names are the same, we're just updating
    # exit()

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
    filename = system_format.replace('$filename', game)
    file.write(get_rom(system, filename))

# TODO: Delete the core.txt and rom.txt files

mksfoex_command = "vita-mksfoex -s TITLE_ID={} \"{}\" content/param.sfo".format(
    title_id,
    game
)
print(mksfoex_command)
subprocess.run(shlex.split(mksfoex_command))

# TODO: If VPKS folder does not exist, create it

input("asfasd")

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


print(pack_vpk_command)
subprocess.run(shlex.split(pack_vpk_command))

# TODO: Print out that everything was successful and path to output VPK file