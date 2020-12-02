# retroarch-bubble-generator

Python script to (semi-automatically) generate PS Vita Livearea Bubbles for your Retroarch ROMS.

# What is this?

Instead of needing to go into Retroarch on your PS Vita then choosing which ROM you want to play from there, I find it asthetically nicer and practically quicker to be able to launch games and ROMS straight from my PS Vita Livearea - but still have all the power and wonderful features of Retroarch.

This is where my script comes in, which in combination with _many_ other wonderful projects can take care of most of the hard work of generating these Liveare Bubbles for your ROMS.

# Credits

My script simply provides a tidy and simple wrapper for the amazing work already done by the community, which includes:

- [u/W00lfwang's](https://www.reddit.com/user/W00lfwang/) original [Reddit post](https://www.reddit.com/r/vitahacks/comments/hjmn5k/ps_vita_daedalusx64_and_retroarch_custom_bubbles) describing the process for generating custom bubbles, and
- [SayianPrinceVegeta](https://www.youtube.com/channel/UCjnHt3Hiz7DUzXGwCHY3EWA) for making a [YouTube video](https://youtu.be/umg2zbt-ydo) documenting the process. This was a big help, and praise the YouTube Algorithm lord for recommending me this in the first place and inspiring me to automate the process
- The team behind [vita-toolchain](https://github.com/vitasdk/vita-toolchain) which is included in this repo and allows for the creating of the VPK files
- Also included here is [pngquant](https://pngquant.org/) which compresses the images for use on the Vita
- And credit to many other amazing open source projects which make this all possible in the first place like to [Rinnegatamante](https://github.com/Rinnegatamante) and to the [Retroarch](https://www.retroarch.com/) team

https://forums.libretro.com/t/one-game-bubbles-for-retroarch-on-playstation-vita-50-120/15316

# Prerequisites

The script runs using [python3](https://www.python.org/downloads/), and only requires `Pillow` to be installed - check the [Installation Documentation](https://pillow.readthedocs.io/en/stable/installation.html) or run the following on your command line:

```python3 -m pip install --upgrade Pillow```

It goes without saying that you need a PS Vita with homebrew installed. [VitaShell](https://github.com/TheOfficialFloW/VitaShell/releases) is highly recommended for transfering and installing the vpk onto your Vita.

There is one more requisite, which is that your ROMS on your PS Vita need to be sorted by system - so in a folder somewhere you should have subfolders for each system you have ROMS for, and in those folders are your ROM files. E.g:

```
ux0:
└── ROMS/
    ├── GBA/
    │   └── Pokemon - Fire Red.gba
    └── NES/
        ├── Super Mario Bros.nes
        └── Tetris.nes
```

(Keep this folder structure in mind, because we'll shortly be creating a very similar one for the ROM cover arts)

# Usage

For each ROM you want to create a custom Livearea Bubble for, you need 3 different cover arts - `icon0.png` which is the Livearea icon itself, `bg.png` which is the game background once it's openned and `startup.png` which is the clickable image that launches the game. since `icon0.png` is the most important and `bg.png` and `startup.png` are less important, I've provided some example images in `examples/` you can use for your own ROMS.


All your cover art images should be orgainzed in a folder structure which is very similar to the one that stores your ROMS on your Vita, with folders for each system, a subfolder for each ROM and in these folders any cover art images. Note that if an image isn't found in a games folder it will search its parent system folder, then the parent images folder. This means that you can re-use certain images for multiple custom Liveara Bubbles without repeating the image. E.g:

```
.
├── Bubble Images/
│   ├── GBA/
│   │   ├── Pokemon - Fire Red/
│   │   │   └── icon0.png
│   │   └── startup.png
│   ├── NES/
│   │   ├── Super Mario Bros/
│   │   │   ├── icon0.png
│   │   │   └── startup.png
│   │   ├── Tetris/
│   │   │   └── icon0.png
│   │   └── startup.png
│   └── bg.png
└── retroarch-bubble-generator/
    ├── settings.yaml
    ├── main.py
    └── ...
```

If we were to create a custom bubble for `Tetris` (apart of the `NES` system) then we'd use `Bubble Images/NES/Tetris/icon0.png` as it's icon, `Bubble Images/NES/startup.png` as it's startup image and `Bubble Images/bg.png` as it's background image. If we were to create a custom bubble for `Super Mario Bros` for instance, it would have it's own unique icon and startup in the `Super Mario Bros` folder, but it would use the same background as all the other ROMS.

Personally, all my ROMS have a unique `icon0.png` icon, every system has a unique `startup.png` and _all_ bubbles have the same `bg.png` but of course this is entirely customizable to your liking.


MORE README TO COME