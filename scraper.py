import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import logging
import time
import dateparser

# https://realpython.com/python-logging/
logging.basicConfig(level = logging.DEBUG, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

# Building helpers

# Scrape a site with a url robustly - with good logging, and good error capturing
# This is important because the script will be running automatically from a crontab without user input/maintenance

def scraper(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.Timeout as e:
        logging.warning(e)
        for retry in range(10):
            try:
                time.sleep(60)
                res = requests.get(url)
            except requests.exceptions.Timeout:
                logging.warning('Connection timed out')
                continue
            except requests.exceptions.RequestException as e:
                logging.error(e)
                raise
            else:
                break
    except requests.exceptions.TooManyRedirects as e:
        logging.error(e)
        raise
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        raise
    except requests.exceptions.RequestException as e:
        raise
    else:
        soup = BeautifulSoup(res.content, 'html.parser')
        return soup


# Scraping

# Information Systems Journal (ISJ)
# https://onlinelibrary.wiley.com/journal/13652575
# https://onlinelibrary.wiley.com/page/journal/13652575/homepage/special_issues.htm

def get_cfp_isj():
    l = []

    # Ingest HTML snapshot from https://onlinelibrary.wiley.com/page/journal/13652575/homepage/special_issues.htm

    html = open('Information Systems Journal.html', 'r')
    soup = BeautifulSoup(html, 'html.parser')

    # Assume there can be 1 to arbitrary n rows in the table that holds our CFPs
    # Assume the table will always have 2 columns, one for the paper, one for the due date

    cfp_rows = soup.find('strong', string = 'Call for Papers').find_next('table').find_all('tr')

    if cfp_rows:
        for row in cfp_rows:
            d = {}
            d['Journal'] = 'Information Systems Journal'
            d['URL'] = row.td.a['href']
            d['Title'] = row.td.text
            d['Due Date'] = dateparser.parse(row.find_all('td')[1].text)
            l.append(d)
    else:
        logging.debug('ISJ returned no CFPs')
    return l

# Information Systems Research (ISR)
# https://pubsonline.informs.org/journal/isre
# https://pubsonline.informs.org/page/isre/calls-for-papers

def get_cfp_isr():
    l = []
    base_url = 'https://pubsonline.informs.org'
    cfp_announcement_url = base_url +'/page/isre/calls-for-papers'
    
    soup = scraper(cfp_announcement_url)
    
    # Only h1 is "Calls for Papers"
    page_anchor = soup.find('h1')
    
    # Last 2 elements are unrelated - assume these elements are always going to be there
    cfp_list = page_anchor.find_all_next('h2')[:-2]
    
    if cfp_list:
        for cfp in cfp_list:
            d = {}
            d['Journal'] = 'Information Systems Research'
            d['Title'] = cfp.text.strip()
            # Assume researchers don't care about universities or emails
            # Commented line preserves universities and emails
            # d['Authors'] = '; '.join(cfp.find_next('h4', string = 'Special Issue Editors').next_sibling.next_sibling.text.split('\n'))
            d['Authors'] = '; '.join([researcher.split(' (')[0] for researcher in cfp.find_next('h4', string = 'Special Issue Editors').next_sibling.next_sibling.text.split('\n')])
            d['URL'] = base_url + cfp.find_next('a', href = re.compile('^/doi'))['href']
            # Due/Submission date seems to be unstructured (researchers word it however they want) 
            # The assumptions is the words 'Submission' AND 'Due' or 'Deadline' will be there in any order
            # Otherwise N/A
            d['Due Date'] = dateparser.parse(scraper(d['URL']).find('td', string = re.compile('(Submission.*(Due|Deadline))|((Due|Deadline).*Submission)')).next_sibling.text)
            l.append(d)
    else:
        logging.debug('ISR returned no CFPs')
    return l

# Journal of the Association for Information Systems (JAIS)

def get_cfp_jais():
    l = []
    url = 'https://aisel.aisnet.org/jais/'
    
    soup = scraper(url)
    
    cfp_list = [cfp.next_sibling for cfp in soup.find_all(string = re.compile('Special Issue Call for Papers'))]
    
    if cfp_list:
        for cfp in cfp_list:
            d = {}
            d['Journal'] = 'Journal of the Association for Information Systems'
            d['URL'] = cfp['href']
            d['Title'] = cfp.text.strip()
            l.append(d)
    else:
        logging.debug('JAIS returned no CFPs')
    return l

# Journal of Information Technology (JIT)
# https://journals.sagepub.com/home/jina

def get_cfp_jit():
    l = []
    url = 'https://journals.sagepub.com/home/jina'
    soup = scraper(url)

    cfp_table = soup.find('h3', string = 'Call for Papers').find_next('table')
    cfp_list = cfp_table.find_all('a')

    if cfp_list:
        for cfp in cfp_list:
            d = {}
            d['URL'] = cfp['href']
            d['Journal'] = 'Journal of Information Technology'
            d['Title'] = cfp.text.strip(":“” ")
            d['Due Date'] = dateparser.parse(re.match('^ First round submission deadline: (.+).$', cfp.next_sibling)[1])
            l.append(d)
    else:
        logging.debug('JIT returned no CFPs')
    return l

# Journal of Strategic Information Systems (JSIS)
# NOTE: This is actually the Journal of Management Information Systems (JMIS)

def get_cfp_jmis():
    l = []

    url = 'https://jmis-web.org/issues'
    soup = scraper(url)

    cfp_list = [cfp for cfp in soup.find_all('a', class_ = 'alert-link') if cfp.previous_sibling == ' A new call for papers has been posted: ']

    if cfp_list:
        for cfp in cfp_list:
            d = {}
            d['Journal'] = 'Journal of Management Information Systems'
            d['URL'] = 'https://jmis-web.org' + cfp['href']
            d['Title'] = cfp.text
            l.append(d)
    else:
        logging.debug('JMIS returned no CFPs')
    return l

# Management Information Systems Quarterly (MISQ)
# https://misq.org

def get_cfp_misq():
    l = []
    
    url = 'https://misq.org'
    soup = scraper(url)

    cfp_list = soup.find_all('a', string = re.compile('^Call for Papers:'))

    cfp = cfp_list[0]

    if cfp_list:
        for cfp in cfp_list:
            d = {}
            d['Journal'] = 'Management Information Systems Quarterly'
            d['URL'] = url + cfp['href']
            d['Title'] = re.match('^Call for Papers:  (.*)$', cfp.text.strip())[1]
            d['Due Date'] = dateparser.parse(re.match('^The submission deadline for this special issue is (.*)$', cfp.parent.next_sibling.next_sibling.text)[1])
            l.append(d)
    else:
        logging.debug('MISQ returned no CFPs')
    return l

if __name__ == "__main__":

    # This will be a list of dictionaries to build our dataframe.
    # This is more efficient than continuously 'appending' to our dataframe
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.append.html
    data = []

    data.extend(get_cfp_isj())
    data.extend(get_cfp_isr())
    data.extend(get_cfp_jais())
    data.extend(get_cfp_jit())
    data.extend(get_cfp_jmis())
    data.extend(get_cfp_misq())

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