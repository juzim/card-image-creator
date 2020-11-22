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
Install Python 3 and pip

Clone the repository or download the files

Run `pip3 install -r requirements.txt` in the folder root

## Run
Adapt the config if needed

Run `python3 make.py`

## Todo
[x] Global config file

[x] More card configurations

[ ] Docker container

[ ] Binary builds for Windows

[ ] GUI

