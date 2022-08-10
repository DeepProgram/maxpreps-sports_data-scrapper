import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


def get_team_id_season_id(url: str) -> list:
    try:
        response = requests.get(url)
    except requests.exceptions.Timeout:
        print("Request Timed Out.. Please Check Internet Connection Or Use A Valid Proxy..")
        return ["-1", "-1"]
    except requests.exceptions.TooManyRedirects:
        print("Url Is Not Valid.. Please check the demo url in github and try url like that..")
        return ["-1", "-1"]
    except requests.exceptions.RequestException as e:
        print("Error Occurred While Fetching Data ", e)
        return ["-1", "-1"]

    soup = BeautifulSoup(response.text, "html.parser")
    all_data = str(soup.find("script", attrs={"id": "__NEXT_DATA__", 'type': 'application/json'}).contents[0])
    clean_dict = json.loads(all_data)
    extracted_team_id = clean_dict["props"]["pageProps"]["teamContext"]["data"]["teamId"]
    extracted_season_id = clean_dict["props"]["pageProps"]["tracking"]["ssid"]
    return [extracted_season_id, extracted_team_id]


def get_player_stats_dict(url: str) -> dict:
    response = requests.get(url)
    return response.json()


def get_selected_groups() -> list:
    return ["Batting", "Pitching"]


def get_header_list(each_subgroup: dict) -> list:
    subgroup_header_list = []
    for header_column in each_subgroup:
        subgroup_header_list.append(header_column["header"])
    return subgroup_header_list


def get_column_data_of_one_row(each_row: dict) -> list:
    column_value_list = []
    for column in range(len(each_row)):
        if column == 0:
            column_value_list.append(int(each_row[column]["value"]))
        else:
            column_value_list.append(each_row[column]["value"])
    return column_value_list


if __name__ == "__main__":
    print("Please Insert The Link : ", end="")
    entered_data = input("")
    season_id, team_id = get_team_id_season_id(entered_data.strip())
    if season_id == "-1" and team_id == "-1":
        print("Couldn't Fetch Data.. Next Execution Can Not Be Done..")
    else:
        link = f"https://production.api.maxpreps.com/gatewayweb/react/team-season-player-stats/rollup/v1?teamid=" \
               f"{team_id}&sportseasonid={season_id}"
        response_dict = get_player_stats_dict(link)
        for group in response_dict["data"]["groups"]:
            if group["name"] in get_selected_groups():
                file_name = group["name"]
                for subgroup in group["subgroups"]:
                    if subgroup["name"] != "":
                        file_name = subgroup["name"]
                    header_list = get_header_list(subgroup["stats"]["columns"])
                    rows_list = []
                    for row in subgroup["stats"]["rows"]:
                        column_list = get_column_data_of_one_row(row["columns"])
                        rows_list.append(column_list)
                    print(f"\n\t\tGetting {file_name}")
                    rows_list = sorted(rows_list, key=lambda x: x[0])  # Sorting Based On Position
                    df = pd.DataFrame(rows_list, columns=header_list)
                    df.to_csv(file_name + ".csv")
