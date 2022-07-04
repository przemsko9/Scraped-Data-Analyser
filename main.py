import pandas as pd
import os
import datetime
import openpyxl
import Scripts

df_all_data = Scripts.merge_files()
df_cleaned_data = Scripts.clean_df(df_all_data)

menu_option = 9999

while menu_option != 0:
    print('\n'*10)
    print('0: Exit')
    print('1: Percentile price spread - First price')
    print('2: Percentile price spread per domain - First price')
    print('3: Category count')
    print('4: Slows analyse')
    print('5: Average discount % in groups')
    print('6: Average first price')
    print('7: Categories spread')
    print('8: Bests and slows analyse')
    print('9: % of discounted articles')
    print('99: Save Combined file')
    print('999: Repair reserved categories and composition')

    menu_option = int(input('Choose option: '))

    if menu_option == 1:
        Scripts.price_spread(df_cleaned_data)
    elif menu_option == 2:
        Scripts.price_spread_by_domain(df_cleaned_data)
    elif menu_option == 3:
        Scripts.category_count(df_cleaned_data)
    elif menu_option == 4:
        Scripts.slow_analyse(df_cleaned_data)
    elif menu_option == 5:
        Scripts.average_in_week(df_cleaned_data)
    elif menu_option == 6:
        Scripts.average_price(df_cleaned_data)
    elif menu_option == 7:
        Scripts.category_spread(df_cleaned_data)
    elif menu_option == 8:
        Scripts.best_and_slows(df_cleaned_data)
    elif menu_option == 9:
        Scripts.percent_of_discounted_items(df_cleaned_data)
    elif menu_option == 99:
        print('Saving file...')
        df_cleaned_data.to_excel('Combined Data File.xlsx')
    elif menu_option == 999:
        Scripts.repair_composition_sizes()




