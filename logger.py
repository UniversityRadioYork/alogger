#!/usr/bin/python

from subprocess import Popen, PIPE
from time import time, sleep
from multiprocessing import Process
from sys import stdout, stderr
from os import remove, lstat, listdir
from re import match
from struct import unpack_from

#import audiotools

#import imp
#imp.load_source('pyaudio','./pyaudio-git/src/pyaudio.py')
#import pyaudio

class Logger:

  def __init__(self, location='.', bits=16, signed=True, littleendian=True, rate=44100, channels=2, chunkseconds=300, logmaxage=60*60*24*42, fileextension='raw'):

    # TODO : sanitize inputs
    self.__rate = rate
    self.__channels = channels
    self.__chunkseconds = chunkseconds
    self.__logmaxage = logmaxage
    self.__location = location
    self.__bits = bits
    self.__signed = signed
    self.__fileextension = fileextension
    self.__littleendian = littleendian

    # work out the filesize of the audio chunk
    framesize = self.__channels * (self.__bits // 8)
    bytespersec = framesize * self.__rate
    self.__chunkbytes = bytespersec * self.__chunkseconds



  def __amplitude_percent(amptotal, samples = 44100, limit = 2**15-1):
    avg = amptotal / samples
    percent = (100.0 / limit) * avg
    return percent

  def __check_2(percntage):
    pass

  def __check(filename, stero=True):
    #could check for mono
    numberofsamples = 0
    amplitude_l = 0
    amplitude_r = 0
    with open(filename,'rb') as f:
      while True:
        data = f.read(4)
        if data:
          l, r = unpack_from('<hh',data)
          l, r = abs(l) , abs(r)
          amplitude_l += l
          amplitude_r += r
          numberofsamples += 1
        else:
          break
    if stero:
      percent = self.__amplitude_percent(amplitude_l + amplitude_r, 2 * numberofsamples, 2.0**15)
    else:
      percent_l = self.__amplitude_percent(amplitude_l, numberofsamples, 2.0**15)
      percent_r = self.__amplitude_percent(amplitude_r, numberofsamples, 2.0**15)
      

  def __removeold(self): 
    checkinterval = self.__chunkseconds // 2
    filesearch = "^[0-9]+\.{0:s}$".format(self.__fileextension)
    try:
      while (True):
        # idle for a while
        sleep(checkinterval)

        # list deletion candidates
        files = listdir('.')
        files=[filename for filename in files if filename[0] != '.']
        files=[filename for filename in files if match(filesearch, filename)]

        # look for and remove old files
        for filename in files:
          try: 
            stat_info = lstat(filename)
          except:
            stderr.write("{0:s}: No such file or directory\n".format(filename))
            continue
          if (stat_info.st_mtime < time() - self.__logmaxage):
            #check(filename)
            stdout.write("Removing old file ({0:s})\n".format(filename))
            remove(filename)
    except KeyboardInterrupt:
      pass

  def __createfile(self, timestamp):
    filename = str(timestamp) + '.' + self.__fileextension
    stdout.write("Creating {0:s} {1:d} bit {2:s} endian {3:d} channel {4:d} Hz raw audio file ({5:s})\n".format('signed' if self.__signed else 'unsigned', self.__bits, 'little' if self.__littleendian else 'big', self.__channels, self.__rate, filename))
    return open(filename,'wb')

  def run(self):
    p1 = Process(target=self.__removeold)
    p1.start()

    # align timing
    stdout.write("Aligning timing to the nearest {0:d} seconds\n".format(self.__chunkseconds))
    now = time()
    sleep(self.__chunkseconds - (now % self.__chunkseconds))
    timestamp = int(time())
    stdout.write("Aligned at unix timestamp {0:d}\n".format(timestamp))

    # initial logfile
    try:
      logfile = self.__createfile(timestamp)
      
      # record

      if self.__signed:
        arformat = 'S' 
      else:
        arformat = 'U'
      arformat += "{0:d}_".format(self.__bits)
      if self.__littleendian:
        arformat += "LE"
      else:
        arformat += "BE"
      cmd =['arecord', '-c', str(self.__channels), '-f', arformat, '-r', str(self.__rate), '-t', 'raw']

      try:
        p = Popen(cmd, stdout=PIPE)
      
        written = 0
        buffersize = 2*1024

        while (True):
          # read a buffer
          buf = p.stdout.read(buffersize)
          written += len(buf)
          if (written >= self.__chunkbytes):
            # last bytes required
            nextwrite = written - self.__chunkbytes
            towrite = len(buf) - nextwrite
            logfile.write(buf[:towrite])
            logfile.flush()
            logfile.close()

            # next audiolog file
            timestamp += self.__chunkseconds
            logfile = self.__createfile(timestamp)

            # overflow bytes
            if (nextwrite != 0):
              logfile.write(buf[towrite:]) # resyncs the buffer with reads
            written = nextwrite
          else:
            logfile.write(buf)
      
      finally:
        p.terminate()
    
    finally:
      logfile.flush()
      logfile.close()

if __name__ == "__main__":
  try:
    l = Logger(chunkseconds=5, logmaxage=60)
    l.run()
  except KeyboardInterrupt:
    print('KeyboardInterrupt')


  # 2 bytes pairs constantly around 0x0000 hence 0xff00 -> 0x00ff is quite
  # 2 bytes pairs peaking ??? not sure what it looks like

  # absolute the 16 bits to give 8 bits positive
  # < 5% over 1 min then silence
  # > 85% over 1 min then peaking


  """import pyaudio
  import sys

  chunk = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 2
  RATE = 44100
  RECORD_SECONDS = 20

  p = pyaudio.PyAudio()

  stream = p.open(format = FORMAT,
                  channels = CHANNELS, 
                  rate = RATE, 
                  input = True,
                  output = False,
                  frames_per_buffer = chunk)

  print "* recording"
  for i in range(0, 44100 / chunk * RECORD_SECONDS):
      data = stream.read(chunk)
      # check for silence here by comparing the level with 0 (or some threshold) for 
      # the contents of data.
      # then write data or not to a file

  print "* done"

  stream.stop_stream()
  stream.close()
  p.terminate()"""


