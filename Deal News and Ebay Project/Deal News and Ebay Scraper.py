from selenium import webdriver  
from selenium.webdriver.chrome.service import Service                  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Levenshtein
import pandas as pd
from selenium.webdriver.chrome.options import Options

# Levenshtein can be played around with .7 and above looked pretty accurate even further down ebays search
# for scrape extra = False if price is not 6 off from product and websites it likely messed up
# simply look through the deal news browser for products without any sort of price (writing in the price section counts as a price) and enter them to be removed
# binary answer check is whether product is profitable (not considering shipping, demand, etc.) regardless of whether code correctly got the lowest price
# feasability is whether you would actually buy it and this includes factors like shipping

class Product():
    
    # constructor with default values
    def __init__(self, name = 'N/A', price = 0, old_price = 0, website = 'N/A', ebay_price = 0, category = 'N/A', difference_price = 0, binary_answer = 0, binary_answer_check = 0, feasability = 0):
        self.name = name
        self.price = price
        self.old_price = old_price
        self.website = website
        self.ebay_price = ebay_price
        self.category = category
        self.difference_price = difference_price
        self.binary_answer = binary_answer
        self.binary_answer_check = binary_answer_check
        self.feasability = feasability
      
    # checks if deal news products are legit
    def dn_product_check(self):
        if(self.price.split()[0].find('$') == -1 or self.price.split()[-1].find('$') == -1 or self.price.split()[0] == self.price.split()[-1]):
            return False
        return True
    
    # fixes deal news price by splitting it into new and old
    def fix_dn_price(self):
        self.old_price = float(self.price.split()[-1].replace('$', '').replace(',', ''))
        self.price = float(self.price.split()[0].replace('$', '').replace(',', ''))
        
    # gets difference in price and the binary answer to whether product is worth pursuing
    def fix_diff_price_and_binary_ans(self):
        if(self.ebay_price != 0):
            self.difference_price = int(self.ebay_price - self.price - self.ebay_price * .13)
        if(self.difference_price >= 45):
            self.binary_answer = 1
     
    # puts attributes in format to be exported to excel        
    def excel_format(self):
        return [self.name, self.price, self.old_price, self.website, self.ebay_price, self.category, self.difference_price, self.binary_answer, self.binary_answer_check, self.feasability]
    
    # creates a print statement for Product object
    def __str__(self):
        return '\n' + self.name + '\n' + str(self.price) + '\n' + str(self.old_price) + '\n' + self.website + '\n' + str(self.ebay_price) + '\n' + self.category + '\n' + str(self.difference_price) + '\n' + str(self.binary_answer)

class Scraper():
    
    # class-wide variables no need for a constructor
    executable_path = Service('C:/Computer Science/chromedriver_win32/chromedriver.exe') # put chromedriver path here
    chrome_options = Options()
    chrome_options.add_argument('--disable-dev-shm-usage') 
    browser = webdriver.Chrome(options = chrome_options, service = executable_path)
    wait = WebDriverWait(browser, 5)
    product_list = []
    ebay_error_list = []
    deal_news_error_list = []
       
    # turns scraped web elements into a usable list 
    def turn_list_to_text(self, list_passed):
        for i in range(0, len(list_passed)):
            list_passed[i] = list_passed[i].text
    
    # does a check on the accuracy of scraped deal news products
    def dn_accuracy_check(self, products, prices, websites):
        
        # prints lengths of scraped products
        print('Products Lengths:', len(products))
        print('Prices Lengths:', len(prices))
        print('Websites Lengths:', len(websites))
        
        # if difference in product and price length isn't 6 then products likely need to be removed 
        if(len(products) - len(prices) != 6):
            print('\nThere appears to be product(s) without a price or a mismatched scraped')
            while(len(products) - len(prices) != 6):
                remove_product = input('Enter a product to remove or N to stop: ')
                if(remove_product.upper() == 'N'):
                    self.browser.close()
                    raise ValueError("Accuracy check didn't pass.")
                
                # product entered not in products causes error
                try:
                    removal_index = products.index(remove_product)
                    del products[removal_index]
                    del websites[removal_index]
                except:
                    print('\nAn incorrect product was entered')
                    
        # requires user input to ensure accuracy of data scraped
        # looks at last product and verifies name and price with user
        smallest_len = min([len(products), len(prices), len(websites)])
        input_string = 'Is this correct?\n' + products[smallest_len-1] + '\n' + prices[smallest_len-1] + '\n' + websites[smallest_len-1] + '\nEnter Y or N: '
        accuracy_input = input(input_string)
        if(accuracy_input.upper() == 'Y'):
            pass
        else:
            raise ValueError("Accuracy check didn't pass.")
        print()
        
    # scrapes the deal news website for deals
    def scrape_deal_news(self, scrape_extra = False):
        
        # list of deal news urls for other specific categories
        urls = ['https://www.dealnews.com/f1682/Staff-Pick/', 'https://www.dealnews.com/c202/Clothing-Accessories/', 'https://www.dealnews.com/c196/Home-Garden/', 'https://www.dealnews.com/c756/Health-Beauty/', 'https://www.dealnews.com/c142/Electronics/', 'https://www.dealnews.com/c39/Computers/', 'https://www.dealnews.com/c211/Sports-Fitness/', 'https://www.dealnews.com/c186/Gaming-Toys/', 'https://www.dealnews.com/c182/Office-School-Supplies/', 'https://www.dealnews.com/c238/Automotive/', 'https://www.dealnews.com/c178/Movies-Music-Books/']
        
        # if scrape extra = True then scroll length defaults to 5000
        scroll_length = 5000
        
        # if scrape extra = False then just scrape the regular page and set scroll length to 0
        if(scrape_extra == False):
            scroll_length = 0
            urls = ['https://www.dealnews.com/']
        
        # loops through urls
        for url in urls:
                
            # error sometimes with tab crashing
            try:
                
                # opens a browser
                self.browser.get(url) 
                
                # scrolls down the page to get some more deals (any larger of a number messes up the price scraping)
                self.browser.execute_script("window.scrollTo(0, " + str(scroll_length) + ")")
            
                # scrapes prices, products, and websites (does a bit of filtering)          
                prices = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'callout.limit-height.limit-height-large-1.limit-height-small-1')))
                self.turn_list_to_text(prices)
                products = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'title.limit-height.limit-height-large-2.limit-height-small-2')))
                self.turn_list_to_text(products)
                websites = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'key-attribute.limit-height.limit-height-large-1.limit-height-small-1')))
                self.turn_list_to_text(websites)
                websites = [x.split()[0] for x in websites]
                
                # accuracy test for regular scrape
                if(scrape_extra == False):
                    self.dn_accuracy_check(products, prices, websites)
                else:
                    # accuracy test for scrape_extra = True because it's much simpler 
                    if(len(products) != len(prices) or len(prices) != len(websites) or len(websites) != len(products)):
                        continue
                    
                # creates Product objects and adds to list if they are legit (uses method in Product class)
                for i in range(0,len(prices)):
                    if(Product(name = products[i], price = prices[i], website = websites[i]).dn_product_check() == True):
                        self.product_list.append(Product(name = products[i], price = prices[i], website = websites[i]))
            
            # prints url along with error
            except Exception as e:
                print(url + '  ERROR\n\n')
                self.deal_news_error_list.append(e)
        
        # fixes the price 
        for Product_obj in self.product_list:
            
            # tries to get price but very few prices don't meet formatting and these are unlikely to scrape on ebay anyways 
            try:
                Product_obj.fix_dn_price()
            except:
                self.product_list.remove(Product_obj)
      
    # scrapes ebay for products from deal news
    def scrape_ebay(self):
        
        # opens initial browser and ensures it loads ebay because sometimes it gets invalid session ids
        works = False
        while(works == False):
            try:
                self.browser.get('https://www.ebay.com/') 
                works = True
            except:
                pass
        
        # starts count and loops through Product object list
        count = 0
        for Product_obj in self.product_list:
            
            # catches errors for cannot determine loading status from target frame detached, buy it now and free shipping options, category of products, lowest price for product and ignores those products
            try:
            
                # increase count and print it
                count += 1
                print(str(count) + '/' + str(len(self.product_list)))
                    
                # enters Product name into search and enters could cause error 
                self.browser.find_element(By.ID, "gh-ac").send_keys(Product_obj.name)
                self.browser.find_element(By.ID, "gh-btn").click()
                
                # checks for the "no exact match found" and if it finds disregard product else keep going
                try:
                    self.browser.find_element(By.CLASS_NAME, 'srp-save-null-search__heading')
                    self.browser.get('https://www.ebay.com/') 
                    self.product_list.remove(Product_obj)
                    continue
                except:
                    pass
                
                # clicks the new option but needs try except for special cases 
                try:
                    self.browser.find_element(By.PARTIAL_LINK_TEXT, "New").click()
                except:
                    pass
                
                # tries to click buy it now and free shipping options else likely not a good product so causes error
                self.browser.find_element(By.PARTIAL_LINK_TEXT, "Buy It Now").click()
                self.browser.find_element(By.LINK_TEXT, "Free Shipping").click()
                    
                # scrapes ebay prices and names 
                ebay_prices = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 's-item__price')))
                self.turn_list_to_text(ebay_prices)
                ebay_names = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 's-item__title')))
                self.turn_list_to_text(ebay_names)
                
                # tries to scrape category of product but if it can't find disregard the product because in later steps it will be removed
                category = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'srp-refine__category__item')))
                self.turn_list_to_text(category)
                Product_obj.category = category[1].split('\n')[0]
                
                # if scraped less than desired search length then make search len the scrape len
                if(len(ebay_prices)<5):
                    search_len = len(ebay_prices)
                else:
                    search_len = 5
            
                # tries to determine lowest price for product and fixes product variables and if error disregard
                # different Levenshtein standard for first item found and if not met set arbitrarily high lowest price
                if(Levenshtein.ratio(Product_obj.name, ebay_names[1]) > .4):
                    lowest_price = float(ebay_prices[1].replace('$', '').split()[0])
                else:
                    lowest_price = 10000
                   
                # for all other checked ebay prices 
                for i in range(2, search_len):
                    if(Levenshtein.ratio(Product_obj.name, ebay_names[i]) > .6 and float(ebay_prices[i].replace('$', '').split()[0]) < lowest_price):
                        lowest_price = float(ebay_prices[i].replace('$', '').split()[0])
                    
                # fixes price and binary answer and if price is still arbitrarily high set it back to 0
                if(lowest_price == 10000):
                    lowest_price = 0
                Product_obj.ebay_price = lowest_price
                Product_obj.fix_diff_price_and_binary_ans()
                
                # resets browser for next product
                self.browser.get('https://www.ebay.com/') 
    
            # print exceptions, remove product, and goes to next loop
            except Exception as e: 
                self.product_list.remove(Product_obj)
                self.ebay_error_list.append(e)
                print('ERROR')
                continue
            
        # closes ebay browser when done 
        self.browser.close()
        
        # export dataframe of errors from scraping 
        error_df = pd.DataFrame(columns = ['Ebay Errors'])
        error_df['Ebay Errors'] = self.ebay_error_list
        error_df = pd.concat([error_df, pd.DataFrame({'Deal News Errors': self.deal_news_error_list})], axis = 1)
        error_df.to_excel('C:/Computer Science/Deal News and Ebay Project/Scraping Error Data.xlsx', index = False) 
     
    # outputs results in a presentable manner
    def show_results(self):
        good_products = []
        for Product_obj in self.product_list:
            if(Product_obj.binary_answer == 1):
                good_products.append(Product_obj)
            else:
                print(Product_obj)
        if(len(good_products) == 0):
            print('\nTHERE WERE NO GOOD PRODUCT(S)')
        else:
            print('\nGOOD PRODUCT(S)')
            for good_product in good_products:
                print(good_product)
            
    # exports to excel         
    def export_to_excel(self, file = ''):
        
        # makes sure user is active when exporting so data isn't added with answers being manually checked
        excel_input = input("Would you like to export to Excel? Y or N: ")
        if(excel_input == 'Y'):
        
            # creates a dataframe out of scraped products
            product_df = pd.DataFrame(columns = ['Name', 'Price', 'Old Price', 'Website', 'Ebay Price', 'Category', 'Difference Price', 'Binary Answer', 'Binary Answer Check', 'Feasability'])
            for Product_obj in self.product_list:
                product_df.loc[len(product_df.index)] = Product_obj.excel_format()
            
            # tries to download current file and check for duplicate products
            try:
                current_product_df = pd.read_excel(file)
                combined_product_df = current_product_df.append(product_df)
                combined_product_df = combined_product_df.drop_duplicates(subset = ['Name', 'Price', 'Binary Answer'])
                print('\n' + str(len(combined_product_df) - len(current_product_df)) + ' New Products Added')
            except:
                print("\nCouldn't Find File")
                combined_product_df = product_df
            
            # drop rows that are empty
            combined_product_df.drop(combined_product_df.index[combined_product_df['Category'] == ''], inplace = True)
            combined_product_df.drop(combined_product_df.index[combined_product_df['Ebay Price'] == 0], inplace = True)
            
            # saves as an excel file 
            combined_product_df.to_excel(file, index = False) 
            print('\nSuccessfully exported to:', file)
    
    # used to change the manual answer columns
    def change_manual_answers(self, file = ''):
        
        # tries to close the browser if open
        try:
            self.browser.close()
        except:
            pass
        
        # reads in the current data
        current_product_df = pd.read_excel(file)
        
        # asks for input for products and then checks binary answer is 1 before potentially changing manual answers 
        product_input = ''
        while(product_input.upper() != 'N'):
            product_input = input('Enter product or N to stop: ')
            row_index_list = current_product_df.index[current_product_df['Name'] == product_input].tolist()
            for row_index in row_index_list:
                if(current_product_df.at[row_index, 'Binary Answer'] == 1):
                    if(input("Would you like to change Binary Answer Check? Enter Y or N: ").upper() == 'Y'): 
                        current_product_df.at[row_index, 'Binary Answer Check'] = 1
                        print('\nChanged Binary Answer Check for', product_input)
                    if(input("Would you like to change Feasability? Enter Y or N: ").upper() == 'Y'): 
                        current_product_df.at[row_index, 'Feasability'] = 1
                        print('\nChanged Feasability for', product_input)
        
        # saves as an excel file
        current_product_df.to_excel(file, index = False) 
        print('\nSuccessfully exported to:', file)
        
# modifies a dataframe that is read in
def modify_dataframe(file = ''):
    
    # reads in dataframe
    df = pd.read_excel(file)
    
    # can modify value at cell
    #df.at[66, 'Binary Answer Check'] = 0
    
    # drop rows that are empty
    df.drop(df.index[df['Category'] == ''], inplace = True)
    df.drop(df.index[df['Ebay Price'] == 0], inplace = True)
    
    # exports to excel
    df.to_excel(file, index = False) 
        
def main():
    
    Scraper_obj = Scraper()
    
    # parameter is scrape extra which can be set to True or False
    Scraper_obj.scrape_deal_news(scrape_extra = True)
    
    # scrapes ebay no parameters needed
    Scraper_obj.scrape_ebay()
    
    # outputs scraped results 
    Scraper_obj.show_results()
    
    # prints how many errors during ebay scraping
    print('\nThere were ' + str(len(Scraper_obj.ebay_error_list)) + ' errors during ebay scraping')
    
    # exports to excel and takes file as a parameter 
    Scraper_obj.export_to_excel(file = 'C:/Computer Science/Deal News and Ebay Project/Deal News and Ebay Scraper Data.xlsx')
    
    # allows to change the manual answer columns and takes file as a parameter
    Scraper_obj.change_manual_answers(file = 'C:/Computer Science/Deal News and Ebay Project/Deal News and Ebay Scraper Data.xlsx')

    # modifies dataframe and takes file as a parameter
    #modify_dataframe(file = 'C:/Computer Science/Deal News and Ebay Project/Deal News and Ebay Scraper Data.xlsx')
         
main()