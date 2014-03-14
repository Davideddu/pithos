# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2014 Davide Depau <me@davideddu.org>
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.

# NOTE: By using this software you agree to use it in a legal way.
# I cannot be held responsible for the use the users make of this plug-in.
### END LICENSE

import logging
from pithos.plugin import PithosPlugin
from pithos.pithosconfig import get_data_file
from gi.repository import GLib, Gtk
from mutagenx import mp4

class DownloadPlugin(PithosPlugin):
    preference = 'download'
    
    def on_prepare(self):
        self.downloadbtn = Gtk.ToolButton()
        self.downloadbtn.set_label("Download playing song")
        self.downloadbtn.set_tooltip_text("Save playing song to your computer for off-line listening.")
        self.downloadbtn.set_stock_id("gtk-save")
        self.downloadbtn.connect("clicked", self.download_playing_song)

        self.toolbar = self.window.builder.get_object("toolbar")
        sepitem = self.window.builder.get_object("separatoritem")

        n = self.toolbar.get_item_index(sepitem)
        self.toolbar.insert(self.downloadbtn, n + 1)
        self.downloadbtn.show()

        self.downloadmi = Gtk.ImageMenuItem.new_with_mnemonic("_Download this song...")
        self.downloadmi.set_tooltip_text("Save this song to your computer for off-line listening")
        self.downloadmi.set_image(self.window.builder.get_object("imagesave"))
        self.downloadmi.connect("activate", self.on_menuitem_download)
        self.window.builder.get_object("song_menu").insert(self.downloadmi, 5)
        self.downloadmi.show()

    def on_enable(self):
        pass

    def on_disable(self):
        self.toolbar.remove(self.downloadbtn)


    def download_playing_song(self, *ignore):
        self.download_song(self.window.current_song)

    def on_menuitem_download(self, widget):
        song = self.window.selected_song()
        self.download_song(song)

    def download_song(self, song):
        dialog = Gtk.FileChooserDialog("Download to...", None, Gtk.FileChooserAction.SAVE)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_SAVE, 1)
        dialog.set_default_response(1)

        fname = song.artist + " - " + song.songName + ".mp4"
        for i in ("<", ">", ":", "\"", "%", "/", "\\", "|", "?", "*"):
            fname.replace(i, "")

        dialog.set_current_name(fname)
        dialog.set_do_overwrite_confirmation(True)

        try:
            if dialog.run() == 1:
                filename = str(dialog.get_filename())
            else:
                return
        finally:
            dialog.destroy()

        def download(song, output):
            try:
                f = open(output, "w")
                u = urllib2.urlopen(song.audioUrlMap["highQuality"]["audioUrl"])
                f.write(u.read())
            finally:
                f.close()
                u.close()

            a = mp4.MP4(output)
            a['\xa9nam'] = song.songName
            a['\xa9alb'] = song.album
            a['\xa9ART'] = song.artist
            a['purl'] = song.songDetailURL

            try:
                u = urllib2.urlopen(song.artRadio)
                art = u.read()

                a['covr'] = [mp4.MP4Cover(art)]
            finally:
                a.save()
                u.close()


        def callback(*args):
            self.window.worker_run(time.sleep, (1.5,), lambda *args: None, "Download finished.")

        self.window.worker_run(download, (song, filename), callback, "Downloading {name} by {artist}...".format(name=song.songName, artist=song.artist))