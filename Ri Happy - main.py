from Ri_Happy_Beautiful_Soup import load_all_products
from spreadsheet_merge import merge_excel_spreadsheets


load_all_products('https://tinyurl.com/56adzpyw', 'Asc')

load_all_products('https://tinyurl.com/ybt2xbnm', 'Des')

merge_excel_spreadsheets('product_discountsAsc.xlsx', 'product_discountsDes.xlsx')

