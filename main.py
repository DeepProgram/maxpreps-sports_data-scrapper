import traceback
from json import JSONDecodeError
from typing import Optional
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


def get_team_id_season_id(url: str) -> Optional[list]:
    try:
        response = requests.get(url)
    except requests.exceptions.Timeout:
        print("Request Timed Out.. Please Check Internet Connection Or Use A Valid Proxy..")
        return None
    except requests.exceptions.TooManyRedirects:
        print("Url Is Not Valid.. Please check the demo url in github and try url like that..")
        return None
    except requests.exceptions.RequestException as e:
        print("Error Occurred While Fetching Data ", e)
        return None
    all_data = ""
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        all_data = str(soup.find("script", attrs={"id": "__NEXT_DATA__", 'type': 'application/json'}).contents[0])
    except AttributeError:
        print("Couldn't Parse HTML Data....Check The URL Again....")
        return None
    except Exception:
        print(traceback.format_exc())
    try:
        clean_dict = json.loads(all_data)
    except JSONDecodeError as e:
        print("JSON Data Couldn't Be Parsed....", e)
        return None
    try:
        extracted_team_id = clean_dict["props"]["pageProps"]["teamContext"]["data"]["teamId"]
        extracted_season_id = clean_dict["props"]["pageProps"]["tracking"]["ssid"]
    except KeyError:
        print("Desired Data Not Found....Website May Have Changed JSON File....")
        return None
    return [extracted_season_id, extracted_team_id]


def get_player_stats_dict(url: str) -> dict:
    response = requests.get(url)
    return response.json()


def get_selected_groups() -> list:
    return ["Batting", "Pitching"]


def get_header_list(each_subgroup: dict) -> list:
    return [header_column["header"] for header_column in each_subgroup]


def get_column_data_of_one_row(each_row: dict) -> list:
    column_value_list = []
    for column_index, column_element in enumerate(each_row):
        if column_index == 0:
            column_value_list.append(int(column_element["value"]))
        else:
            column_value_list.append(column_element["value"])
    return column_value_list


def get_all_row_stats(all_row: list) -> list:
    return [get_column_data_of_one_row(row["columns"]) for row in all_row]


def sort_and_save_to_csv(file_name: str, header_list: list, rows_list: list):
    rows_list = sorted(rows_list, key=lambda x: x[0])  # Sorting Based On Position
    df = pd.DataFrame(rows_list, columns=header_list)
    df.to_csv(file_name + ".csv")


def process_subgroups(group: dict, file_name: str):
    for subgroup in group:
        if subgroup["name"] != "":
            file_name = subgroup["name"]
        try:
            header_list = get_header_list(subgroup["stats"]["columns"])
            rows_list = get_all_row_stats(subgroup["stats"]["rows"])
        except KeyError:
            print("Desired Data Not Found....Website May Have Changed JSON File....")
            return
        print(f"\n\t\tGetting {file_name}")
        sort_and_save_to_csv(file_name, header_list, rows_list)


def process_groups(player_stats_groups: dict):
    for group in player_stats_groups:
        if group["name"] in get_selected_groups():
            try:
                file_name = group["name"]
                process_subgroups(group["subgroups"], file_name)
            except KeyError:
                print("Desired Data Not Found....Website May Have Changed JSON File....")
                return
        else:
            print(f"\n{group['name']} Stats Is Excluded [Check get_selected_groups() Function To Include It]....")


def main():
    print("Please Insert The Link : ", end="")
    entered_data = input("")
    season_id_team_id = get_team_id_season_id(entered_data.strip())
    if season_id_team_id is not None:
        link = f"https://production.api.maxpreps.com/gatewayweb/react/team-season-player-stats/rollup/v1?teamid=" \
               f"{season_id_team_id[1]}&sportseasonid={season_id_team_id[0]}"
        response_dict = get_player_stats_dict(link)
        try:
            process_groups(response_dict["data"]["groups"])
        except KeyError:
            print("Desired Data Not Found....Website May Have Changed JSON File....")
            return


if __name__ == "__main__":
    main()
 
