# This code is by Peter Otten.
# This does look to do what I want but doesn't look very flexible.
# Will study it later.
#import sys 
#import logging 
# 
#logger = logging.getLogger("my_app") 
#logger.setLevel(logging.DEBUG) 
#
#x = 2
# 
#class LevelFilter(logging.Filter): 
#     def __init__(self, level): 
#         self.level = level 
#     def filter(self, record): 
#         return self.level == record.levelno 
# 
#def make_handler(outstream, format, level): 
#     handler = logging.StreamHandler(outstream) 
#     formatter = logging.Formatter(format) 
#     handler.setFormatter(formatter) 
#     handler.addFilter(LevelFilter(level)) 
#     return handler 
# 
#if (x == 1) is True:
#    logger.addHandler(make_handler(sys.stderr, 
#       'STDERR %(levelname)s %(message)s', logging.WARN)) 
#logger.addHandler(make_handler(sys.stdout, 
#     'STDOUT %(levelname)s %(message)s', logging.INFO)) 
# 
#logger.info("the world is flat") 
#logger.warning("take care not to fall off its rim")


# I was tired of Python's logger module. The documentation doesn't seem to be very good. :-(

# Following Unix KISS logic, I'm keeping it simple
# I guess, my requirement doesn't require a complete logging facility

# This simple trick came to my mind after 2 weeks of fiddling with logger.
# I'm a dork. Developing Programming Skills is really going to take its own time.

# Will enhance it more later....

import sys

class log:
    '''A OOP implementation for logging.
    warnings is to tackle the warning option
    verbose is to tackle the verbose option
    debug is to tackle the debug option
    
    You should pass these options, taking it from optparse/getopt,
    during instantiation'''
    
    def __init__(self, warnings, verbose, debug):
        
        if warnings is True:
            self.WARN = True
        else: self.WARN = False
        
        if verbose is True:
            self.VERBOSE = True
        else: self.VERBOSE = False
        
        if debug is True:
            self.DEBUG = True
        else: self.DEBUG = False
        
    def msg(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()
        
    def err(self, msg):
        sys.stderr.write(msg)
        sys.stderr.flush()
    
    # For the rest, we need to check the options also
    def warn(self, msg):
        if self.WARN is True:
        #if pypt_variables.options.warnings is True:
            sys.stderr.write(msg)
            sys.stderr.flush()

    def verbose(self, msg):
        if self.VERBOSE is True:
        #if pypt_variables.options.verbose is True:
            sys.stdout.write(msg)
            sys.stdout.flush()
            
    def debug(self, msg):
        if self.DEBUG is True:
        #if pypt_variables.options.debug is True:
            sys.stdout.write(msg)
            sys.stdout.flush()

#def log(msg, log_level):
#    
#    if log_level == "MSG":
#        sys.stdout.write(msg)
#        sys.stdout.flush()
#        return
#    
#    if log_level == "ERR":
#        sys.stderr.write(msg)
#        sys.stderr.flush()
#        return
#        
#    if log_level == "VERBOSE":
#        if pypt_variables.options.verbose is True:
#            sys.stdout.write(msg)
#            sys.stdout.flush()
#            return
#    
#    if log_level == "WARNING":
#        if pypt_variables.options.warnings is True:
#            sys.stderr.write(msg)
#            sys.stderr.flush()
#            return