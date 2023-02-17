'''
2021-09-30 Kei Moriya

Run all create_*.py tests.

'''

import os
import sys
import subprocess

test_files = ['create_2col_fig.py',  'create_area.py', 'create_daily_html.py',
              'create_dual_y.py', 'create_hline_vline.py', 'create_html.py',
              'create_line_bar.py']

failures = []
for itest, test_file in enumerate(test_files):
    if not os.path.isfile(test_file):
        print('File ' + test_file + ' does not exist')
        continue

    print('Running ' + test_file + ' (' + str(itest+1) + '/' + str(len(test_files)) + ')')
    command = 'python ' + test_file
    exitcode = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if exitcode != 0:
        print('    FAILED for ' + test_file)
        failures.append(test_file)

print('Failed tests: (' + str(len(failures)) + ')')
print('\n'.join(failures))

          
