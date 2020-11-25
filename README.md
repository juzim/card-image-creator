# Create printable image/text combinations

This scripts helps you create printable pdf files of images with text below. My use-case is to have an easy way of creating RFID-cards for my kid's [Phonieboxes](http://phoniebox.de/).

## Example
### File list

![alt text](repo/example_images.png)

### Result

![alt text](repo/example_result.png)

## Features
- Puts image on top and filename as text below
- Turns "__" into linebreaks
- Resizes the image (aspect ratio must be 1:1)
- Additional configuration for each image by adding a text file with the same name (yaml syntax)
    - Font family
    - Fixed, max and min font size
    - Font color
    - Custom Text
    - Background Colors (todo)
- Splits result into multiple pages
- Archives processed images
- Chooses best font-size for text length 


## Installation
1. Download/clone the repository

2. Setup the default font 
You have to point the config key 'font' to a valid font file.

Example:

```
font_folder: C:\Windows\Fonts # Windows
font: ariblk.ttf
```

3. Put images in the `images` folder
The text gets extracted from the filename (if not specified in the card config file, see below). 

4. (Optional) customize cards
All card-specific config values can be overwritten by putting them in a yaml file with the same name as the image. The text can also be changed in the file.

### Python
Install Python 3 and pip

Clone the repository or download the files

Run `pip3 install -r requirements.txt` in the folder root

Run `python3 make.py`

### Windows
Execute the `make.exe` file


## Result
The result files are generated in the `result` folder. If the config value `archive` is set, the processed files are moved to the archive folder.

## Todo
[x] Global config file

[x] More card configurations

[ ] Docker container

[x] Binary builds for Windows

[ ] GUI

[ ] Add way to split text in title and subtitle

[ ] Include default fonts

[ ] Config for input and archive folders

[ ] Add some tests

[ ] Make text processing configurable ('__' etc)

[ ] Clean up config values