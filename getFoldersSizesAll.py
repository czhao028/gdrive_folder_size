from gdrive_calculator import service, credentials, GoogleDriveSizeCalculate, ID_TO_PARENT_DICT, ID_TO_NAME_DICT
from googleapiclient.discovery import build

input_file_name = "MarketingAndCommunications_Photos.txt"
will_use_own_file = input("\nWould you like to provide a file of comma separated Google Drive links to get file Size of? Y/N:")
answer = will_use_own_file.strip().lower()
if answer == "y":
    input_file_name = input("\nPaste file name for comma-separated list of Google Drive links:").strip()
print(f"Using file name {input_file_name}")

service =  build('drive', 'v3', credentials=credentials, cache_discovery=False)
with (open(input_file_name, "r") as in_file):
    for line in in_file.readlines():
        line = line.strip()
        links = line.split(", ")
        for link in links:
            calculator = GoogleDriveSizeCalculate(service)
            calculate = calculator.gdrive_checker(link)
            if not calculate is None:
                print('')
                for k, v in calculate.items():
                    print(f'{k.title()}:', v)
