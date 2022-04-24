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
             "Total Value Index": {},  # Total Value : {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             "Net Gain Index": {},  # Net Gain: {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             "Odds Index": {},   # Odds: {game_number, game_name, prize_total_value, net_gain_loss, price, adjusted_odds}
             "Adjusted Odds": {},
             "Net Gain": {},
             "Game Names Array": [],
             "Pack Value": {},
             "Total Value": {},
             "Prize Availability": {},
             "Adjusted Odds Array": [],
             "Net Gain Array": [],
             "Pack Value Array": [],
             "Total Value Array": [],
             "Availability Array": [],
             "Odds Rank": [],
             "Total Prizes Rank": [],
             "Pack Value Rank": [],
             "Net Gain Rank": [],
             "Availability Rank": []
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
    from collections import OrderedDict
    urls = list(OrderedDict.fromkeys(urls))
    for url in urls:
        try:
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

            main_dict["Game Names Array"].append(game_name)

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

            main_dict["Adjusted Odds"].update({adjusted_odds: game_number})
            main_dict["Net Gain"].update({net_gain: game_number})
            main_dict["Pack Value"].update({guaranteed_per_pack_usd: game_number})
            main_dict["Total Value"].update({total_value: game_number})
            main_dict["Prize Availability"].update({avg_availability_chance: game_number})
            main_dict["Adjusted Odds Array"].append(adjusted_odds)
            main_dict["Adjusted Odds Array"].sort(reverse=True)
            main_dict["Net Gain Array"].append(net_gain)
            main_dict["Net Gain Array"].sort(reverse=True)
            main_dict["Pack Value Array"].append(guaranteed_per_pack_usd)
            main_dict["Pack Value Array"].sort(reverse=True)
            main_dict["Total Value Array"].append(total_value)
            main_dict["Total Value Array"].sort(reverse=True)
            main_dict["Availability Array"].append(avg_availability_chance)
            main_dict["Availability Array"].sort(reverse=True)

            print("\n")
            print(f'Ticket Info: {main_dict["ticket_info"][game_number]}')
            print(f'Odds Index: {adjusted_odds}: {main_dict["Odds Index"][adjusted_odds]}')
            print(f'Net Gain Index: {net_gain}: {main_dict["Net Gain Index"][net_gain]}')
            print(f'Pack Value Index: {guaranteed_per_pack_usd: }{main_dict["Pack Value Index"][guaranteed_per_pack_usd]}')
            print(f'Total Value Index: {total_value}: {main_dict["Total Value Index"][total_value]}')
            print(f'Prize Availability Index: {avg_availability_chance} {main_dict["Prize Availability Index"][avg_availability_chance]}')
        except:
            pass


def sortOddsIndex():  #Returns a list of lists, index value 1 leads to game number
    odds_temp_array = []
    for key in list(main_dict["Adjusted Odds"].keys()):
        odds_temp_array.append(key)
    odds_temp_array.sort(reverse=True)
    odds = odds_temp_array
    odds_temp_array = []
    for odd in odds:
        odds_temp_array.append((odd, main_dict["Adjusted Odds"][odd]))
    return odds


def sortNetGainIndex():  #Returns a list of lists, index value 1 leads to game number
    net_temp_array = []
    for key in list(main_dict["Net Gain"].keys()):
        net_temp_array.append(key)
    net_temp_array.sort(reverse=True)
    odds = net_temp_array
    net_temp_array = []
    for odd in odds:
        net_temp_array.append((odd, main_dict["Net Gain"][odd]))
    return odds


def sortPackValueIndex():  #Returns a list of lists, index value 1 leads to game number
    temp_array = []
    for key in list(main_dict["Pack Value"].keys()):
        temp_array.append(key)
    temp_array.sort(reverse=True)
    packs = temp_array
    temp_array = []
    for pack in packs:
        temp_array.append((pack, main_dict["Pack Value"][pack]))
    return temp_array


def sortTotalValueIndex():  #Returns a list of lists, index value 1 leads to game number
    temp_array = []
    for key in list(main_dict["Total Value"].keys()):
        temp_array.append(key)
    temp_array.sort(reverse=True)
    packs = temp_array
    temp_array = []
    for pack in packs:
        temp_array.append((pack, main_dict["Total Value"][pack]))
    return temp_array


def sortAvailabilityValueIndex():  #Returns a list of lists, index value 1 leads to game number
    temp_array = []
    for key in list(main_dict["Prize Availability"].keys()):
        temp_array.append(key)
    temp_array.sort(reverse=True)
    packs = temp_array
    temp_array = []
    for pack in packs:
        temp_array.append((pack, main_dict["Prize Availability"][pack]))
    return temp_array





getTicketDetails(GET_ALL_TICKET_URLS())
print('\n')
main.save_to_file(file_name=f"Scraped_Texas_Lottery_{datetime.date.today()}.txt", final_string=str(main_dict))
emailer.itoven_send_email_str(to="arthur@itoven-ai.co", subject=f"Lottery AI Report {datetime.date.today()}", message=str(main_dict))


sortedAvailability = sortAvailabilityValueIndex()
sortedTotalValues = sortTotalValueIndex()
sortedOddsValues = sortOddsIndex()
sortedNetGain = sortNetGainIndex()
sortedPackValue = sortPackValueIndex()

ranking_array_availability = []
ranking_array_net_gain = []
ranking_array_total_prizes = []
ranking_array_odds = []
ranking_array_packValue = []
# TODO BUT JUST COMPLETED BELOW FOR ONE CATEGORY




temp_array_pack_values = []
for i in range(len(main_dict["Pack Value Array"])-1):
    if main_dict["Pack Value Array"][i] not in temp_array_pack_values:
        temp_array_pack_values.append(main_dict["Pack Value Array"][i])
temp_array_availability_values = []
for i in range(len(main_dict["Availability Array"])-1):
    if main_dict["Availability Array"][i] not in temp_array_availability_values:
        temp_array_pack_values.append(main_dict["Availability Array"][i])
temp_array_odds_values = []
for i in range(len(main_dict["Adjusted Odds Array"])-1):
    if main_dict["Adjusted Odds Array"][i] not in temp_array_odds_values:
        temp_array_pack_values.append(main_dict["Adjusted Odds Array"][i])
temp_array_netgain_values = []
for i in range(len(main_dict["Net Gain Array"])-1):
    if main_dict["Net Gain Array"][i] not in temp_array_netgain_values:
        temp_array_pack_values.append(main_dict["Net Gain Array"][i])
temp_array_totalval_values = []
for i in range(len(main_dict["Total Value Array"])-1):
    if main_dict["Total Value Array"][i] not in temp_array_totalval_values:
        temp_array_pack_values.append(main_dict["Total Value Array"][i])

"""PACK VALUE SORTING"""
avail_added = []
odds_added = []
total_val_added = []
pack_val_added = []
net_gain_added = []
print("\n")
for i in range(0, len(main_dict["Pack Value Array"])-1):
    """AVAILABILITY SORTING"""
    availability = main_dict["Availability Array"][i]
    game_number = main_dict["Prize Availability Index"][availability]["Game Number"]
    ticket_info = main_dict['ticket_info'][game_number]
    price = ticket_info["Ticket Price USD"]

    game_name = ticket_info["Game Name"]
    rank = i + 1

    availability_sorted = {"Availability Rank": rank, "Game": game_name, "Game Number": game_number,
                           "Availability": availability, "Price": price}
    if availability_sorted in avail_added:
        ranking_array_availability.append(availability_sorted)
        #print(availability_sorted)

    """ODDS SORTING"""
    odds = main_dict["Adjusted Odds Array"][i]
    game_number = main_dict["Odds Index"][odds]["Game Number"]
    ticket_info = main_dict['ticket_info'][game_number]
    game_name = ticket_info["Game Name"]
    price = ticket_info["Ticket Price USD"]
    rank = i + 1
    availability_sorted = {"Adjusted Odds Rank": rank, "Game": game_name, "Game Number": game_number,
                           "Adjusted Odds": odds, "Price": price}
    if availability_sorted not in odds_added:
        ranking_array_odds.append(availability_sorted)
        #print(availability_sorted)

    """Net Gain SORTING"""
    net_gain = main_dict["Net Gain Array"][i]
    game_number = main_dict["Net Gain Index"][net_gain]["Game Number"]
    ticket_info = main_dict['ticket_info'][game_number]
    game_name = ticket_info["Game Name"]
    price = ticket_info["Ticket Price USD"]
    rank = i + 1
    availability_sorted = {"Net Gain Rank": rank, "Game": game_name, "Game Number": game_number,
                           "Net Gain": net_gain, "Price": price}
    if availability_sorted not in net_gain_added:
        ranking_array_net_gain.append(availability_sorted)
        #print(availability_sorted)

    """TOTAL VALUE PRIZES SORTING"""
    total_value = main_dict["Total Value Array"][i]
    game_number = main_dict["Total Value Index"][total_value]["Game Number"]
    ticket_info = main_dict['ticket_info'][game_number]
    game_name = ticket_info["Game Name"]
    price = ticket_info["Ticket Price USD"]
    rank = i + 1
    availability_sorted = {"Total Prizes Rank": rank, "Game": game_name, "Game Number": game_number,
                           "Total Value Prizes": total_value, "Price": price}
    if availability_sorted not in total_val_added:
        ranking_array_total_prizes.append(availability_sorted)
        #print(availability_sorted)


    pack_value = main_dict["Pack Value Array"][i]
    game_number = main_dict["Pack Value Index"][pack_value]["Game Number"]
    ticket_info = main_dict['ticket_info'][game_number]
    game_name = ticket_info["Game Name"]
    price = ticket_info["Ticket Price USD"]
    rank = i + 1
    availability_sorted = {"Pack Value Rank": rank, "Game": game_name, "Game Number": game_number, "Pack Value": pack_value, "Price": price}
    if availability_sorted not in pack_val_added:
        ranking_array_packValue.append(availability_sorted)
        #print(availability_sorted)
    print("\n")

def TicketInfo(game_number):
    return main_dict['ticket_info'][game_number]


for ticket_number in main_dict["Ticket Numbers"]:
    ticket_info = TicketInfo(ticket_number)

master_dict_list = []
boof_array = []
for listed in [ranking_array_total_prizes, ranking_array_odds, ranking_array_availability, ranking_array_packValue, ranking_array_net_gain]:
    for dicted in listed:
        if str(dicted).split(", ", 1)[1] not in boof_array:
            master_dict_list.append(dicted)
            boof_array.append(str(dicted).split(", ",1)[1])
            print(dicted)
    print("\n")



