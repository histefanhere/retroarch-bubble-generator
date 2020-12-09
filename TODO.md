# TODO:

- Does this qualify for https://forums.libretro.com/t/one-game-bubbles-for-retroarch-on-playstation-vita-50-120/15316 (?)

- GUI (?)

- allow assigning ID through arguments (?)

- when asking if to use the same title ID, pressing enter should be yes and typing anything should be no / change

# COMPLETED:
- make all paths configurable in settings.yaml (and provide sane defaults)
- example settings.yaml file
- section off the code into discrete parts
- Provide basic startup.png and bg.png _somewhere_
- detailed README encorporating https://ascii-tree-generator.com/
- specify that FOLDER NAME HAS TO BE THE SAME AS ROM FILENAME
- credits
  - https://www.youtube.com/watch?v=umg2zbt-ydo&t=147s
  - https://www.reddit.com/r/vitahacks/comments/hjmn5k/ps_vita_daedalusx64_and_retroarch_custom_bubbles/?utm_medium=android_app&utm_source=share
  - https://pngquant.org/
  - https://github.com/vitasdk/vita-toolchain
- SPECIFICALLY SAY that it should only be used with ROMS you own
- provide example icon0.png
- Screenshot of the Livearea bubbles in README
- say in readme where to find cores
- use `shlex.quote` as much as I can, but it seems to be using single quotes instead of double quotes
- CLI interface for picking a system and game without going through the interactive script

# TRASHED:
- Delete the core.txt and rom.txt files _=>_ all generation content is preserved in ./content/
- auto open browser to google images if icon doesn't exist? _=>_ well this would just be annoying
- change "game" to "rom" in code _=>_ it refers to the local paths, not the paths on the vita, I don't want these to be confused
- error for missing file in README.troubleshooting _=>_ I want it to be general for all errors not just that specific one
- custom `vpk` output path? _=>_ The output VPK path isn't intented to be permanent storage (but it could be...)
