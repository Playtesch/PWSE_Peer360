import xlsxwriter

datos = [("David", 5.2, 7.86), ("Alvaro", 6, 7.5), ("Alexis", 8.2, 9.36)]

def writeExcel(file_name, data):
    row = 1
    column = 0
    workbook = xlsxwriter.Workbook(f'{file_name}.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Evaluado')
    worksheet.write('B1', 'Nota Media')
    worksheet.write('C1', 'Nota Normalizada')
    for i in data:
        for j in i:
            worksheet.write(row, column, j)
            column += 1
        row += 1
        column = 0
    workbook.close()

writeExcel("1", datos)