import csv
import html
import os
from prettytable import PrettyTable

def make_html(csv_name):
    with open(csv_name, 'r') as f:
        data = f.readlines()
    for i in range(0, len(data)):
        data[i] = data[i].replace("\n", "")
    table = PrettyTable(["State", "City/County", "Ordinance", "Site"])
    for i in range(1, len(data)):
        row = data[i].split(",")
        url = r'<a href="%s">%s</a>' % (row[2], row[2])
        table.add_row([row[0], row[1], url, row[3]])
    code = table.get_html_string(format=True)
    code = html.unescape(code)
    file_name = r"%s" % os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/index.html'
    print(file_name)
    html_file = open(file_name, 'w')
    html_file = html_file.write(code)

if __name__ == '__main__':
    target = input("File you'd like to compile: ")
    make_html(target)