import csv

def write_destination_csv(params, state):
    workbook = state['workbook']
    output_file = params['output_file']
    for sheet in workbook.worksheets():
        title = sheet.title
        rows = sheet.get_all_values()
        with open(output_file, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
    return True
