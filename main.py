import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

if __name__ == "__main__":
    print("Please Insert The Link : ", end="")
    entered_data = input("")
    r1 = requests.get(entered_data.strip())
    soup = BeautifulSoup(r1.text, "html.parser")
    all_data = str(soup.find("script", attrs={"id": "__NEXT_DATA__", 'type': 'application/json'}).contents[0])
    clean_dict = json.loads(all_data)
    team_id = clean_dict["props"]["pageProps"]["teamContext"]["data"]["teamId"]
    season_id = clean_dict["props"]["pageProps"]["tracking"]["ssid"]
    link = f"https://production.api.maxpreps.com/gatewayweb/react/team-season-player-stats/rollup/v1?teamid=" \
           f"{team_id}&sportseasonid={season_id}"
    r2 = requests.get(link)
    response_dict = r2.json()
    for i in response_dict["data"]["groups"]:
        if i["name"] == "Batting" or i["name"] == "Pitching":
            file_name = i["name"]
            for j in i["subgroups"]:
                if j["name"] != "":
                    file_name = j["name"]
                header_list = []
                for k in j["stats"]["columns"]:
                    header_list.append(k["header"])
                header_value_list = []
                for k in j["stats"]["rows"]:
                    row_list = []
                    for m in range(len(k["columns"])):
                        if m == 0:
                            row_list.append(int(k["columns"][m]["value"]))
                        else:
                            row_list.append(k["columns"][m]["value"])
                    header_value_list.append(row_list)
                print(f"\n\t\tGetting {file_name}")
                header_value_list = sorted(header_value_list, key=lambda x: x[0])
                df = pd.DataFrame(header_value_list, columns=header_list)
                df.to_csv(file_name + ".csv")
