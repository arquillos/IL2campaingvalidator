# Il-2 Campaign Validator
Based in the work of andqui
- [Il-2 Campaign Validator v1.0 release](https://www.sas1946.com/main/index.php?topic=65584.0
)

---

## Script Execution
First: edit the `settings.ini` file and set the proper PATHs


```bash
# Activate the python virtual environment in a powershell 
.\.venv\Scripts\Activate.ps1

# Activate the python virtual environment in a cmd
.\.venv\Scripts\Activate.bat

# Execute the script
python .\main.py

# Alternatively, execute the script with the new CLI
pip install -r requirements.txt  # This command is needed only once
python .\cli.py
```


The script will read the settings from the `settings.ini`file and display them
The user will have the option to modify the settings manually
- `Modify any setting? [y/N]:`

The "Final" settings will be displayed and the user have the option to execute the campaign validator or abort the execution
- `Proceed with these settings? [Y/n]:`

The report is in the "output" folder (by default)


Important!
When the script finished the execution you may get printed issues like these ones:
```
Failed to decode e:\IL-2 Sturmovik 1946 v4.15.1\MODS\STD\com\maddox\il2\objects\chief.ini as UTF-8; retrying with Windows-1251 encoding
Failed to decode e:\IL-2 Sturmovik 1946 v4.15.1\MODS\STD\com\maddox\il2\objects\static.ini as UTF-8; retrying with Windows-1251 encoding
```
The script worked fine!
Those issues are not error. The script is complaining regarding the encoding format of those files.
They are there for debugging purposes only.

---

## SIMPLE INITIAL INSTRUCTIONS
- Settings.txt and Common Conversions.txt must be in the same folder as the executable
- Open Settings.txt to control the input parameters to the program. You will need to specify:
  - Path to the STD folder of whatever Il-2 installation you are using, so the program can see what objects and weapons are available
  - Path to the skins folder
  - Path to the campaign you want to analyze. There must be a campaign.ini present in this folder to tell the program what missions to loop through
  - [Optional] Path to the output destination (where you want the report to be written)
    - The default is to create an Output folder in the same folder as the .exe
  - Specify if you want the program to auto-convert some features of the missions for you. To just get a report, make all of the last three entries 0. To auto-convert several aspects of missions, read on below.
- Once the settings file is established as above, run the .exe and the report and any auto-corrected missions will be generated at the specified output folder.

## MORE DETAILED INFO/INSTRUCTIONS
In order, for each mission, the program reports:
- The map used for the mission
- The set mission date. Old campaigns are either missing this entirely or become auto-set to July 1940 if opened up and saved in the FMB, and you will be notified of this
- The aircraft used in a list, so you can easily look over it and see if there are any hacks/substitute planes that can be easily replaced
  - If a loadout for an aircraft has changed or is not available in your current Il-2 install you will be warned of this as well
- Alerts if any of the skins requested by the mission can't be found in your install
- A list of moving ground/sea vehicles used in the mission (chiefs), followed by alerts for any errors or missing ones
- A list of stationary objects used, again with errors of any that are missing from your current install
- Finally, alerts if the stationary aircraft don't have markings enabled. This can happen when converting from old mission formats.

What to do if you open up a campaign and it's full of errors? Who wants to sit for hours hand correcting stationary aircraft markings or changing hundreds of object paths? That's where the last three options in the settings file can help. When any one of these three flags is enabled, the program will spit out copies of all the missions with changes/corrections automatically made.

- Auto-correct static aircraft markings?=1. This will look for stationary aircraft with no skins applied and no markings and enable markings for you

- Auto-replace stationary objects?=1. One big problem when converting from, say, HSFX to BAT and vice versa, is that they use different stationary object paths. For example, in HSFX, the Bismarck is ships.Ship$Bismarck, whereas in BAT it's ships.ShipNew$Bismarck. BAT is missing the default Ju-87D-3 static aircraft, and instead has JU_87D3j. The Common Conversions.txt file has a list of swaps you want to automatically make to fix these errors. In this file, there are pairs separated by a comma. On the left is what you want the program to find in your mission file, on the right is what you want to replace it with. With this download comes a partial list of these, the intent is for you to modify/replace them with whatever objects you get errors in in the report so you don't have to replace them all by hand.

- Make all except player flight AI-only?=0. This one I made for myself, is of marginal usefulness. I play co-op occasionally with some friends, and often make the co-op missions from campaigns. This will automatically set the non-player flights in a mission as AI-only so they don't clog up the co-op aircraft selection dialogue in-game. Little things, but I use it, so it's here.


## Development instructions

### Requirements
- Python 3.14

### Download code
```bash
git clone git@github.com:arquillos/IL2campaingvalidator.git
cd IL2campaingvalidator
```

### Installation of a virtual environment
```bash
python3 -m venv .venv

# Activate the python virtual environment in a powershell 
.\.venv\Scripts\Activate.ps1

# Activate the python virtual environment in a cmd
.\.venv\Scripts\Activate.bat

# This is needed if we execute the cli.py script
pip install -r requirements.txt
```
---
