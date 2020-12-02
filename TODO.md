# TODO:

- detailed README encorporating https://ascii-tree-generator.com/

- specify that FOLDER NAME HAS TO BE THE SAME AS ROM FILENAME

- auto open browser to google images if icon doesn't exist?

- credits
  - https://www.youtube.com/watch?v=umg2zbt-ydo&t=147s
  - https://www.reddit.com/r/vitahacks/comments/hjmn5k/ps_vita_daedalusx64_and_retroarch_custom_bubbles/?utm_medium=android_app&utm_source=share
  - https://pngquant.org/
  - https://github.com/vitasdk/vita-toolchain

- provide example icon0.png

- change "game" to "rom" in code

- SPECIFICALLY SAY that it should only be used with ROMS you own

- custom `vpk` output path?

- use `shlex.quote` as much as I can, but it seems to be using single quotes instead of double quotes?

- Does this qualify for https://forums.libretro.com/t/one-game-bubbles-for-retroarch-on-playstation-vita-50-120/15316 ????????

- GUI (oh boy.)

# COMPLETED:
- make all paths configurable in settings.yaml (and provide sane defaults)
- example settings.yaml file
- section off the code into discrete parts
- Provide basic startup.png and bg.png _somewhere_

# TRASHED:
- Delete the core.txt and rom.txt files _=>_ all generation content is preserved in ./content/
