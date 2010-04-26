# -*- coding: utf-8 -*-
import getopt, sys
import logging

def parameters_parse(argv, param_list, usage_callback):
    logging.debug('Parsing input data (%s)' % param_list)
    
    def add_equal(x): return '%s=' % x
    param_list = map(add_equal, param_list)

    try:                          
        opts, args = getopt.getopt(argv, "", param_list)
    except getopt.GetoptError:
        usage_callback()
        sys.exit(2)
        
    if len(opts) < len(param_list):
        usage_callback()
        sys.exit(2)
    
    result = []
    for opts_item in opts: 
        opt, arg = opts_item
        logging.debug('Parameter %s with value %s found' % (opt, arg))
        result.append(arg)
    return result