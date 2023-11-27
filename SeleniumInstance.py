from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.common.proxy import Proxy, ProxyType

import os, random, time, subprocess, re

class SeleniumInstance:
    def __init__(
        self,
        cache_directory = None,
        options = None,
        base_timeout = 20,
        variance = 8,
        proxy = None
    ):
        self.base_timeout = base_timeout
        self.variance = variance
        self.proxy_address = self.select_proxy(proxy)
        #Init the webdriver with default options (if applicable)
        '''
        Default options are incognito and a user-agent change, more extensive measures need to be taken such as removing the headers that show selenium being used. The goal is to mimic human use as much as possible. 
        
        If there's a way to run a headless browser and not have it show in the headers, that needs to be looked into as well. 
        '''
        #----------
        default_options = [
            '--incognito',
            f'user-agent={self.generate_user_agent()}',
            '--start-maximized',
            '--disable-extensions',
            '--disable-network-throttling'
        ]
        if options:
            for option in default_options:
                if option not in options:
                    options.append(option)
        else:
            options = default_options
            if self.proxy_address != None:
                options.append(self.proxy_address)

        webdriver_options = Options()
        for option in options:
            webdriver_options.add_argument(option)

        self.driver = webdriver.Chrome(options=webdriver_options)
        self.driver.set_page_load_timeout(30)
        #----------
        #Init the cache system to reduce webpage calls when testing
        '''
        This currently isn't much of an extensive caching system. It's literally a folder with a bunch of files once up and running. Later on, will need to set in some type of autoclearing similar to tempfiles after a certain amount of time. 
        
        Also directory structuring would be very useful here in case there is a discrepency with the web version vs downloaded.
        '''
        #----------
        if cache_directory is not None:
            self.cache_directory = cache_directory
            print(f"Saving websites to cache at {os.getcwd()}/{cache_directory}")
            os.makedirs(cache_directory, exist_ok=True)
        else:
            print("No cache directory specified. Webpages are not being saved")
        #----------
    #Cache directory management methods
    #----------
    
    #----------
    #Anti-bot capabilities, meant to be inserted in helper functions
    '''
    These are the raw methods that should be used throughout the rest of the package for the purposes of anti-bot protection. 
    Any amount of heavy abuse will always be banned, not to mention I'm not the smartest kid on the block, so still use with discretion. 
    This is meant to be enough to get in and get out with the information needed.

    Future Needs:
        > Proxy cycling between non-login sessions
        > Human-like scrolling
        > Working hours method to keep automation within "normal awake hours" per se. How could one account be combing through a website from 7am to 2am without a break? Not even someone from the twitter mob can do that for more than a day.
    '''
    #----------
    def timeout_function(self, base_timeout, variance):
        time_variation = random.uniform(variance - (variance * 2), variance)
        total_time = base_timeout + time_variation
        print(f'Timeout: {total_time:.0f}')

        time.sleep(total_time)
        
    def short_wait(self):
        self.timeout_function(3, 2)

    def reading_wait(self):
        self.timeout_function(20, 8)
    
    def generate_user_agent(self):
        sys_info_list = [
            'Windows NT 10.0; Win64; x64',
            'Windows NT 11.0; Win64; x64',
            'Macintosh; Intel Mac OS X 10_15_7',
            'Macintosh; Intel Mac OS X 13_1',
            'X11; Linux x86_64'
        ]
        
        sys_info = random.choice(sys_info_list)
        platform = 'AppleWebKit/537.36'
        platform_details = 'KHTML, like Gecko'
        extensions = f'Chrome/{self.search_chromium_version()} Safari/537.36'

        return f'Mozilla/5.0 ({sys_info}) {platform} ({platform_details}) {extensions}'

    def search_chromium_version(self):
        try:
            # Run the pacman command and capture the output
            result = subprocess.check_output(["pacman", "-Ss", "chromium"]).decode("utf-8")

            # Split the output into lines
            lines = result.split("\n")

            # Find the line with the version information for "extra/chromium"
            for line in lines:
                if line.startswith("extra/chromium "):
                    version_line = line.split("extra/chromium ")[1]
                    # Use regular expression to extract the version number
                    version = re.match(r"(\d+\.\d+)\.\d+\.\d+", version_line).group(1) + ".0.0.0"
                    return version
        except subprocess.CalledProcessError:
            pass

        return None

    def select_proxy(self, string_or_list = None):
        if string_or_list == None:
            return None
        else:
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            
            if isinstance(string_or_list, str):
                string_or_list = string_or_list.strip()
                try:
                    if string_or_list[3] == 's':
                        proxy.ssl_proxy = string_or_list
                    elif string_or_list[3] == ':':
                        proxy.http_proxy = string_or_list
                except:
                    print('No valid proxy url address detected')

                return f'--proxy-server={string_or_list}'
            
            elif isinstance(string_or_list, list):
                picked_url = random.choice(string_or_list).strip()
                try:
                    if picked_url[3] == 's':
                        proxy.ssl_proxy = picked_url
                    elif picked_url[3] == ':':
                        proxy.http_proxy = picked_url
                except:
                    print('No valid proxy url address detected')

                return f'--proxy-server={picked_url}'
    #----------
    #Helper methods
    #----------
    def get_page(self, url):
        base_cache_filename = os.path.join(self.cache_directory, url.replace('/', '_'))
        cache_filename = f'{base_cache_filename}.html'
        if os.path.exists(cache_filename):
            print(f'Using cached file {cache_filename}')
            self.driver.get(f'file://{os.getcwd()}/{cache_filename}')

        else:
            
            self.driver.get(url)
            
            page_content = self.driver.page_source
            with open(cache_filename, 'w', encoding='utf-8') as cache_file:
                cache_file.write(page_content)
                print(f'saving page {cache_filename}')
            self.reading_wait()
            return page_content

    def get_text_elements(self, container_element, tag_name):
        
        h2_array = container_element.find_elements(By.TAG_NAME, tag_name)
        h2_text_array = [h2.text for h2 in h2_array]
        
        return h2_text_array

    def get_href_elements(self, container_element):

        a_array = container_element.find_elements(By.TAG_NAME, 'a')
        a_href_array = [a.get_attribute('href') for a in a_array]
        
        return a_href_array
        
    def go_back(self):
        previous_url = self.driver.execute_script('return location.href;')
        if previous_url and (previous_url.startswith("file://") or previous_url.startswith("/home")):
            print('going back to cached webpage.')
            self.driver.back()
        else:
            print('going back to non-cached webpage.')
            self.timeout_function(self.base_timeout, self.variance)
            self.driver.back()
        


    def close(self):
        self.driver.quit()
        #----------
        #Passthrough to the driver for all other non-specified functions
        '''
        The functionality of this might have some bugs, not really sure, but it's meant to be a passthrough for anything connecting to the driver with an implicit random delay to simulate human interaction without having to directly code it in every time. Optimization will be needed since there's a lot done by the driver that doesn't use get/post requests, but that's for a later date to sort out.

        We all have patterns, just find what it is and put it into code.

        passthrough ideally works as simply as SeleniumInstance_1.{driver-expression}(*args/**kwargs)
        '''
        #----------
    
    def remove_duplicates_keep_first(self, arr):
        unique_items = []
        seen = set()
        for item in arr:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        return unique_items

    def zip_to_dict(self, keys, values):
        if len(keys) != len(values):
            raise ValueError("Input arrays must have the same length")

        result_dict = {}
        for key, value in zip(keys, values):
            result_dict[key] = value
        return result_dict

    def __getattr__(self, attr):
        def implicit_timeout(*args, **kwargs):
            excluded_broswer_methods = ['find_element', 'find_elements']
            print(f'using unknown method {attr}({args}{kwargs})')
            if attr.lower() not in excluded_broswer_methods:
                print(f'Timing out for method {attr}')
                self.timeout_function(self.base_timeout, self.variance)
            
            return getattr(self.driver, attr)(*args, **kwargs)
            
        if hasattr(self.driver, attr):
            return implicit_timeout
        else:
            raise AttributeError(f"'SeleniumDriver' object has no attribute '{attr}'")
        #----------