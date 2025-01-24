"""
Title:
    Game Selector

Author:
    Terrence Jackson

Source:
    Sometimes it's hard to pick what game to play

Summary:
    Gets filepaths to all game executables, generates a df that includes data on how to execute, generates a random list, and chooses one to open

Future:
    Don't have filepaths hardcoded, create some kind of generator that takes user input
    Maybe make a gui for the die roll?
    Make something so you can select single player or co-op game lists to roll from
    Change from df storage to Game object storage
"""

import math
import os
import random
import subprocess
from datetime import datetime

import pandas as pd

# class Game(object):
#     def __init__(self) -> None:
#         self.name = ""
#         self.type = ""
#         self.location = ""

#     def __init__(self, name, type, location) -> None:
#         self.name = name
#         self.type = type
#         self.location = location

#     def run(self):
#         if self.type == "exe":
#             os.system(f'cmd /c "{self.location}"')
#         else:
#             subprocess.Popen(f'explorer /select,"{self.location}"')


def generate_seed() -> float:
    """Generates a random seed for the random number generator"""
    now = datetime.now()
    date = now.day / math.pi
    time = (now.second + now.hour) / now.minute
    seed = (date * time) - math.pow(time, (date * -1))
    return seed


def get_games_from_dir(df: pd.DataFrame, dir: str, skip: list = []) -> pd.DataFrame:
    """
    This function will find game exes if a launcher stores game files in a centralized location

    Args:
        - string dir = directory where the launcher stores game files
        - list skip = list of names to skip within that directory, deafaults to empty

    Returns:
        A data frame of the games it found
    """
    for file in os.scandir(dir):
        if file.name in skip:
            pass
        else:
            exe = get_exe(file)
            if exe == "":
                # if exe has not been found, look through one layer of subfolders
                for _file in os.scandir(file.path):
                    if exe == "":
                        exe = get_exe(_file)

            # fill in data and move on to next file
            df = fill_df(df, file.name, "exe", exe)

    return df


def fill_df(old_df, _name: str, _type: str, _location: str) -> pd.DataFrame:
    """Takes in data and puts it into the df, returns df"""
    data = {"name": _name.strip(), "type": _type.strip(), "location": _location.strip()}
    new_df = pd.DataFrame(data, index=[len(old_df)])
    df = pd.concat([old_df, new_df])
    return df


def get_exe(in_file: os.DirEntry) -> str:
    """Finds executables given filepath. Exception for Civ 6 since Steam did weird shit"""
    if in_file.path.endswith("Civilization VI"):
        return "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\LaunchPad\LaunchPad.exe"
    for file in os.scandir(in_file.path):
        if file.path.endswith("exe"):
            for word in in_file.name.split(" "):
                if file.name.lower().startswith(word[0].lower()):
                    return file.path
    return ""


def get_games() -> pd.DataFrame:
    """Reads through hardcoded dict of game locations, generates df of all games"""
    df = pd.DataFrame(columns=["name", "type", "location"])

    game_locations = {
        "Steam": [
            "exe",
            "C:\Program Files (x86)\Steam\steamapps\common",
            ["Steam Controller Configs", "Steamworks Shared", "Tabletop Simulator"],
        ],
        "The Sims 4": "C:\Program Files (x86)\Origin Games\The Sims 4\Game\Bin\TS4_x64.exe",
        "Genshin": "C:\Program Files\Genshin Impact\launcher.exe",
        "WoW": "C:\Program Files (x86)\World of Warcraft\World of Warcraft Launcher.exe",
        "Hearthstone": "C:\Program Files (x86)\Hearthstone\Hearthstone.exe",
        "Overwatch": "C:\Program Files (x86)\Overwatch\Overwatch Launcher.exe",
        "League": '"C:\Riot Games\Riot Client\RiotClientServices.exe" --launch-product=league_of_legends --launch-patchline=live',
        "Legends of Runeterra": '"C:\Riot Games\Riot Client\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live',
        "Valorant": '"C:\Riot Games\Riot Client\RiotClientServices.exe" --launch-product=valorant --launch-patchline=live',
        "Darkest 2": [
            "fe",
            "com.epicgames.launcher://apps/6ff9efdef6dc45ecb40ed20fcd2c4621%3A86d5286d1b254e10902d6e2d7fc3bb76%3ASuka?action=launch&silent=true",
        ],
        "Ruined King": [
            "fe",
            "com.epicgames.launcher://apps/a69c5a82682c43148e4e2542fe2fcd0f%3A8f2c787eaf124dd2b549fbffd0edd61e%3A7f048ed7208d49588b1867edc0ab368a?action=launch&silent=true",
        ],
        "Runescape": [
            "fe",
            "rs-launch://www.runescape.com/k=5/l=$(Language:0)/jav_config.ws",
        ],
    }

    for key in game_locations:
        if type(game_locations[key]) == list:
            if game_locations[key][0] == "exe":
                try:
                    df = get_games_from_dir(
                        df, game_locations[key][1], game_locations[key][2]
                    )
                except IndexError:
                    df = get_games_from_dir(df, game_locations[key][1])
            elif game_locations[key][0] == "fe":
                df = fill_df(df, key, "file explorer", game_locations[key][1])
        else:
            df = fill_df(df, key, "exe", game_locations[key])
    return df


def generate_die(df: pd.DataFrame) -> pd.DataFrame:
    """Picks 20 random games from the games df and returns as a df"""
    out_df = pd.DataFrame(columns=df.columns.to_list())
    for i in range(18):
        game_selection = random.randrange(0, len(df) - 1)
        game = df.iloc[game_selection]
        while game["name"] in out_df["name"].to_list():
            game_selection = random.randrange(0, len(df) - 1)
            game = df.iloc[game_selection]
        out_df = fill_df(out_df, game["name"], game["type"], game["location"])
    return out_df


def main():
    """Runtime function"""
    _seed = generate_seed()
    random.seed(_seed)
    choice = random.randrange(1, 20)

    df = get_games()
    df = generate_die(df)

    if choice == 1:
        print("Crit fail! Go do chores.")
    elif choice == 20:
        print("Nat 20! Go buy a new game to play.")
    else:
        choice -= 2
        cmd: str = df.iloc[choice]["location"]
        if df.iloc[choice]["type"] == "exe":
            os.system(f'cmd /c "{cmd}"')
        elif df[choice]["type"] == "fe":
            subprocess.Popen(f'explorer /select,"{cmd}"')


if __name__ == "__main__":
    main()
