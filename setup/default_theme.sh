#!/bin/bash

# Autostart script to set the default theme and wallpaper

# See if overwriting the default theme is enabled
override_theme=$(awk -F'=' '/override_theme/{print ($2=="True")?"True":"False"}' ~/.config/thintrust/override_theme)

# If the override_theme is set to False, exit
if [ "$override_theme" == "False" ]; then
    exit
fi

# Set the wallpaper
gsettings set org.cinnamon.desktop.background picture-uri "file:///usr/share/wallpapers/wallpaper.svg"

# Set the theme
gsettings set org.cinnamon.desktop.interface gtk-theme "Adwaita-dark"

# Set the icon theme
gsettings set org.cinnamon.desktop.interface icon-theme "Papirus-Dark"

# Set the cursor theme
gsettings set org.cinnamon.desktop.interface cursor-theme "mate-black"

# Set the Cinnamon theme
gsettings set org.cinnamon.theme name "BlueMenta"