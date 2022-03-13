import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd

# url to Scrape Website
url = "https://www.oyorooms.com/search?location=Chennai%2C%20Tamil%20Nadu%2C%20India&city=Chennai&searchType=city&checkin=12%2F03%2F2022&checkout=13%2F03%2F2022&roomConfig%5B%5D=2&guests=2&rooms=1&filters%5Bcity_id%5D=12"

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"} 

# Getting Requests from the webpage
webpage = req.get(url,headers=header)

# Creating BeautifulSoup Object
soup = bs(webpage.content,'html.parser')

# finding the class which has Hotels Listings
hotel_listings = soup.find_all(class_="oyo-row oyo-row--no-spacing listingHotelDescription")

# Creating Separate list for collect the data
names = list()
addres = list()
rating = list()
prices = list()
lst = list()
item = list()
city = list()
country = list()
image = list()

# Loop for getting the data from the website
for hotel in hotel_listings:
    name = hotel.find(class_="listingHotelDescription__hotelName d-textEllipsis")
    address = hotel.find(class_="u-line--clamp-2")
    ratings = hotel.find(class_="is-fontBold hotelRating__rating hotelRating__rating--excellent hotelRating__rating--clickable")
    price = hotel.find(class_="listingPrice__finalPrice")

    # appending the data into the list
    names.append(name.text if name else 'N/A')
    addres.append(address.text if address else 'N/A')
    rating.append(ratings.text if ratings else 'N/A')
    prices.append(price.text if price else 'N/A')
    # for loop for meta data which is not shown for everyone.
    for index,meta in enumerate(hotel.find_all('meta')):
        # Telephone
        if index == 0:
            item.append(meta['content'] if meta['content'] else 'N/A')
        # Link
        elif index == 3:
            lst.append(meta['content'] if meta['content'] else 'N/A')
        # City
        elif index == 5:
            image.append(meta['content'] if meta['content'] else 'N/A')
        # Country
        elif  index == 8:
            city.append(meta['content'] if meta['content'] else 'N/A')
        # Image
        elif  index == 9:
            country.append(meta['content'] if meta['content'] else 'N/A')


    

# Creating the dataframes
hotel_df = pd.DataFrame({"Hotel Name":names,"Address":addres,"Ratings":rating,"Price":prices})
meta_df = pd.DataFrame({"Phone Number":item,"Link":lst,"City":city,"Country":country,"Image":image})

# Merging two dataframes together
df = pd.merge(hotel_df,meta_df,left_index=True,right_index=True)

# Exporting as Excel File
df.to_excel('Oyo_dataset.xlsx',index=False)
