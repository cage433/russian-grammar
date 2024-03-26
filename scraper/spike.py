from bs4 import BeautifulSoup, Tag


def file_contents():
    with open('/scraper/test_resources/scraped_pages/авторизовывать.html', 'rt', newline='') as f:
        return f.read()

def parse_file():
    text = file_contents()
    soup = BeautifulSoup(text, 'html.parser')
    divs = soup.body.find("div", {"class": 'NavHead'})
    print(divs.contents[-1])
    table = soup.body.find("div", {"class": 'NavContent'})
    rows = table.find_all('tr')
    for row in rows:
        # print(row.contents)
        texts = [
            c.text.strip() for c in row.contents
            if isinstance(c, Tag)
        ]
        print(texts)

if __name__ == '__main__':
    parse_file()