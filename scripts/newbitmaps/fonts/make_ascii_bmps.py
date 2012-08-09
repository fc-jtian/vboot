#!/usr/bin/python -tt
# Copyright (c) 2011 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import optparse
import os
import subprocess
import sys
import tempfile

chars = '* 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ{}-_'

def main():
  """Convert a set of text chars into individual BMPs.

  This uses ImageMagick, so don't run it inside the build chroot.
  Not all characters in the world are supported.
  """

  parser = optparse.OptionParser()
  parser.description = ' '.join(main.__doc__.split())
  parser.add_option("--foreground", default='#000000',
                    dest="fg", action="store", metavar="COLOR",
                    help="foreground color (%default)")
  parser.add_option("--background", default='#ffffff',
                    dest="bg", action="store", metavar="COLOR",
                    help="background color (%default)")
  parser.add_option("--font", default='Droid Sans',
                    dest="font", action="store",
                    help="font to use (%default)")
  parser.add_option("--size", default='15', metavar="POINTSIZE",
                    dest="size", action="store",
                    help="font size (%default)")
  parser.add_option('--dir', default='./outdir',
                    dest="outdir", action="store",
                    help="output directory (%default)")
  (options, args) = parser.parse_args()

  if not os.path.isdir(options.outdir):
    os.mkdir(options.outdir)

  # ARM U-Boot is very picky about its BMPs. They have to have exactly 256
  # colors in their colormap. Imagemagick generally tries to reduce the
  # colormap when it can, so we have to play some games to force it not to.
  # We'll create a gradient file with 256 colors, and then make sure that all
  # our rendered characters use the same colormap. This makes the resulting
  # images larger, but it also means they'll work on x86 too. Sigh.
  (handle, gradient_file) = tempfile.mkstemp(".png")
  os.close(handle)

  cmd = ('convert', '-size', '256x1',
         'gradient:%s-%s' % (options.fg, options.bg),
         gradient_file)
  print ' '.join(cmd)
  subprocess.call(cmd)


  count=0
  for ascii in chars:
    pngfile = os.path.join(options.outdir,
                           "idx%03d_%x.png" % (count,ord(ascii)))
    bmpfile = os.path.join(options.outdir,
                           "idx%03d_%x.bmp" % (count,ord(ascii)))
    cmd = ('pango-view', '-q', '--no-auto-dir',
           '--background=%s' % options.bg,
           '--foreground=%s' % options.fg,
           '--font="%s %s"' % (options.font, options.size),
           '--dpi', '72',
           '--margin', '0',
           '--text="%s"' % ascii,
           '-o', pngfile)

    cmd = ' '.join(cmd)
    print cmd
    os.system(cmd) # This must be run in a subshell for correct font rendering.

    cmd = ('convert',
           '-bordercolor', options.bg,
           '-border', '0x3',
           '-resize', '59%x78%',          # Scale the same as other images.
           '-colors', '256',
           '-remap', gradient_file,
           '-compress', 'none',
           '-alpha', 'off',
           pngfile,
           bmpfile)
    print ' '.join(cmd)
    count += 1
    subprocess.call(cmd)

  os.unlink(gradient_file)


# Start it all off
if __name__ == '__main__':
  main()