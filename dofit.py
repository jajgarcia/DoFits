#!/usr/bin/python
#
# dofit.py (Based on fitxsp.py)
#
# Load data and perform a model fit using PyXspec
#
# Requires: xspec
# Make sure to set:
#           export VERSIONER_PYTHON_PREFER_32_BIT=yes
#    (only for heasoft earlier than 6.16)
#
import sys 
from xspec import *
from optparse import OptionParser
import os,os.path
import glob
from astropy.io import fits as pyfits
#import pyfits
#
# ------------------------------------------------------------------------------
#
# MAIN PROGRAM
#
#
#
version='0.1a'
date='- Tue Jul 21 11:16:23 EDT 2015 -'
author='Javier Garcia'
#
ul=[]
ul.append("usage: %prog [options] PREFIX")
ul.append("")
ul.append("Get total counts in different bands for a given observation")
ul.append("PREFIX can be a single PHA file or a group (e.g. *.pha)")
usage=""
for u in ul: usage+=u+'\n'

parser=OptionParser(usage=usage)
parser.add_option("-v","--version",action="store_true",dest="version",default=False,help="show version number")

(options,args)=parser.parse_args()

if options.version:
  print 'dofit.py version:',version,date
  print 'Author:',author
  sys.exit()

if len(args) == 0:
  parser.print_help()
  sys.exit(0)

#-----

# No chatter
#Xset.chatter = 0

# Query
Fit.query = 'yes'

# Load local models
#AllModels.lmod("relxill")

# Get current directory
currpath = os.getcwd()

# Observations path
obspath='/Users/javier/crab-hexte/rebinned-clean-observations/'

# Change dir to observations path
os.chdir(obspath)

# List of spectrum files
files=glob.glob(args[0])


#----- LOOP OVER OBSERVATIONS ---#
for specfile in files:

  # Change dir to observations path
  os.chdir(obspath)

  # Check if specfile exist
  if not os.path.isfile(specfile):
    print 'Warning: spectrum file',specfile,'does not exist!'
    print 'Skiping...'

  else:  # Here I need to discriminate between pcu, mjd, etc...

    # Load data
    s1 = Spectrum(specfile);

    # Go back to the working directory
    os.chdir(currpath)

    # Exposure time
    et = s1.exposure

    # Ignore/notice data
    s1.ignore("0.-20.,250.-**")

    # Define the Model
    m1 = Model("const*tbabs*pow")

    m1(1).values = "1. -1"
    m1(2).values = "0.34 -1"
    m1(3).values = "2.0 1"
    m1(4).values = "10. 1"

    # Fit
    Fit.renorm()
    Fit.perform()

    # Create and open a log file
    logFile = Xset.openLog('complete/fit-'+specfile+'.log')
    logFile = Xset.log

    # Calculate Errors
    Fit.error("maximum 20. 2.706 3 4")

    # Close currently opened log file.
    Xset.closeLog()

    # Equivalent to show all
    logFile = Xset.openLog('complete/fit-'+specfile+'.txt')
    logFile = Xset.log
    s1.show()
    m1.show()
    Fit.show()
    Xset.closeLog()

    # Get total flux
    AllModels.calcFlux("20. 250.")
    fx = s1.flux

    outfile='complete/fit-'+specfile+'.fluxes'
    f = open(outfile, 'w')
    f.write('# Mean Fluxes: Total ---\n')
    f.write(str(fx[0])+'\n')
    f.close()

    # Get residuals for all channels
    s1.notice("**")
    Plot.xAxis = "keV"
    Plot("residuals")
    xvals = Plot.x()     # Center bin energy (keV)
    yvals = Plot.y()     # Residuals: Data-Model (counts/sec/keV)
    xErrs = Plot.xErr()  # Half of bin width (keV)
    yErrs = Plot.yErr()  # Sigma: Error bar (counts/sec/keV)

    outfile='complete/fit-'+specfile+'.res'
    f = open(outfile, 'w')
    for i in range(len(xvals)):
      f.write(str(xvals[i])+' '+str(xErrs[i])+' '+str("%1.8f" %yvals[i])+' '+str(yErrs[i])+'\n')
    f.close()

    outfile='complete/fit-'+specfile+'.error'
    f = open(outfile, 'w')
    f.write('Param   Value   Low_lim    Up_lim\n')
    f.write(str(m1(3).values[0])+' '+str(m1(3).error[0])+' '+str(m1(3).error[1])+'\n')
    f.write(str(m1(4).values[0])+' '+str(m1(4).error[0])+' '+str(m1(4).error[1])+'\n')
    f.close()

    # Unload data
    AllData -= s1

    # Unload the model
    AllModels.clear()

# Output
#
#
sys.exit()
# ------------------------------------------------------------------------------
