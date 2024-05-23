import time
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
from selenium.webdriver.common.keys import Keys
import os

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

def fetch_table_and_rows(driver):
        print("Fetching table and rows")
        table = driver.find_element(By.ID, "ContentPlaceHolder1_gdvFirSearch")
        rows = table.find_elements(By.TAG_NAME, 'tr')
        return table, rows

def download_one_FIR_num(driver, path, download_dir):
    print("Download One FIR called---------------")
    try:
        _, rows = fetch_table_and_rows(driver)
        
        num_rows = len(rows)
        index_row = 0
        default_window = driver.current_window_handle
        print("num_rows: ", num_rows)
        
        while index_row < num_rows:
            print("index_row: ", index_row)
            try:
                _, rows = fetch_table_and_rows(driver)
                columns = rows[index_row].find_elements(By.TAG_NAME, "td")
                print("Year: ", columns[1].text[-4:])
            except (StaleElementReferenceException, IndexError):
                print("Invalid index: Stale element or IndexError")
                index_row = updateIndex(index_row)
                continue

            print("Before columns check")
            if len(columns) > 0 and columns[1].text[-4:] in ["2019", "2021", "2022"]:
                print("Columns check: true")
                old_files = os.listdir(download_dir)
                link = columns[6].find_element(By.TAG_NAME, "a")
                
                windows_before = driver.window_handles
                link.click()

                try:
                    WebDriverWait(driver, 20).until(EC.new_window_is_opened(windows_before))
                    driver.switch_to.window([x for x in driver.window_handles if x not in windows_before][0])
                    file_window_handle = driver.current_window_handle
                except TimeoutException:
                    driver.switch_to.window(default_window)

                try:
                    download_button_outer = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "RptView_ctl06_ctl04_ctl00_ButtonLink")))
                    download_button_outer.click()
                    
                    download_button_inner = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/form/span/div/table/tbody/tr[4]/td/span/div/div/div[4]/table/tbody/tr/td/div[2]/div[1]/a")))
                    download_button_inner.click()
                except TimeoutException:
                    print("Download button not found")
                    driver.close()
                    driver.switch_to.window(default_window)
                    index_row = updateIndex(index_row)
                    continue

                downloading_too_long = 0
                while True:
                    try:
                        new_files = os.listdir(download_dir)
                        downloaded_file = [x for x in new_files if x not in old_files][0]
                        print("File Downloaded")
                        time.sleep(5)
                        break
                    except IndexError:
                        print("File not downloaded yet!")
                        downloading_too_long += 1
                        if downloading_too_long > 10:
                            driver.switch_to.window(default_window)
                            download_one_FIR_num(driver, path, download_dir)
                        time.sleep(4)

                time.sleep(2)
                driver.close()
                driver.switch_to.window(default_window)
            print("Columns check: false")
            index_row = updateIndex(index_row)
        
        driver.switch_to.window(default_window)
    except NoSuchElementException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return 0

def updateIndex(index_row):
    return index_row + 1

def main(dist, stn):
    dist = int(dist)
    stn = int(stn)
    home = os.path.expanduser("~")
    download_dir = os.path.join(home, "Downloads")
    absolute_path = os.path.dirname(__file__)
    wd_path = os.path.join(absolute_path, 'chromedriver.exe')
    s = Service(wd_path)

    driver = webdriver.Chrome(service=s)
    url = 'https://policecitizenportal.uk.gov.in/Citi/firSearch.aspx'

    # try to open the website
    try:
        # Open the website in chrome
        driver.get(url)
        time.sleep(4)
    except:
        try:
            driver.refresh()
            time.sleep(4)
        except:
            print("Website not opening. Try again later.")
            time.sleep(4)

    # loop through the FIR numbers

    district_list = Select(driver.find_element("id", "ContentPlaceHolder1_ddlDitrictFirSearch"))
    time.sleep(3)
    district_names = []
    for district in district_list.options:
        district_names.append(district.accessible_name)
    district = district_names[dist]
    district_list.select_by_index(dist)
    print("District: ", district)
    time.sleep(5)
    station_list = Select(driver.find_element("id", "ContentPlaceHolder1_ddlPoliceStationFirSearch"))
    station_names = []
    for station in station_list.options:
        station_names.append(station.accessible_name)
    print("Station names: ", station_names)

    for station in station_names[stn:]:  # stn should be 1 by default
        path = os.path.join(download_dir, str(dist), str(stn))
        print("Station: ", station)
        time.sleep(5)
        bool_var = expected_conditions.staleness_of(station_list)
        while bool_var:
            # Select the police station
            try:
                station_list = Select(
                    driver.find_element("id", "ContentPlaceHolder1_ddlPoliceStationFirSearch"))
                station_list.select_by_index(stn)
            except selenium.common.exceptions.StaleElementReferenceException:
                print("stale element!")
            else:
                break

            stn = stn + 1
            time.sleep(5)
            bool_var = expected_conditions.staleness_of(station_list)

        time.sleep(5)
        # print(station)

        # loop fir num
        for i in range(1, 1000):
            FIR = driver.find_element("id", "ContentPlaceHolder1_txtFirNoSearch")
            FIR.click()
            print("\nFIR num=")
            print(i)
            FIR.clear()
            FIR.send_keys(str(i))
            time.sleep(1)
            FIR.send_keys(Keys.ENTER)
            print("Searching")
            time.sleep(5)

            try:
                _ = driver.find_element('id', 'ContentPlaceHolder1_gdvFirSearch_lblNoRecordFound')
                print("No more FIRs here!")
                break
            except:
                download_one_FIR_num(driver, path, download_dir)
                print("downloading")

    driver.close()
    driver.quit()


if __name__ == '__main__':
    distNo = input("Enter District No: ")
    psNo = input("Enter PS No: ")
    print("Entered values are: ", distNo, psNo)
    main(distNo, psNo)
