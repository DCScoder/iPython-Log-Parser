#################################################################################
#   Copyright © 2019 DCScoder
#
#                                    ~ iPython Log Parser ~
#
#   Description:  Parses console logs from iPython console history file and
#                 exports into custom .xlsx report for further review
#
#   Usage:        python ipython_log_parser.py input_dir output_dir
#
#   Artefacts:    Console history logs
#
#   Change Log:   v1.0  Initial release decoding of history.sqlite
#
#################################################################################

import sqlite3
import hashlib
import re
import xlsxwriter
import sys
import os

__version__ = 'v1.0'
__author__ = 'DCScoder'
__email__ = 'dcscoder@gmail.com'

# Input/Output directory paths
input_dir = os.path.join(sys.argv[1])
output_dir = os.path.join(sys.argv[2])

# Read 16 byte file header to confirm file type is SQLite database
def check_file_signature(input_dir):
    file_header = b'\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00'
    f = open(input_dir, "rb")
    header_data = f.read(16)
    result = re.match(file_header, header_data)
    if result:
        return True
    else:
        return False

# Returns data from binary file
def get_logs(input_dir):
    # Connect to database
    try:
        connection = sqlite3.connect(input_dir)
        c = connection.cursor()
    except sqlite3.DatabaseError:
        sys.exit("\nCould not connect to SQLite database!")

    # Execute SQL queries
    try:
        print("\nAnalysing SQL data...")
        log_data = c.execute("SELECT history.SESSION, history.LINE, sessions.START, sessions.END, sessions.NUM_CMDS, "
                             "history.SOURCE, history.SOURCE_RAW FROM history LEFT JOIN sessions ON sessions.SESSION = "
                             "history.SESSION ORDER BY history.SESSION").fetchall()
    except sqlite3.DatabaseError:
        sys.exit("\nCould not execute SQL queries!")
    c.close()
    return log_data

def main():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~ iPython Log Parser " + __version__ + " developed by", __author__ + " ~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    sig_check_result = check_file_signature(input_dir)
    if sig_check_result == True:
        print("\nFile signature check undertaken: positive match")
    else:
        sys.exit("\nFile signature check undertaken: negative match")

    print("\nPython script initialised...")

    # Read all bytes from file
    print("\nReading file...\n")
    f = open(input_dir, "rb")
    all_data = f.read()
    total_bytes = len(all_data)
    print(total_bytes, "bytes read")

    # Create MD5 and SHA1 hash values of binary file
    print("\nCreating MD5 and SHA1 hashes of file...")
    my_hash_1 = hashlib.md5()
    my_hash_2 = hashlib.sha1()
    my_hash_1.update(all_data)
    my_hash_2.update(all_data)
    hash_string_1 = my_hash_1.hexdigest()
    hash_string_2 = my_hash_2.hexdigest()
    filehash = print("\nMD5 Hash:", hash_string_1)
    filehash = print("SHA1 Hash:", hash_string_2)

    # Returns decoded data from binary file
    log_data = get_logs(input_dir)

    # Artefacts
    headings = ("Session No", "Line ID", "Start Time", "End Time", "CMD Total", "Source Data", "Source RAW Data")

    print("\nGenerating reports...")

    # .xlsx creation
    try:
        workbook = xlsxwriter.Workbook(os.path.join(output_dir, "iPython_report.xlsx"))
        worksheet_1 = workbook.add_worksheet("Console Logs")
        worksheet_2 = workbook.add_worksheet("Notes")
    except:
        sys.exit("\nUnable generate .xlsx report!")

    # .xlsx format
    format1 = workbook.add_format()
    format1.set_font_size(12)
    format1.set_bold()
    format2 = workbook.add_format()
    format2.set_font_size(12)
    format2.set_bold()
    format2.set_align('center')
    format3 = workbook.add_format()
    format3.set_align('center')
    row = 0
    col = 0
    worksheet_1.set_tab_color('#5DADE2')
    worksheet_2.set_tab_color('red')
    worksheet_1.set_column('A:B', 11, format3) + worksheet_1.set_column('C:D', 25, format3)
    worksheet_1.set_column('E:E', 11, format3) + worksheet_1.set_column('F:G', 75) + worksheet_2.set_column('A:A', 50)
    worksheet_2.write("A1", "Notes", format1)
    worksheet_2.write("A3", "This report was generated utilising iPython Log Parser " + __version__ + ".")
    worksheet_1.write_row(row, col, headings, format2)

    try:
        print("\nProcessing records...")
        # Single loop for all data formats
        for log_entry in log_data:
            log_entry = list(log_entry)
            row += 1

            # Write .xlsx
            worksheet_1.write_row(row, col, log_entry)

        print("\nProcessing completed.")
    except:
        print("\nUnable to process records, source data structure may have changed.")

    workbook.close()

    print("\nSee user defined directory path for reports.")

if __name__ == "__main__":
    main()