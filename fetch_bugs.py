import os
import sys
import string

import debianbts

package = "sl"
bug_list = []
file = "C:\\bug_report.txt"
file_handle = open(file, 'w')

(num_of_bugs, header, bugs_list) = debianbts.get_reports(package)

if num_of_bugs:
    for x in bugs_list:
        (sub_bugs_header, sub_bugs_list) = x
        for x in sub_bugs_list:
            break_bugs = x.split(':')
            bug_num = string.lstrip(break_bugs[0], '#')
            data = debianbts.get_report(bug_num, followups=True)
            file_handle.write(data[0] + "\n\n")
            for x in data[1]:
                file_handle.write(x)
                file_handle.write("\n")
            file_handle.write("\n\n\n")
            file_handle.flush()