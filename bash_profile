source ~/.profile

#
# don't put duplicate lines in the history. See bash(1) for more options                                                          
# don't overwrite GNU Midnight Commander's setting of `ignorespace'.                                                              
# ... or force ignoredups and ignorespace                                                                                         
#
export HISTCONTROL=$HISTCONTROL${HISTCONTROL+,}ignoredups
export HISTCONTROL=ignoreboth

#
# Setup C library paths
#
export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH
#export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH_PATH
export CPATH=/usr/local/include:$CPATH


#
# Adding arduino tools to command line
#
export PATH=$PATH:/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin

#
# Adding ArduPilot Testing Environment
#
export PATH=$PATH:$HOME/Code/THIRD_PARTY/UAVs/ardupilot-diydrones/Tools/autotest
export PATH=$PATH:$HOME/Code/THIRD_PARTY/UAVs/MAVProxy
export PATH=$PATH:$HOME/Code/THIRD_PARTY/UAVs/mavlink/pymavlink/examples
export PATH=$PATH:$HOME/Code/THIRD_PARTY/UAVs/jsbsim/src

#
# PYTHON Path setup
#
export PYTHONPATH="/Users/njoubert/Library/Enthought/Canopy_64bit/User/lib/python2.7/site-packages/:$PYTHONPATH"
export PATH="/Users/njoubert/Library/Enthought/Canopy_64bit/User/bin:$PATH"

#
# Adding "brew install coreutils" bins to our path
#
PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
MANPATH="/usr/local/opt/coreutils/libexec/gnuman:$MANPATH"

#
# Andrew Tridgell's function to extract current git branch
#
function parse_git_branch {
  /usr/bin/git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1)/'
}

#
# Set up pretty command prompt with nice colors.
#
function proml {
  local      NORMAL="\[\033[0;0m\]"
  local        BLUE="\[\033[0;34m\]"
  local       BLACK="\[\033[0;30m\]"
  local         RED="\[\033[0;31m\]"
  local   LIGHT_RED="\[\033[1;31m\]"
  local       GREEN="\[\033[0;32m\]"
  local LIGHT_GREEN="\[\033[1;32m\]"
  local       WHITE="\[\033[1;37m\]"
  local  LIGHT_GRAY="\[\033[0;37m\]"
  local  LIGHT_PINK="\[\033[0;35m\]"
  case $TERM in
    xterm*|screen*)
    TITLEBAR='\[\033]0;\u@\h:\w\007\]'
    ;;
    *)
    TITLEBAR=""
    ;;
  esac

  PS1="${TITLEBAR}$LIGHT_PINK\u@$GREEN\h:$BLUE\w$LIGHT_PINK\$(parse_git_branch)$NORMAL\\$ "
  PS2='> '
  PS4='+ '
}
proml


#
# Setup more verbose git output
#

GIT_MERGE_VERBOSITY=2

##
# Your previous /Users/njoubert/.bash_profile file was backed up as /Users/njoubert/.bash_profile.macports-saved_2015-09-17_at_18:09:56
##

# MacPorts Installer addition on 2015-09-17_at_18:09:56: adding an appropriate PATH variable for use with MacPorts.
export PATH="/opt/local/bin:/opt/local/sbin:$PATH"
# Finished adapting your PATH environment variable for use with MacPorts.

