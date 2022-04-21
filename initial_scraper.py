import main
import selenium.webdriver, selenium


driver = selenium.webdriver.Chrome()

main_dict = {"base_url": "https://www.texaslottery.com/export/sites/lottery/Games/Scratch_Offs/index.html#",
             "price_points": [1, 2, 3, 5, 10, 20, 30, 50]}


def OpenLotteryHomePage(price_point):  # in dollars, find the lottery page to extract info
    mod_url = f"{main_dict['base_url']}{price_point}"
    print(mod_url)
    return driver.get(mod_url)


def get_pg_source(url):
    return driver.page_source


def GET_TICKET_URLS_PRICE_POINT(price_point=0):  # in dollars
    OpenLotteryHomePage(main_dict["price_points"][price_point])  # Each price point has a different URL which leads to its tickets
    mod_url_src = (get_pg_source(driver.current_url))  # Obtain Page Source for Ticket Catalogue Page
    ticket_numbers_at_pricePoint = (main.FIND_ALL_SUBSTRINGS_BETWEEN_2_STRINGS(mod_url_src, ".html_", '.html"'))  # Get All Ticket Numbers at this price point
    pricePointTicketUrls = main.INJECT_URL_MODIFIERS_BETWEEN_2_STRINGS(url_prefix="https://www.texaslottery.com/export/sites/lottery/Games/Scratch_Offs/details.html_", url_suffix=".html", injections=ticket_numbers_at_pricePoint)
    return pricePointTicketUrls


print(GET_TICKET_URLS_PRICE_POINT())

# TODO ACCESS EACH URL WE FOUND AND GET ODDS AND ADD TO JSON OR DICT WITH NAME OF TICKET AND URL TO TICKET

