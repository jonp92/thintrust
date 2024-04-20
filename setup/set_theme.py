#!/usr/bin/env python3

from gi.repository import Gio

def set_theme():
    gsettings_bg = Gio.Settings.new('org.cinnamon.desktop.background')
    gsettings_bg.set_string('picture-uri', 'file:///usr/share/wallpapers/wallpaper.svg')
    gsettings_bg.apply()

    gsettings_interface = Gio.Settings.new('org.cinnamon.desktop.interface')
    gsettings_interface.set_string('gtk-theme', 'Adwaita-dark')
    gsettings_interface.set_string('icon-theme', 'Papirus-Dark')
    gsettings_interface.set_string('cursor-theme', 'mate-black')

    gsettings_theme = Gio.Settings.new('org.cinnamon.theme')
    gsettings_theme.set_string('name', 'BlueMenta')

if __name__ == "__main__":
    set_theme()