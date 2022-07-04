import numpy as np
import pandas as pd
import os
import plotly.graph_objects as pio
import matplotlib.pyplot as plt
import datetime
import openpyxl


def merge_files():
    all_data = pd.DataFrame()
    files = [file for file in os.listdir('./Files')]
    files_count = 0
    files_max = len(files)

    for file in files:
        files_count = files_count + 1
        print(f'{files_count}/{files_max}')
        df = pd.read_excel('./Files/' + file)
        file_name_split = file.split(' ')
        df['Week number'] = file_name_split[0] + ' ' + file_name_split[1]
        df['Season 2'] = df['Season']
        all_data = pd.concat([all_data, df])

    all_data = all_data.reset_index(drop=True)

    return all_data


def clean_df(df):
    print(f'Cleaning file...')
    df_clean = df[df['Product name'].notna()]
    df_clean = df_clean.reset_index(drop=True)
    df_clean = df_clean.drop_duplicates(subset=['Unique value', 'Top category', 'Week number', 'Domain'],
                                        keep='first')
    df_clean = df_clean.reset_index(drop=True)
    df_clean['Current price'] = df_clean['Price']
    df_clean['Discount'] = 0

    for i, row in df_clean.iterrows():
        if pd.notna(row['Season']):
            season = row['Season']
            season_splited = season.split(' ')
            df_clean.at[i, 'Season 2'] = season_splited[1] + ' ' + season_splited[0]
        else:
            df_clean.at[i, 'Season 2'] = 'N/A'

        if row['Discount price'] > 0:
            df_clean.at[i, 'Current price'] = row['Discount price']
            df_clean.at[i, 'Discount'] = 1 - (row['Discount price'] / row['Price'])

    df_clean['Sizes'] = df_clean['Sizes'].str.replace('Not available', 'unavailable')
    df_clean['Sizes'] = df_clean['Sizes'].str.replace('Available', 'available')
    df_clean['Sizes'] = df_clean['Sizes'].str.replace('false', 'unavailable')
    df_clean['Sizes'] = df_clean['Sizes'].str.replace('true', 'available')

    return df_clean


def price_spread(df):
    category_option = 9999

    categories = df['Top category'].tolist()
    categories = list(dict.fromkeys(categories))
    categories.sort()
    categories.insert(0, 'Exit')

    while category_option != 0:
        for i in range(len(categories)):
            print(f'{i}: {categories[i]};', end='')
            if i % 5 == 0:
                print('')

            if i == 0:
                print('\t', end='')
            elif len(categories[i]) >= 8:
                print('\t', end='')
            else:
                print('\t\t', end='')

        category_option = int(input('\nJaka kategoria: '))

        if (category_option != 0) & (category_option < len(categories)):
            category = categories[int(category_option)]
            df_filtered = df[df['Top category'] == category]
            value_25 = df_filtered['Price'].describe()[4]
            value_50 = df_filtered['Price'].describe()[5]
            value_75 = df_filtered['Price'].describe()[6]

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value'], keep='first')
            df_filtered = df_filtered.reset_index(drop=True)

            print(f'Category: {category}')
            print(f"<Ω25 {value_25}: {df_filtered[df_filtered['Price'] < value_25]['Price'].count()}")
            print(f"<Ω50 {value_50}: {df_filtered[(df_filtered['Price'] >= value_25) & (df_filtered['Price'] < value_50)]['Price'].count()}")
            print(f"<Ω75 {value_75}: {df_filtered[(df_filtered['Price'] >= value_50) & (df_filtered['Price'] < value_75)]['Price'].count()}")
            print(f">Ω75 {value_75}: {df_filtered[df_filtered['Price'] >= value_75]['Price'].count()}")

            input('Done')


def price_spread_by_domain(df):
    category_option = seasons_option = 9999
    df_filtered = df.copy()
    value_25 = value_50 = value_75 = 0.0
    chart_title = 'Chart'

    categories = df['Top category'].tolist()
    categories = list(dict.fromkeys(categories))
    categories.sort()
    categories.insert(0, 'Exit')

    seasons = df['Season 2'].tolist()
    seasons = list(dict.fromkeys(seasons))
    seasons.sort(reverse=True)
    seasons.insert(0, 'All')

    while category_option != 0:
        for i in range(len(categories)):
            print(f'{i}: {categories[i]};', end='')
            if i % 5 == 0:
                print('')

            if i == 0:
                print('\t', end='')
            elif len(categories[i]) >= 8:
                print('\t', end='')
            else:
                print('\t\t', end='')

        category_option = int(input('\nCategory select: '))

        if category_option != 0:
            print('-----------------------------------')
            for i in range(len(seasons)):
                print(f'{i}: {seasons[i]};\t', end='')
                if i % 5 == 0:
                    print('')

            seasons_option = int(input('\nSeason select: '))

        if (category_option != 0) & (category_option < len(categories)) & \
                (seasons_option != 0) & (seasons_option < len(seasons)):
            category = categories[int(category_option)]
            season = seasons[int(seasons_option)]
            df_filtered = df[(df['Top category'] == category) & (df['Season 2'] == season)]
            print(df_filtered.describe())
            value_25 = df_filtered['Price'].describe()[4]
            value_50 = df_filtered['Price'].describe()[5]
            value_75 = df_filtered['Price'].describe()[6]
            chart_title = category + ' ' + season
            print(chart_title)
        elif (category_option != 0) & (category_option < len(categories)) & \
                (seasons_option == 0):
            category = categories[int(category_option)]
            df_filtered = df[(df['Top category'] == category)]
            print(df_filtered.describe())
            value_25 = df_filtered['Price'].describe()[4]
            value_50 = df_filtered['Price'].describe()[5]
            value_75 = df_filtered['Price'].describe()[6]
            chart_title = category
            print(chart_title)

        if category_option != 0:
            df_new = df_filtered[["Product URL", "Domain", "Top category", "Product name",
                                  "Price", "Color", "Unique value", "Season 2", ]]
            df_new = df_new.drop_duplicates(subset=['Unique value'], keep='first')
            df_new = df_new.reset_index(drop=True)

            for i, row in df_new.iterrows():
                if row['Price'] < value_25:
                    df_new.at[i, 'Percentile'] = '<Ω25 ' + str(value_25)
                elif row['Price'] < value_50:
                    df_new.at[i, 'Percentile'] = '<Ω50 ' + str(value_50)
                elif row['Price'] < value_75:
                    df_new.at[i, 'Percentile'] = '<Ω75 ' + str(value_75)
                elif row['Price'] >= value_75:
                    df_new.at[i, 'Percentile'] = '>Ω75 ' + str(value_75)

            df_pivot = pd.pivot_table(df_new, index=['Percentile'], columns=['Domain'], values='Unique value',
                                      aggfunc='count')

            # show char with counted values
            '''print(df_pivot)
            df_pivot.plot(kind='bar')
            plt.xticks(rotation=90)
            plt.show()'''

            # create additional DataFrame ant show chart with percentage per percentile
            df_pivot2 = df_pivot.copy()
            for row in range(len(df_pivot)):
                for column in range(len(df_pivot.columns)):
                    df_pivot2.iat[row, column] = df_pivot.iloc[row, column] / df_pivot.iloc[:, [column]].sum()
                    df_pivot2.iat[row, column] = round(df_pivot2.iloc[row, column], 2)
            print(df_pivot2)
            df_pivot2.plot(kind='bar')
            plt.xticks(rotation=45)
            plt.title(chart_title)
            plt.show()

            input('\nDone')


def category_count(df):
    df.sort_values('Week number')

    category_option = 9999
    categories = df['Top category'].tolist()
    categories = list(dict.fromkeys(categories))
    categories.sort()
    categories.insert(0, 'All')
    categories.insert(0, 'Exit')

    seasons = df['Season 2'].tolist()
    seasons = list(dict.fromkeys(seasons))
    seasons.sort(reverse=True)
    seasons.insert(0, 'All')
    category = season = None

    while category_option != 0:
        category_option = seasons_option = 9999

        for i in range(len(categories)):
            print(f'{i}: {categories[i]};', end='')
            if i % 5 == 0:
                print('')

            if i == 0:
                print('\t', end='')
            elif len(categories[i]) >= 8:
                print('\t', end='')
            else:
                print('\t\t', end='')

        while not (category_option < len(categories)) & (category_option >= 0):
            category_option = int(input('\nCategory select: '))

        if category_option > 0:
            print('-----------------------------------')
            for i in range(len(seasons)):
                print(f'{i}: {seasons[i]};\t', end='')
                if i % 5 == 0:
                    print('')

            while not (seasons_option < len(seasons)) & (seasons_option >= 0):
                seasons_option = int(input('\nSeason select: '))

        if (category_option > 1) & (seasons_option != 0):
            category = categories[category_option]
            season = seasons[seasons_option]
            df_filtered = df[df['Top category'] == category]
            df_filtered = df_filtered[df_filtered['Season 2'] == season]

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value', 'Week number'], keep='first')
            df_pivot = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                      values='Unique value', aggfunc='count', dropna=False, fill_value=0)

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value'], keep='first')
            df_pivot2 = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                      values='Unique value', aggfunc='count', dropna=False, fill_value=0)

        elif (category_option > 1) & (seasons_option == 0):
            category = categories[category_option]
            season = None
            df_filtered = df[df['Top category'] == categories[category_option]]

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value', 'Week number'], keep='first')
            df_pivot = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                      values='Unique value', aggfunc='count', dropna=False, fill_value=0)

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value'], keep='first')
            df_pivot2 = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                      values='Unique value', aggfunc='count', dropna=False, fill_value=0)

        elif category_option == 1 & (seasons_option != 0):
            category = None
            season = seasons[seasons_option]
            df_filtered = df[df['Season 2'] == season]

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value', 'Week number'], keep='first')
            df_pivot = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                      values='Unique value', aggfunc='count', dropna=False, fill_value=0)

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value'], keep='first')
            df_pivot2 = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                       values='Unique value', aggfunc='count', dropna=False, fill_value=0)

        elif category_option == 1:
            season = category = None

            df_filtered = df.drop_duplicates(subset=['Unique value', 'Week number'], keep='first')
            df_pivot = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                      values='Unique value', aggfunc='count', dropna=False, fill_value=0)

            df_filtered = df_filtered.drop_duplicates(subset=['Unique value'], keep='first')
            df_pivot2 = pd.pivot_table(df_filtered, index=['Week number'], columns=['Domain'],
                                       values='Unique value', aggfunc='count', dropna=False, fill_value=0)
        if category_option != 0:
            print('\n' * 10)
            print(f'{category} {season}')
            print('Number of models in each week')
            print(df_pivot)
            input('Done')

            print('\n' * 10)
            print(f'{category} {season}')
            print('New models per each week')
            print(df_pivot2)
            input('Done')


def slow_analyse(df):
    print('Analyzing...')
    df = df.drop_duplicates(subset=['Unique value', 'Week number'])
    df = df.reset_index(drop=True)
    grouped_df = df.groupby(['Unique value'])['Product name'].count()
    grouped_df = grouped_df.to_frame().reset_index()
    grouped_df['Max discount'] = 0
    grouped_df['URL'] = None


    for i, row in grouped_df.iterrows():
        grouped_df.at[i, 'Max discount'] = float(df[df['Unique value'] == row['Unique value']]['Discount'].max())
        url_position = int(df[df['Unique value'] == row['Unique value']]['Discount'].idxmax())
        grouped_df.at[i, 'URL'] = df.loc[url_position, 'Product URL']

    grouped_df.rename(columns={'Product name': 'Count'}, inplace=True)
    grouped_df = grouped_df.sort_values(by=['Count', 'Max discount', 'Unique value'], ascending=[False, False, True])
    grouped_df.reset_index(drop=True, inplace=True)
    #print(grouped_df[['Product URL', 'Count', 'Max discount']].head(20))
    pd.set_option('display.max_columns', None)
    pd.set_option('max_colwidth', None)
    #print(grouped_df.head(20))
    print(grouped_df.head(100).to_string())

    input('Done')


def average_in_week(df):
    category_option = 9999
    pd_filtered = None
    pd_filtered_2 = None

    categories = df['Top category'].tolist()
    categories = list(dict.fromkeys(categories))
    categories.sort()
    categories.insert(0, 'All')
    categories.insert(0, 'Exit')
    df = df[df['Discount'] > 0]
    df.reset_index(drop=True, inplace=True)

    while category_option != 0:
        print('\n' * 10)
        for i in range(len(categories)):
            print(f'{i}: {categories[i]};', end='')
            if i % 5 == 0:
                print('')

            if i == 0:
                print('\t', end='')
            elif len(categories[i]) >= 8:
                print('\t', end='')
            else:
                print('\t\t', end='')

        category_option = int(input('\nJaka kategoria: '))

        if (category_option != 0) & (category_option != 1):
            filtered_df = df[df['Top category'] == categories[category_option]]
            print('')
            print(f'Average discount value for {categories[category_option]}')
            pd_filtered = pd.pivot_table(filtered_df, index=['Season 2'], columns=['Week number'],
                                         values=['Discount'], aggfunc=[np.mean], dropna=True)
            print(pd_filtered)
            wait = input('Next')
            print('')
            print(f'Amount of discounted items for {categories[category_option]}')
            pd_filtered_2 = pd.pivot_table(filtered_df, index=['Season 2'], columns=['Week number'],
                                           values=['Product URL'], aggfunc=['count'], dropna=True)
            print(pd_filtered_2)
            wait = input('Done')
        elif category_option == 1:
            print('')
            print(f'Average discount value for all categories')
            pd_filtered = pd.pivot_table(df, index=['Season 2'], columns=['Week number'],
                                         values=['Discount'], aggfunc=[np.mean], dropna=True)
            print(pd_filtered)
            wait = input('Next')
            print('')
            print(f'Amount of discounted items for all categories')
            pd_filtered_2 = pd.pivot_table(df, index=['Season 2'], columns=['Week number'],
                                           values=['Product URL'], aggfunc=['count'], dropna=True)
            print(pd_filtered_2)
            wait = input('Done')
        pd_filtered.to_excel('Value of discounted items.xlsx')
        pd_filtered_2.to_excel('Count of discounted items.xlsx')


def average_price(df):
    filtered_df = df.drop_duplicates(subset=['Product URL', 'Top category'])

    filtered_df.to_excel('Filtered DF.xlsx')


def category_spread(df):
    df_new = df.drop_duplicates(subset=['Unique value', 'Top category'], keep='first')

    group_table = df_new.groupby('Top category')['Unique value'].count()
    group_table.plot(kind='pie')
    plt.show()
    input('Done')


def category_save(df):
    df_category = df[df['Top category'] == 'Kurtki_M']
    df_category.to_excel('Combined file.xlsx')


def repair_composition_sizes():
    files = [file for file in os.listdir('./Files')]
    files_count = 0
    files_max = len(files)

    for file in files:
        files_count = files_count + 1
        print(f'{files_count}/{files_max}')
        df = pd.read_excel('./Files/' + file)

        for i, row in df.iterrows():
            composition = []
            sizes = []
            if row['Composition'] == row['Sizes']:
                temp_element = row['Composition'].replace("'", "")
                temp_element = temp_element.replace("[", "")
                temp_element = temp_element.replace("]", "")
                temp_element = temp_element.split(",")
                for element in temp_element:
                    if (element.find('true') >= 0) or (element.find('false') >= 0):
                        sizes.append(element)
                    else:
                        composition.append(element)
                df.at[i, 'Composition'] = composition
                df.at[i, 'Sizes'] = sizes
            else:
                print(f'Not equal: {file} - {i}')
        file_new = file.replace('.xlsx', '')
        file_new = str(file_new) + ' new.xlsx'
        df.to_excel('./Files/' + file_new)


def best_and_slows(df):
    print('Analysing...')

    # Finding first apperance of article
    df_first_prices = df[df['Discount price'].isnull()]
    df_first_prices = df_first_prices.sort_values(by=['Week number'])
    df_first_prices = df_first_prices.drop_duplicates(subset=['Unique value'], keep='first')
    week_numbers = df_first_prices['Week number'].tolist()
    week_numbers = list(set(week_numbers))
    week_numbers.sort()
    df_first_prices = df_first_prices[df_first_prices['Week number'] != week_numbers[0]]

    # Finding first discount and each discount deepening
    df_discounts = df[df['Discount price'].notnull()]
    df_discounts = df_discounts.sort_values(by=['Week number'])
    df_discounts = df_discounts.drop_duplicates(subset=['Unique value', 'Discount price'], keep='first')
    df_discounts = df_discounts[df_discounts['Week number'] != week_numbers[0]]
    df_combined = df_first_prices
    df_combined = df_combined.reset_index(drop=True)
    df_discounts = df_discounts.reset_index(drop=True)

    unique_values_list = df_first_prices['Unique value'].tolist()

    # Setting week number (how many weeks, counting from year 2000)
    for unique_value in unique_values_list:
        df_check = df_discounts[df_discounts['Unique value'] == unique_value]
        if not df_check.empty:
            dataframes = [df_combined, df_check]
            df_combined = pd.concat(dataframes)

    df_combined['Numeric week'] = ""
    del df_combined['id']
    df_combined = df_combined.sort_values(by=['Unique value', 'Week number'])
    df_combined = df_combined.reset_index(drop=True)

    for i, row in df_combined.iterrows():
        if pd.notna(row['Week number']):
            week = (int(row['Week number'][-5:-3])*52)+int(row['Week number'][-2:])
            df_combined.at[i, 'Numeric week'] = week

    # Setting value how many weeks it took after first apperance for each discount
    unique_values_list = df_combined['Unique value'].tolist()
    unique_values_list = list(set(unique_values_list))
    df_final = pd.DataFrame()
    df_combined['Weeks difference'] = "Not discounted"
    for unique_value in unique_values_list:
        df_check = df_combined[df_combined['Unique value'] == unique_value]
        if len(df_check) > 1:
            df_check = df_check.reset_index(drop=True)
            df_check.at[0, 'Weeks difference'] = 0
            for i in range(1, len(df_check)):
                week_difference = int(df_check.at[i, 'Numeric week']) - int(df_check.at[0, 'Numeric week'])
                df_check.at[i, 'Weeks difference'] = week_difference
        dataframes = [df_final, df_check]
        df_final = pd.concat(dataframes)

    df_final = df_final.sort_values(by=['Unique value', 'Week number'])
    df_final = df_final.reset_index(drop=True)

    # Setting value how long an article was in a sale
    df = df.sort_values(by=['Week number'], ascending=False)
    df = df.reset_index(drop=True)
    unique_values_list = df_final['Unique value'].tolist()
    df_final['Weeks on sale'] = ""

    for unique_value in unique_values_list:
        df_check = df_final[df_final['Unique value'] == unique_value]
        df_check_reindexed = df_check.reset_index(drop=True)
        df_all_appearances = df[df['Unique value'] == unique_value]
        df_all_appearances = df_all_appearances.reset_index(drop=True)
        last_available = (int(df_all_appearances.at[0, 'Week number'][-5:-3]) * 52) + \
                       int(df_all_appearances.at[0, 'Week number'][-2:])
        weeks_on_sale = int(last_available) - int(df_check_reindexed.at[0, 'Numeric week'])
        indexes_list = df_check.index.tolist()

        for i in indexes_list:
            df_final.at[i, 'Weeks on sale'] = weeks_on_sale

    # Check if article is still available (based on last file)
    df_final['Is available?'] = "Not available"
    week_numbers.sort(reverse=True)
    df_last_week = df[df['Week number'] == week_numbers[0]]
    for i, row in df_final.iterrows():
        df_check = df_last_week[df_last_week['Unique value'] == row['Unique value']]
        if not df_check.empty:
            df_final.at[i, 'Is available?'] = 'Available'

    # Setting 100% sizes availability
    sizes_count = []
    max_sizes_dic = {}
    '''for i, row in df.iterrows():
         sizes_count.append(row['Sizes'].count(' available'))  
    df['Available sizes count'] = sizes_count'''

    df['Available sizes count'] = ""
    for i, row in df.iterrows():
        df.at[i, 'Available sizes count'] = row['Sizes'].count(' available')

    unique_values_list = df['Unique value'].tolist()
    unique_values_list = list(set(unique_values_list))
    for unique_value in unique_values_list:
        sizes_count = []
        df_check = df[df['Unique value'] == unique_value]
        sizes_count = df_check['Available sizes count'].tolist()
        sizes_count.sort(reverse=True)
        max_sizes_dic.update({unique_value: sizes_count[0]})

    # Setting % of available sizes for each row
    df_final['Sizes %'] = ""
    for i, row in df_final.iterrows():
        if max_sizes_dic.get(row['Unique value']) != 0:
            df_final.at[i, 'Sizes %'] = row['Sizes'].count(' available') / max_sizes_dic.get(row['Unique value'])
            # sizes_count.append(row['Sizes'].count(' available'))
        else:
            df_final.at[i, 'Sizes %'] = 0

    # Save file :)
    df_final.to_excel('Best and slows analyse.xlsx')


def percent_of_discounted_items(df):
    category_option = 'Kurtki_M'
    season_option = 'AW 2021'
    week_numbers = df['Week number'].tolist()
    week_numbers = list(set(week_numbers))
    week_numbers.sort()
    domains = df['Domain'].tolist()
    domains = list(set(domains))
    domains.sort()
    data = {'Week number': week_numbers}
    df_final = pd.DataFrame(data)
    df_final_count = pd.DataFrame(data)

    for domain in domains:
        discount_percentage = []
        articles_count = []
        df_check = df[df['Domain'] == domain]
        df_check = df_check[df_check['Season'] == season_option]
        df_check = df_check[df_check['Top category'] == category_option]
        for week in week_numbers:
            df_week = df_check[df_check['Week number'] == week]
            if not df_week.empty:
                df_discounted = df_week[df_week['Discount price'].notnull()]
                percentage = len(df_discounted)/len(df_week)
                percentage = "{:.0%}".format(percentage)
                discount_percentage.append(percentage)
                articles_count.append(len(df_week))
            else:
                percentage = 0
                percentage = "{:.0%}".format(percentage)
                discount_percentage.append(percentage)
                articles_count.append(len(df_week))
        df_final[domain] = discount_percentage
        df_final_count[domain] = articles_count

    print(f'{category_option} in {season_option}:')
    print(df_final)
    print(f'{category_option} in {season_option}:')
    print(df_final_count)




