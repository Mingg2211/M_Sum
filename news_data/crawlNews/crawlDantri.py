from bs4 import BeautifulSoup
import urllib.request
import json
import os
class Data:
    def __init__(self, title, description, paras) -> None:
        self.title = title
        self.description = description
        self.paras = paras

# Initialize the JSON data object
data = {"content": []}

# url = 'https://dantri.com.vn/the-gioi/ong-kim-jong-un-yeu-cau-tang-toc-phat-trien-tiem-luc-quan-su-20230210132924777.htm'

def crawl_News(url):
    if "dantri.com.vn" not in url:
        return "khong dung duoc"
    else:
        json_folder = "news_data//crawlNews//json_data"
        cut = url.split("/")
        file_name = cut[-1].replace(".htm", "").replace("-","_")
        file_name = str(file_name) + ".json"
        json_storage = os.path.join(json_folder, file_name)
        

        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        # Get title
        title = soup.select('h1.title-page')[0].text.strip()
        # print(title)

        # Get description
        description = soup.select('h2.singular-sapo')[0].text.strip()
        # print(description)

        # Get content
        content = soup.find('div', class_="singular-content")
        p_tags = content.find_all("p")

        paras = []
        for p in p_tags:
            para = p.text
            paras.append(para)
        # print(paras)

        # Store the data in a Data object
        content = Data(title, description, paras)

        # Append the new data to the content list
        data["content"].append({"title": content.title, "description": content.description, "paras": content.paras})

        # Write the JSON data object to a file
        with open(json_storage, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return "Data written successfully to data.json"

# crawl_News(url)