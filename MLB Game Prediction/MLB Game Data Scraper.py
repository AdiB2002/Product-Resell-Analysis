from selenium import webdriver  
from selenium.webdriver.chrome.service import Service                  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.chrome.options import Options

class Scraper():
    
    # class-wide variables that set up browser and create dataframe for scraped games
    executable_path = Service('C:/Computer Science/chromedriver_win32/chromedriver.exe')
    chrome_options = Options()
    chrome_options.add_argument('--disable-dev-shm-usage') 
    browser = webdriver.Chrome(options = chrome_options, service = executable_path)
    wait = WebDriverWait(browser, 5)
    df = pd.DataFrame(columns=['Week', 'Home_Team', 'Away_Team', 'Result'])
    
    # turns scraped web elements into a usable list 
    def turn_list_to_text(self, list_passed):
        for i in range(0, len(list_passed)):
            list_passed[i] = list_passed[i].text
            
    # scrapes past mlb games
    def scrape_past_games(self):
        
        # months that mlb games are played and used to navigate through website
        months = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
        
        # opens up browser to website and starts count
        self.browser.get('http://www.playoffstatus.com/mlb/mlbaprschedule.html')
        count = 0
        
        # loops through months 
        for month in months:
            
            # clicks on month by using link text 
            self.browser.find_element(By.PARTIAL_LINK_TEXT, month).click()
            
            # loops through table of information 
            for i in range(2, 1000):
                
                # gets the week of the game
                # try except is needed if the end of table is hit an error is thrown
                try:
                    week = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sflx"]/div/table[3]/tbody/tr[' + str(i) + ']/td[1]')))
                    self.turn_list_to_text(week)
                    week = week[0]
                except:
                    break
                
                # prints count
                count += 1
                print(str(count) + '/' + str(2430))
                
                # gets the home team 
                home_team = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sflx"]/div/table[3]/tbody/tr[' + str(i) + ']/td[2]')))
                self.turn_list_to_text(home_team)
                home_team = home_team[0].split()[:-1]
                home_team = ' '.join(home_team)
                
                # try except needed because scraping upcoming matches that don't have a score yet and this throws an error
                try:
                    
                    # gets the score
                    score = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sflx"]/div/table[3]/tbody/tr[' + str(i) + ']/td[3]')))
                    self.turn_list_to_text(score)
                    home_score = score[0].split()[0].split('‑')[0]
                    away_score = score[0].split()[0].split('‑')[1]
                    
                    # determines the winner
                    if(home_score > away_score):
                        result = 1
                    elif(away_score > home_score):
                        result = 0
                    else:
                        continue
                
                # for future games make result N/A
                except:
                    result = 'No Result'
                
                # gets the away team
                away_team = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sflx"]/div/table[3]/tbody/tr[' + str(i) + ']/td[4]')))
                self.turn_list_to_text(away_team)
                away_team = away_team[0].split()[:-1]
                away_team = ' '.join(away_team)
                    
                # appends information to dataframe as a row
                self.df.loc[len(self.df)] = [week, home_team, away_team, result]
        
        # returns the dataframe         
        return self.df
            
def main():
    
    # scraper object
    Scraper_obj = Scraper()
    
    # scrapes past games and doesn't take any parameters 
    df = Scraper_obj.scrape_past_games()
    
    # exports df to csv
    df.to_csv('C:/Computer Science/MLB Game Prediction/MLB Game Data.csv', index = False) 
    
    # quits browser after done
    Scraper_obj.browser.quit()
    
main()