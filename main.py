'''
Software to generate a more readable pdf of a detailed .csv report from Clockify.me time keeping system.

Version:        0.1
Date:           2019-08-11
Last update:    2019-08-11
Created by:     Jens Sjögren
Licence:        LGPL v3.0
'''

import csv
import html_strings

from project import Project
from fpdf import FPDF, HTMLMixin
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

# -------- Constants -------- #
VERSION = '0.1'
USER = 0
EMAIL = 1
CLIENT = 2
PROJECT = 3
TASK = 4
DESCRIPTION = 5
BILLABLE = 6
START_DATE = 7
START_TIME = 8
END_DATE = 9
END_TIME = 10
DURATION_H = 11
DURATION_DECIMAL = 12
TAGS = 13
HOURLY_RATE = 14
AMOUNT_SEK = 15


class PDF(FPDF, HTMLMixin):
    def header(self):
        # Logo
        self.image('logo.png', 160, 8, 33)
        # Arial bold 15
        self.set_font('Arial', '', 10)
        # Time stamp
        self.cell(30, 10, time_created, 0, 0, 'L')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, 'Avser period: %s' % label, 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        txt = name
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()

    def print_chapter(self, num, title):
        self.add_page()
        self.chapter_title(num, title)


print('Tidrapport avser period: ')
user_input_period = input()
print('Namn: ')
user_input_name = input()
print('Ange .csv-fil... ')

Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file

print('Spara rapport i mapp...')
directory = askdirectory()  # ask for save directory


# -------- Parse data from .csv file -------- #

projects = []
with open(filename, encoding='utf-8') as csv_file:
    csv_reader = csv.reader(x.replace('\0', '') for x in csv_file)
    next(csv_reader, None)  # skip the headers

    for row in csv_reader:
        found = False
        for project in projects:
            if row[PROJECT] in project.get_name():
                found = True
                task = row[TASK]
                if task == '':
                    task = 'Ospecifierat'
                project.add_time(task=task, time=float(row[DURATION_DECIMAL]))

        if not found:
            # add new project if not found
            new_project = Project(name=row[PROJECT])
            task = row[TASK]
            if task == '':
                task = 'Ospecifierat'
            new_project.add_time(task=task, time=float(row[DURATION_DECIMAL]))
            projects.append(new_project)


# -------- Create html content for pdf creation -------- #
time_created = datetime.now().isoformat(timespec='minutes')

text = html_strings.HTML_1 + user_input_period + html_strings.HTML_2 + \
       user_input_name + html_strings.HTML_3

total_time = 0
for project in projects:
    keys = project.get_tasks().keys()
    values = project.get_tasks().values()
    total_time += project.get_total_time()

    text += html_strings.PROJECT_1 + project.get_name() + html_strings.PROJECT_2 + str(project.get_total_time()) + \
        html_strings.PROJECT_3

    for key in keys:
        text += html_strings.TASK_1 + key + html_strings.TASK_2 + str(project.get_tasks()[key]) + html_strings.TASK_3

text += html_strings.HTML_4 + html_strings.HTML_5 + str(total_time) + html_strings.HTML_6


# -------- Create pdf -------- #
pdf = PDF()
pdf.add_page()
pdf.set_creator('Bjesses tidrapportsexpress v.' + VERSION)
pdf.write_html(text)
pdf.output(directory + '\Tidrapport ' + user_input_name + ' ' + user_input_period + '.pdf', 'F')

print('Klar!')
