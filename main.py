import fire
from src.graph import get_graph
from src.visualize_graph import plot_G
from src.scrape import get_main_page, get_main_table, save_jumpscares, get_links, get_detailed_data, save_data_details, add_jump_ratings


def scrape_data():
    soup = get_main_page()
    jumpscares = get_main_table(soup)
    good_links = get_links(soup)
    jumpscares['link'] = good_links
    save_jumpscares(jumpscares)
    data_details = get_detailed_data(good_links)
    data_details = add_jump_ratings(data_details, jumpscares)
    save_data_details(data_details)


def graph():
    G = get_graph()
    plot_G(G)


if __name__ == '__main__':
    fire.Fire({
        'graph': graph,
        'scrape_data': scrape_data
    })
