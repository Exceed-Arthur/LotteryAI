import datetime
import emailer
from selenium.webdriver.common.by import By

import main
import selenium.webdriver, selenium
import time
driver = selenium.webdriver.Chrome()

main_dict = {"base_url": "https://www.texaslottery.com/export/sites/lottery/Games/Scratch_Offs/index.html#",
             "price_points": [1, 2, 3, 5, 10, 20, 30, 50],
             "ticket_info": {},
             "Ticket Numbers": [],
             "Pack Value Index": {},
             "Prize Availability Index": {},  # Availability: {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             "Total Value Index": {},  # Availability: {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             "Net Gain Index": {},  # Availability: {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             "Odds Index": {}   # Availability: {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             }



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
    global main_dict
    for url in urls:

        driver.get(url)
        time.sleep(.1)
        page_src = driver.page_source
        findDBClusters(full_string=page_src)
        game_number = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=page_src, p1="Game No. ", p2=" - ")[0]

        game_name = driver.find_element(By.XPATH, "//*[@id=\"content\"]/div/div/div[1]/div/div/h2").text.split("- ")[1]

        total_prizes_dollars = int(float(driver.find_element(By.XPATH, "//*[@id=\"content\"]/div/div/div[2]/div[2]/div/ul").text.split("$")[1].split(" ")[0])*1000000)

        pack_size = main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(full_string=page_src, p1="Pack Size: ", p2=" tickets")[0]
        max_tickets = driver.find_element(By.XPATH, "//*[@id=\"content\"]/div/div/div[2]/div[2]/p[2]").text.split("approximately ")[1].split("*")[0].replace(",", "")
        guaranteed_per_pack_usd = page_src.split("Amount = $")[1].split(" per pack")[0]
        guaranteed_per_ticket_usd = float(guaranteed_per_pack_usd) / float(int(pack_size))
        # print(page_src)
        odds2 = main.SANDWHICHED_SUBSTRING(full_string=page_src, slice_1="1 in ", slice_2="**")
        adjusted_odds = float(1.0/float(odds2))
        temp_full_string = main.list_SANDWHICHED_SUBSTRING(full_string=page_src, slice_1="<tbody>", slice_2="</tbody>")
        temp_array = []
        for item in temp_full_string:
            temp_array.append(item)
        highest_prize = temp_array[0]
        lowest_prize = main.getLowestPrize(temp_array)
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
        avg_availability_chance = (1 - avg_claimed_ratio) * 100
        table_cells_prizes = temp_array
        #print({"Table Cells": table_cells_prizes})
        # TO DO GAME NUMBER, GAME ODDS, PACK SIZE, TOTAL PRIZES, LARGEST_PRIZE, MEAN_PRIZE, PACK

        #  print(f"Price Per Ticket: {lowest_prize}")
        base_url = "https://www.texaslottery.com/"
        prefix_url_mod = "/export/sites/lottery/Images/scratchoffs/"
        suffix_url_mid = f"{game_number}_img1.gif"
        url1 = f"{base_url}{prefix_url_mod}{suffix_url_mid}"
        suffix_url_mid = f"{game_number}_img2.gif"
        url2 = f"{base_url}{prefix_url_mod}{suffix_url_mid}"
        image_urls = [url1, url2]
        # image_urls = image_urls.append(main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(page_src, "<img src=", '"')[0])
        print("\n")
        net_gain = float(guaranteed_per_ticket_usd) - float(str(lowest_prize).replace("$", ""))
        main_dict['ticket_info'].update({game_number: {
         "Game Name": game_name,
         "Game Number": game_number,
         "Prize Pool (USD)": float(total_prizes_dollars),
         "Average Winnings Per Ticket": float(guaranteed_per_ticket_usd),
         "Net Gain/Loss Per Ticket": float(guaranteed_per_ticket_usd) - float(str(lowest_prize).replace("$", "")),
         "Tickets In Circulation": float(max_tickets),
         "Adjusted Odds": float(adjusted_odds),
         "Pack Value (USD)": int(guaranteed_per_pack_usd),
         "Highest Prize": float(int(str(highest_prize).replace("$", "").replace(",", ""))),
         "Current Prize Availability": float(avg_availability_chance),
         "Pack Size": (int(pack_size)),
         'Ticket Price USD': float(str(lowest_prize).replace("$", "")),
         "Image Urls": image_urls,
         "Ticket Url": url
          }})
        highest_prize = int(str(highest_prize).replace("$", "").replace(",", ""))
        total_value = highest_prize + int(total_prizes_dollars) + int(guaranteed_per_pack_usd)


        #  print(main_dict['ticket_info'][game_number])
        main_dict['Ticket Numbers'].append(game_number)

        main_dict["Pack Value Index"].update({guaranteed_per_pack_usd: {"Game Number": game_number,
                                                                        "Net Gain": net_gain,
                                                                        "Total Value": total_prizes_dollars,
                                                                        "Prize Availability": avg_availability_chance,
                                                                        "Adjusted Odds": adjusted_odds}})
        main_dict["Prize Availability Index"].update({avg_availability_chance: {"Game Number": game_number,
                                                              "Net Gain": net_gain,
                                                              "Total Value": total_prizes_dollars,
                                                              "Pack Value": int(
                                                                guaranteed_per_pack_usd),
                                                              "Adjusted Odds": adjusted_odds}})
        main_dict["Total Value Index"].update({total_value: {"Game Number": game_number,
                                                              "Net Gain": net_gain,
                                                              "Prize Availability Index": avg_availability_chance,
                                                              "Pack Value": int(
                                                                  guaranteed_per_pack_usd),
                                                              "Adjusted Odds": adjusted_odds}})
        main_dict["Net Gain Index"].update({net_gain: {"Game Number": game_number,
                                                              "Total Value": total_value,
                                                              "Prize Availability Index": avg_availability_chance,
                                                              "Pack Value": int(
                                                                  guaranteed_per_pack_usd),
                                                              "Adjusted Odds": adjusted_odds}})
        main_dict["Odds Index"].update({adjusted_odds: {"Game Number": game_number,
                                                              "Total Value": total_value,
                                                              "Prize Availability Index": avg_availability_chance,
                                                              "Pack Value": int(
                                                                  guaranteed_per_pack_usd),
                                                              "Net Gain Index": net_gain}})
        print(main_dict['ticket_info'][game_number])




getTicketDetails(GET_ALL_TICKET_URLS())
print('\n')
main.save_to_file(file_name=f"Scraped_Texas_Lottery_{datetime.date.today()}.txt", final_string=str(main_dict))
emailer.itoven_send_email_str(to="arthur@itoven-ai.co", subject=f"Lottery AI Report {datetime.date.today()}", message=str(main_dict))
# TODO ACCESS EACH URL WE FOUND AND GET ODDS AND ADD TO JSON OR DICT WITH NAME OF TICKET AND URL TO TICKET

# TODO CREATE 0-100 SYSTEM FOR EACH ATTRIBUTE THEN RANK, based on rank in all tickets for that category (like madden player ratings)

def TicketInfo(game_number):
    return main_dict['ticket_info'][game_number]


for ticket_number in main_dict["Ticket Numbers"]:
    ticket_info = TicketInfo(ticket_number)
