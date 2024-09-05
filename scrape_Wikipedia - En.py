# #                                                        Code Surge !
# #                                                        Code Surge !
# #                                                        Code Surge !
# #                                                        Code Surge !
#                                                   https://github.com/MiladMirj
#                                           https://www.linkedin.com/in/milad-mirjalili-15147421a/
#                                               https://www.youtube.com/watch?v=1txJ2GyvwRk
#
#
"""
Enjoy Scraping !
This script allows the user to scrape Articles from Wikipedia  (English) !

To run this script, you need to install the following Python libraries:
1. `requests` - For making HTTP requests.
2. `beautifulsoup4` - For parsing HTML content.

"""


import requests
from bs4 import BeautifulSoup
import random
import json
from pathlib import Path
import os
import time
import traceback


def connect_url(url, time_out, retries, wait_between_call):
    """
    Attempts to connect to a URL with a specified number of retries and timeout.
    
    Args:
        url (str): The URL to connect to.
        timeout (int): The maximum number of seconds to wait for a response. Default is 10 seconds.
        retries (int): The number of times to retry the request in case of failure. Default is 3 retries.
        wait_between_calls (int): The number of seconds to wait between retries. Default is 5 seconds.

    Returns:
        requests.Response or None: The response object if the connection is successful; None if all retries fail.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=time_out)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f'\nError connecting... retrying in {wait_between_call} seconds... {str(e)}')
            time.sleep(wait_between_call)
    return None

def scrape_Wiki_article(url, _c_counter, _filter_links, _processed_links ,_loaded_datas,
                     number_links_to_extract=1, first_run=False ):

    """
    Scrapes a Wikipedia article, processes its content, and recursively extracts links.

    Args:
        url (str): The URL of the Wikipedia article to scrape.
        _c_counter (int): The current count of articles processed.
        _filter_links (list): A list to keep track of links to be processed.
        _processed_links (list): A list of URLs that have already been processed.
        _loaded_datas (list): A list to store the extracted article data.
        number_links_to_extract (int): The number of articles to extract. Default is 1.
        first_run (bool): A flag indicating if this is the first run of the function. Default is False.

    Returns:
        tuple: A tuple containing the list of loaded data and the list of filtered links.
    """
    response = connect_url(url, time_out=10, retries=5, wait_between_call=5)
    if response is None:
        print( "Error connecting to the URL ! ")
        return _loaded_datas, _filter_links
    soup = BeautifulSoup(response.content, 'html.parser')
    text_content = soup.find(id="bodyContent")

    ids_to_process = ['references', 'See_also', 'External_links', 'Bibliography']
    for section_id in ids_to_process:
        h2_tag = text_content.find('h2', id=section_id)
        if h2_tag:
            next_list = h2_tag.find_next('ul')
            if next_list:
                next_list.decompose()
    
    selectors_to_remove = ['iframe', 'script', 'table', 'figure', 'span.mw-editsection-bracket',
                           'span.mw-editsection', 'div.reflist', 'div.catlinks', 'div.refbegin',
                           'div.vector-body-before-content', 'div#contentSub', 'div.printfooter',
                           'sup.reference', 'h3#Bibliography', 'span.lang-comment', 'a.external text',
                           'style', 'h2#References', 'h2#See_also', 'h2#External_links', 'div.quotebox']

    for selector in selectors_to_remove:
        [s.extract() for s in text_content.select(selector)]

    title = soup.find(id="firstHeading")                                   
    if title and text_content:
        temp_dict ={
            "id_url" : url, 
            "info": {"title": title.text.strip(),
             "body_text": text_content.get_text(strip=True)}
        }
        
        if not first_run:
            _c_counter +=1 
            _loaded_datas.append(temp_dict)
            progress =str(round(_c_counter / number_links_to_extract * 100, 2))
            print(progress + " % ", end=' ', flush=True)
        _processed_links.append(url)
        allLinks = text_content.find_all("a", href=True)
        for link in allLinks:
            href = link['href']    
            if "/wiki/" in href and "wikipedia" not in href and "https://" not in href and \
                "https://en.wikipedia.org/" + href not in _filter_links and \
                not href.lower().endswith((".jpg", ".png")):                                
                _filter_links.append("https://en.wikipedia.org" + href)                               
    if _c_counter >= number_links_to_extract:
        return _loaded_datas, _filter_links

    link_to_process = random.choice(_filter_links)
    try:
        while link_to_process in _processed_links:
            if len(_processed_links) >= len(_filter_links):
                return _loaded_datas, _filter_links
            else:
                link_to_process = random.choice(_filter_links)
        if (_c_counter) % 15 == 0 and not first_run:
            print(f"\nTaking a break... (20 seconds) {_c_counter} articles added to the database.")
            time.sleep(20)

        return scrape_Wiki_article(link_to_process, _c_counter, _filter_links, _processed_links,_loaded_datas, 
                            first_run=False, number_links_to_extract=number_links_to_extract)
    except KeyboardInterrupt:
         return _loaded_datas, _filter_links
         print("Canceled ! ")

def generate_data(_processed_links, _loaded_datas, _extracted_links, number_links_to_extract=1,
            save_location='', save_extracted_location=''):
    c_counter = 0
    try:
        if len(_extracted_links) > 0:
            _url = random.choice(_extracted_links)
            _first_run=False
        else:
            _url = "https://en.wikipedia.org/wiki/Main_Page"
            _first_run=True
        print(" Progress : ")

        ret_loaded_datas, ret_extracted_links = scrape_Wiki_article(_url, c_counter, _extracted_links, 
                                                                    _processed_links, _loaded_datas, first_run=_first_run,
                                                                    number_links_to_extract=number_links_to_extract)

        print(f"\nSaving data: {len(ret_loaded_datas)} articles saved to the database!")
        print(f"Saving data: {len(ret_extracted_links)} links ready for extraction!")
        save_data(ret_loaded_datas, ret_extracted_links, save_location, save_extracted_location)           
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())


def save_data(dict_to_save, extracted_links, save_data_location, extracted_links_location):
    with open(save_data_location, "w", encoding="utf-8") as file:
        json.dump(dict_to_save, file, indent=4)

    with open(extracted_links_location, "w", encoding="utf-8") as file:
        for extraced_link in extracted_links:   
            file.write(extraced_link +'\n')

def load_data(data_location, extracted_links_location):
    json_file = Path(data_location)
    extracted_links_file = Path(extracted_links_location)
    loaded_datas = []
    extracted_links = []
    processed_links = []
    if json_file.is_file():
        with open(data_location, "r", encoding="utf-8") as file:
            loaded_datas = json.load(file)	
    if len(loaded_datas) != 0:
        for load_data in loaded_datas:
            processed_links.append(load_data["id_url"]) 
    if extracted_links_file.is_file():
        with open(extracted_links_location, "r", encoding="utf-8") as file:
            for extracted_link in file.readlines():
                extracted_links.append(extracted_link.strip()) 
    return loaded_datas, processed_links, extracted_links



if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    articles_folder = os.path.join(dir_path, "Articles")
    Path(articles_folder).mkdir(parents=True, exist_ok=True)
    articles_location = os.path.join(articles_folder, 'Articles.json')
    extracted_links_location = os.path.join(articles_folder, 'extracted_links.txt')

    loaded_datas, processed_links, extracted_links = load_data(articles_location, extracted_links_location)

    print("<< WELCOME! >>")
    print(f"{len(loaded_datas)} articles stored in the database!")
    print(f"{len(extracted_links)} links ready for extraction!")
    number_links_to_save = input(" How many articles to save? ").strip()
    if number_links_to_save.isdigit() and number_links_to_save!= '0':
                try:
                    generate_data(processed_links, loaded_datas, extracted_links, number_links_to_extract=int(number_links_to_save), save_location=articles_location,
                        save_extracted_location=extracted_links_location)
                except Exception as e:
                    print("Error " + str(e))
    else:
            number_links_to_save = "invalid"
            print(" Enter a number ! ")
            while not number_links_to_save.isdigit() or number_links_to_save== '0':
                number_links_to_save = input("How many Articles to save? ").strip()  
            try:
                generate_data(processed_links, loaded_datas, extracted_links, number_links_to_extract=int(number_links_to_save), save_location=articles_location,
                    save_extracted_location=extracted_links_location)
            except Exception as e:
                print("Error " + str(e)) 
                 
# ////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////
# ////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////# ////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////# ////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////# ////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# ///////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////


