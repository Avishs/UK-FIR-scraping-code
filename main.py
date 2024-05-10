import time
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
import os


def download_one_FIR_num(driver, path, download_dir):
    # Find the table element
    table = driver.find_element("id", "ContentPlaceHolder1_gdvFirSearch")

    # Find all rows in the table
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # Iterate over each row in the table
    for row in rows:
        # Find all columns in the row
        columns = row.find_elements(By.TAG_NAME, "td")
        # Check if the first column value is in the predefined set of values
        if len(columns) > 0 and columns[1].text[-4:] in ["2019", "2021", "2022"]:
            # Listing the old files still in the directory
            old_files = os.listdir(download_dir)
            print("year=", columns[1].text[-4:])
            # If yes, click the link in the second column (assuming it's a link)
            print("Column value")
            print(columns[6])
            link = columns[6].find_element(By.TAG_NAME, "a")
            print(link.text)
            windows_before = driver.window_handles
            link.click()
            time.sleep(4)
            # Go to the new page and download the FIR
            WebDriverWait(driver, 20).until(expected_conditions.new_window_is_opened(windows_before))
            time.sleep(3)
            driver.switch_to.window([x for x in driver.window_handles if x not in windows_before][0])
            time.sleep(5)
            download_button_outer = driver.find_element("id", "RptView_ctl06_ctl04_ctl00_ButtonLink")
            time.sleep(1)
            download_button_outer.click()
            time.sleep(1)
            download_button_inner = driver.find_element(By.XPATH,
                                                        "/html/body/form/span/div/table/tbody/tr[4]/td/span/div/div/div[4]/table/tbody/tr/td/div[2]/div[1]/a")
            download_button_inner.click()
            time.sleep(3)

            while True:
                try:
                    # List the new files in the directory
                    new_files = os.listdir(download_dir)
                    # Check which file is new.
                    downloaded_file = [x for x in new_files if x not in old_files][0]
                except IndexError:
                    print("File not downloaded yet!")
                    time.sleep(4)
                else:
                    break
            # rename and re-store downloaded file
            # The full name is the address, along with the date
            os.rename(os.path.join(download_dir, downloaded_file), os.path.join(path, downloaded_file))
            driver.switch_to.window(windows_before[0])


def main(dist: int, stn: int):
    download_dir = 'C:/Users/asha2/Downloads'
    wd_path = 'C:/Users/asha2/Documents/_Projects/FIRs_2021_2022/UK/downloading/chromedriver.exe'
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
    for i in range(1, 100):
        FIR = driver.find_element("id", "ContentPlaceHolder1_txtFirNoSearch")
        FIR.click()
        FIR.send_keys("1")

        time.sleep(5)

        district_list = Select(driver.find_element("id", "ContentPlaceHolder1_ddlDitrictFirSearch"))

        time.sleep(5)
        district_names = []
        for district in district_list.options:
            district_names.append(district.text)

        for district in district_names[dist]:
            print(district)
            district_list.select_by_visible_text(district)
            time.sleep(3)
            station_list = Select(driver.find_element("id", "ContentPlaceHolder1_ddlPoliceStationFirSearch"))
            station_names = []
            for station in station_list.options:
                station_names.append(station.text)

            for station in station_names[stn:]:

                path = os.path.join(download_dir, district, station)
                print(path)
                time.sleep(5)
                bool_var = expected_conditions.staleness_of(station_list)
                while bool_var:
                    # Select the police station
                    try:
                        station_list = Select(
                            driver.find_element("id", "ContentPlaceHolder1_ddlPoliceStationFirSearch"))
                        station_list.select_by_visible_text(station)
                    except selenium.common.exceptions.StaleElementReferenceException:
                        print("stale element!")
                    else:
                        break
                    time.sleep(5)
                    bool_var = expected_conditions.staleness_of(station_list)

                time.sleep(3)
                station_list.select_by_visible_text(station)
                time.sleep(3)
                print(station)

                # click submit button

                search_button = driver.find_element("id", "ContentPlaceHolder1_btnSearchFir")
                print("found the search button")
                search_button.click()
                print("clicked the search button")
                time.sleep(5)

                download_one_FIR_num(driver, path, download_dir)

    driver.close()
    driver.quit()


if __name__ == '__main__':
    main(4, 1)
