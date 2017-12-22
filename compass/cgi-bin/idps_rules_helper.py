#!/usr/bin/python

import re
import sys
import subprocess
from Cheetah.Template import Template
from optparse import OptionParser
from endian.core.logger import *

ICMP_PATTERN    = r'" icmp "'
SID_PATTERN     = r"sid:\s*(\d{1,10})\s*;"
COMMENT_FLAG    = r'"^#"'

def dumpSids(sid_list, separator):
    print separator.join(sid_list)
    

def getIcmpSids(directories):
    icmp_sids = []
    directory_list = directories.split("_##_");
    debug("directoris: %s", directory_list)
    for directory in directory_list:
        cmd = r"grep -v " + COMMENT_FLAG + " " + directory + r"/*.rules | grep " + ICMP_PATTERN
        debug("cmd: %s", cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            search_result = re.search(SID_PATTERN, line)
            if(search_result != None):
                icmp_sids.append(search_result.group(1))
            else:
                debug("line: %s",line)
        retval = p.wait()
    return icmp_sids

def dumpSearchResults(search_results, separator):
    print separator.join(search_results)
        

def searchFromSidAndMsg(directories, key_word):
    potential_rules = []
    search_results = []
    directory_list = directories.split("_##_");
    debug("directoris: %s", directory_list)
    search_pattern_1 = r'^\s*\w{3,8}\s+(?P<protocol>\w{2,5}).*' + r'\(msg:"(?P<msg>[^"]*' + key_word + r'[^"]*)"' + r'.*sid:\s*(?P<sid>\d{1,10})\s*;.*'
    search_pattern_2 = r'^\s*\w{3,8}\s+(?P<protocol>\w{2,5}).*' + r'\(msg:"(?P<msg>[^"]*)"' + r'.*sid:\s*(?P<sid>\d{,10}' + key_word + r'\d{,10})\s*;.*'

    if key_word == "":
        key_word = '""'
    for directory in directory_list:
        cmd = r"grep --no-filename -v " + COMMENT_FLAG + " " + directory + r"/*.rules | grep -i " + r'"' + key_word + r'"'
        debug("cmd: %s", cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        potential_rules.extend(p.stdout.readlines())
        retval = p.wait()

    for potential_rule in potential_rules:
        debug(potential_rule)
        m1 = re.match(search_pattern_1, potential_rule, re.I)
        if( m1 != None):
            search_results.append("#__#".join(m1.groups()))
        else:
            m2 = re.match(search_pattern_2, potential_rule, re.I)
            if( m2 != None):
                search_results.append("#__#".join(m2.groups()))

    return search_results

if __name__ == '__main__':
    usage = "usage: %prog [-d] [-f dir1_##_dir2_##_...]\n" + \
            "       %prog [-d] [-s dir1_##_dir2_##_... keyword]\n"
    parser = OptionParser(usage)
    parser.add_option(  "-d", "--debug", dest="debug",
                        action="store_true",
                        help="Be more verbose", default=False)
    parser.add_option(  "-f", "--find_icmp_rules", dest="findIcmpRules",
                        action="store_true",
                        help="Find rules with icmp, their sids will be returned", default=False)
    parser.add_option(  "-s", "--search", dest="search",
                        action="store_true",
                        help="Search key word in fields 'msg'&'sid' of rules", default=False)
    

    (options,args) = parser.parse_args()

    if options.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if(options.findIcmpRules):
        if( len(args) == 1 ):
            dumpSids(getIcmpSids(args[0]), '#')
            sys.exit(0)

    if(options.search):
        if( len(args) == 2 ):
            dumpSearchResults(searchFromSidAndMsg(args[0], args[1]), "_##_")
        elif( len(args) == 1 ):
            dumpSearchResults(searchFromSidAndMsg(args[0], ""), "_##_")
        sys.exit(0)
        
    parser.print_help()

