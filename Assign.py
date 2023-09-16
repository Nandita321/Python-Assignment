from selenium import webdriver
import schedule
import time
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--ignore-certificate-errors')

uri ="mongodb+srv://nanditas435:A%40rti$03@nandita.jsipzjr.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))


# Send a ping to confirm a successful connection
ping=client.admin.command('ping')
print(ping)
if not(ping.get("ok")):
   print("error connecting db try again.")
   exit(1) # exit process
print("Pinged your deployment. You successfully connected to MongoDB!")
db = client["property-web-scrapper"]
property =db.get_collection("property")


def pageBottom(driver):
    bottom=True
    a=0
    while bottom:
        time.sleep(1)
    # To get actual page height
        Total_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {a});")
        if a > Total_height:
            bottom=False
        a+=5000 # incremental value can be adjusted


citiesCode={12:"Mumbai",38:"Hyderabad",205:"Lucknow",45:"Ahmedabad",25:"Kolkata",177:"Jaipur",32:"Chennai",20:"Bangalore"}

# Iterating over values

def scrapdata(property,driver,cityCode,cityName):
    driver.get(f"https://www.99acres.com/search/property/buy/{cityName.lower()}-all?city={cityCode}&preference=S&area_unit=1&res_com=R")
    driver.implicitly_wait(30)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    pageBottom(driver)

    html=driver.page_source
    driver.close()

#To analyze the html page
    soup=BeautifulSoup(html,'html.parser')

#Creating a list to stored the data
    mylist=[]
    for div in soup.find_all(class_="projectTuple__cardWrap"):
     for tag in div:
        info = tag.find('a',class_="projectTuple__projectName projectTuple__pdWrap20 ellipsis",href=True)
        name =tag.find(class_="projectTuple__subHeadingWrap body_med ellipsis")
        price=tag.find(class_="list_header_bold configurationCards__srpPriceHeading configurationCards__configurationCardsHeading")
      
#To obtain the data in form of dictionary
        Mydic={
    "PropertyInfo": name.text,
    "Propertyprice": price.text,
    "Propertyname": info.text,
    "PropertyCity":cityName,
    "Propertylink": info.attrs.get("href")
         }
        mylist.append(Mydic)
   
    print(mylist)
    property.insert_many(mylist)
    

def job():
    """Setting up a scheduled cron job
"""
    for code in citiesCode.keys():
      driver = webdriver.Chrome(options=options)
      scrapdata(property,driver,code,citiesCode.get(code))
      #driver = webdriver.Chrome(options=options)

#Scheduling the job to run twice daily
#schedule.every(1).minutes.do(job) #for testing purpose
schedule.every().day.at("12:00").do(job)
schedule.every().day.at("23:59").do(job)

# to execute for the first time running process
job()
   
# infinite while loop to keep the code running intead of exiting.
while True:
    schedule.run_pending() #check for pending jobs every seconds
    time.sleep(1)
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(current_time,end='\r')
