import scraper
import pandas as pd

if __name__ == "__main__":

    # This will be a list of dictionaries to build our dataframe.
    # This is more efficient than continuously 'appending' to our dataframe
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.append.html
    data = []

    data.extend(scraper.get_cfp_isj())
    data.extend(scraper.get_cfp_isr())
    data.extend(scraper.get_cfp_jais())
    data.extend(scraper.get_cfp_jit())
    data.extend(scraper.get_cfp_jmis())
    data.extend(scraper.get_cfp_misq())

    # Build our CSV

    df = pd.DataFrame(data)

    # Convert Datetime to human readable date
    # If N/A, convert to "Not Known"
    # https://stackoverflow.com/questions/36107094/pandas-apply-to-all-values-except-missing
    # https://www.programiz.com/python-programming/datetime/strftime
    df['Due Date'] = df['Due Date'].apply(lambda x: str(x.strftime('%d/%m/%Y')) if pd.notnull(x) else 'Not Known')

    # Rename columns according to spec (assignment brief)
    rename_dict = {'Journal': 'Journal Name',
                'URL': 'Link to CFP details page',
                'Title': 'CFP title',
                'Authors': 'CFP authors',
                'Due Date': 'Due date',}
    df = df.rename(columns = rename_dict)

    # Order output according to spec (assignment brief)
    # No index, no NaN --> N/A
    output_order = ['Journal Name', 'CFP title', 'CFP authors', 'Due date', 'Link to CFP details page']
    df.to_csv('out.csv', index = False, na_rep = 'N/A', columns = output_order)