from selenium.webdriver.common.by import By

import main
import selenium.webdriver, selenium
import time
driver = selenium.webdriver.Chrome()

main_dict = {"base_url": "https://www.texaslottery.com/export/sites/lottery/Games/Scratch_Offs/index.html#",
             "price_points": [1, 2, 3, 5, 10, 20, 30, 50],
             "ticket_info": {}}


def OpenLotteryHomePage(price_point):  # in dollars, find the lottery page to extract info
    mod_url = f"{main_dict['base_url']}{price_point}"
    return driver.get(mod_url)


def get_pg_source(url):
    return driver.page_source


def GET_TICKET_URLS_PRICE_POINT(price_point):  # in dollars
    OpenLotteryHomePage(
        main_dict["price_points"][main_dict["price_points"].index(price_point)])  # Each price point has a different URL which leads to its tickets
    mod_url_src = (get_pg_source(driver.current_url))  # Obtain Page Source for Ticket Catalogue Page
    ticket_numbers_at_pricePoint = (main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(mod_url_src, ".html_",
                                                                               '.html"'))  # Get All Ticket Numbers at this price point
    pricePointTicketUrls = main.INJECT_URL_MODIFIERS_BETWEEN_2_STRINGS(
        url_prefix="https://www.texaslottery.com/export/sites/lottery/Games/Scratch_Offs/details.html_",
        url_suffix=".html", injections=ticket_numbers_at_pricePoint)
    return pricePointTicketUrls


def GET_ALL_TICKET_URLS():  # Should Get About 50 Links To Specific Tickets/Info
    url_array = []
    for price_point in main_dict['price_points']:
        url_array.append(GET_TICKET_URLS_PRICE_POINT(price_point))
    return url_array[0]


def findDBClusters(full_string):
    for match in main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=full_string, p1="<tr>", p2="</tr>"):
        prize_usd = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=match, p1="<td>", p2="</td>")[0]
        totalPrizesForTicketAtAmount = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=match, p1="<td>", p2="</td>")[1]
        claimed_prizes_at_level = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=match, p1="<td>", p2="</td>")[2]
        print(prize_usd, totalPrizesForTicketAtAmount)
        blurb_info = f"There are "


#  print(GET_ALL_TICKET_URLS())
def getTicketDetails(urls: list):
    for url in urls:
        driver.get(url)
        time.sleep(.1)
        page_src = driver.page_source
        findDBClusters(full_string=page_src)
        game_number = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=page_src, p1="Game No. ", p2=" - ")[0]
        print(f"Game Number: {game_number}")
        game_name = driver.find_element(By.XPATH, "//*[@id=\"content\"]/div/div/div[1]/div/div/h2").text.split("- ")[1]
        print(f"Game Name: {game_name}")
        total_prizes_dollars = int(float(driver.find_element(By.XPATH, "//*[@id=\"content\"]/div/div/div[2]/div[2]/div/ul").text.split("$")[1].split(" ")[0])*1000000)
        print(f"Total Prize Money Pool: ${total_prizes_dollars}")
        pack_size = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=page_src, p1="Pack Size: ", p2=" tickets")[0]
        max_tickets = driver.find_element(By.XPATH, "//*[@id=\"content\"]/div/div/div[2]/div[2]/p[2]").text.split("approximately ")[1].split("*")[0].replace(",", "")
        guaranteed_per_pack_usd = page_src.split("Amount = $")[1].split(" per pack")[0]
        guaranteed_per_ticket_usd = int(pack_size)/float(guaranteed_per_pack_usd)
        print(f"Average ticket winnings: ${guaranteed_per_ticket_usd}")
        print(f"Total Possible Tickets: {max_tickets}")
        odds2 = main.SANDWHICHED_SUBSTRING(full_string=page_src, slice_1="1 in ", slice_2="**")
        adjusted_odds = float(odds2)
        print(f"Adjusted Odds: 1 in {adjusted_odds}")
        temp_full_string = main.list_SANDWHICHED_SUBSTRING(full_string=page_src, slice_1="<tbody>", slice_2="</tbody>")
        temp_array = []
        for item in temp_full_string:
            temp_array.append(item)

        highest_prize = temp_array[0]
        print(f"Highest Prize: {highest_prize}")
        prize_data = temp_array
        claimed_ratio_data_points = []  # will average them
        available_ratio_data_points = []
        for i in range(1, len(prize_data)-1, 3):
            if i not in [6]:
                available_tickets = str(prize_data[i]).replace(",", "").replace("$", "")
                available_tickets = int(available_tickets)
                available_ratio_data_points.append(available_tickets)
        for i in range(2, len(prize_data), 3):
            claimed_tickets = str(prize_data[i]).replace(",", "").replace("$", "")
            claimed_tickets = int(claimed_tickets)
            claimed_ratio_data_points.append(claimed_tickets)
        avg_claimed_ratio = float(sum(claimed_ratio_data_points)/sum(available_ratio_data_points))
        avg_availability_chance = 1 - avg_claimed_ratio
        print(f"Current Prize Availability: {round(avg_availability_chance, 4)}%")
        table_cells_prizes = temp_array
        print({"Table Cells": table_cells_prizes})
        # TO DO GAME NUMBER, GAME ODDS, PACK SIZE, TOTAL PRIZES, LARGEST_PRIZE, MEAN_PRIZE, PACK
        print(f"Pack Size: {pack_size} Tickets")


getTicketDetails(GET_ALL_TICKET_URLS())
# TODO ACCESS EACH URL WE FOUND AND GET ODDS AND ADD TO JSON OR DICT WITH NAME OF TICKET AND URL TO TICKET
