from getfilelistpy import getfilelist
from httplib2 import Http

import gdrive_calculator
from gdrive_calculator import service, credentials, GoogleDriveSizeCalculate

BYTES_LIMIT = 100 * 1073741824
ID_TO_NAME_DICT = {}
#Here is the code that will return the index if the value is found, otherwise the index of the item that is closest to that value, hope it helps.
def searchTupleArray(array, start_idx, end_idx, search_val, occupied_indices):
   bool_index_already_in_use = (occupied_indices.get(start_idx) != None)
   if( start_idx == end_idx ):
      return start_idx if (array[start_idx][0] <= search_val and not bool_index_already_in_use) else -1

   mid_idx = start_idx + (end_idx - start_idx) // 2

   if( search_val < array[mid_idx][0] ):
      return searchTupleArray(array, start_idx, mid_idx, search_val, occupied_indices)

   ret = searchTupleArray(array, mid_idx + 1, end_idx, search_val, occupied_indices)
   return -1 if bool_index_already_in_use else mid_idx if ret == -1 else ret
   #return mid_idx if ret == -1 else ret

def verifyAllElemsSumToLessThanMaxBytes(list_of_lists):
    global BYTES_LIMIT
    for pairing in list_of_lists:
        its_sum = 0
        for size, id, name in pairing:
            its_sum += size
        if its_sum > BYTES_LIMIT:
            raise Exception(f"Bug in your code: pairing {pairing} not compliant")

def getCombinedFolderNameOfListOfFoldersInPath(list_of_folder_ids, service):
    global ID_TO_NAME_DICT
    combined_names = []
    for folder_id in list_of_folder_ids:
        if ID_TO_NAME_DICT.get(folder_id) == None:
            drive_file = service.files().get(fileId=folder_id, fields="name",
                                                supportsTeamDrives=True).execute()
            combined_names.append(drive_file['name'])
        else:
            combined_names.append(ID_TO_NAME_DICT.get(folder_id))
    return "_".join(combined_names)



def findSubFoldersWithLessThanMaxBytes(folder_id, service):
    global BYTES_LIMIT
    #We're given that folder_id is a folder that is > 100GB
    id_folders_already_being_moved = dict()
    recursion_tree_folders_being_moved = []
    folders_not_moved = []
    #So we can create a newly moved folder in the new drive that's PARENTFOLDER1_SUBPARENTFOLDER2_SUBPARENTFOLDER3
    #i.e. [['1rbz6Lv3sQpAnEebm5L7taLOOiMB8_DsX', '1DNa_D0cpy1p9Hu0DptTn-4f_Gjji0TNc'], ['1rbz6Lv3sQpAnEebm5L7taLOOiMB8_DsX', '1WF9Jcv81PEdHFR5THMBvAjJJ59wrdSGU', '1uGC0TOLzBjKqX-6XesXV-_2Su0QLO9G2']]
    resource = {
        "oauth2": credentials,
        #"id": GoogleDriveSizeCalculate.getIdFromUrl(
            #"https://drive.google.com/drive/folders/1rpk2EdCGGkIRXd43xRKZY0H7iRbaDbmK"),
         "id": folder_id,
        "fields": "files(name,id)",
    }
    res = getfilelist.GetFolderTree(resource)  # or r = getfilelist.GetFolderTree(resource)
    for folder_list in res["id"]:
        if len(folder_list) < 2: continue
        current_folder_id = folder_list[-1]
        parent_folder_id = folder_list[-2]
        if id_folders_already_being_moved.get(parent_folder_id) != None: continue
        calculator = GoogleDriveSizeCalculate(service)
        childFolderCalculate = calculator.gdrive_checker(current_folder_id)
        if childFolderCalculate["bytes"] < BYTES_LIMIT:
            id_folders_already_being_moved[childFolderCalculate["id"]] = 1
            recursion_tree_folders_being_moved.append((childFolderCalculate["bytes"],
                                                       #getCombinedFolderNameOfListOfFoldersInPath(folder_list, service),
                                                       childFolderCalculate["name"]))
        else:
            print(f"Child folder id {childFolderCalculate["id"]}, name {childFolderCalculate["name"]} was not moved")
            folders_not_moved.append(childFolderCalculate["id"])
    #validate that all folders at least appear in subfolders that are being moved
    for folder_not_moved in folders_not_moved:
        exists = False
        for folder_size_moved, folder_id_moved_list, folder_name_moved in recursion_tree_folders_being_moved:
            exists = exists or (folder_not_moved in folder_id_moved_list)
        if not exists:
            raise Exception(f"Folder {folder_not_moved} NOT found, in folders to move, as a parent tree")

    return recursion_tree_folders_being_moved


"""
Instructions
"""
# 0. Prompt for folder to split into < 100 GB (use g_drive_folder_size code)
# 1. Iterate in folder: Find optimal pairing of highest_storage, binarySearch(folders, remaining_data) WHILE sum(grouping) < 100GB. Make sure to exclude digits that are already paired, via dictionary
# 2. Store this optimal pairing
# 3. Ask the user for N number of Google Drive folders to split the original folder into
# 4. Throw exception if not N number are given
# 5. Assign optimal groupings to google drive folders

# SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
#
# store = file.Storage('token.json')
# creds = store.get()
# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets('rrc_crds.json', SCOPES)
#     creds = tools.run_flow(flow, store)
input_file_name = "MarketingAndCommunications_Videos.txt"
will_use_own_file = input("\nWould you like to provide a file of comma separated Google Drive links to separate into 100 GB folders? Y/N:")
answer = will_use_own_file.strip().lower()
if answer == "y":
    input_file_name = input("\nPaste file name for comma-separated list of Google Drive links:").strip()
print(f"Using file name {input_file_name}")

folder_sizeidname_tuples = []
with open(input_file_name, "r") as in_file:
    for line in in_file.readlines():
        line = line.strip()
        links = line.split(", ")
        for link in links:
            # ~ Complete creating the service variable and then pass it here
            calculator = GoogleDriveSizeCalculate(service)  # GoogleDriveSizeCalculate(service)
            calculate = calculator.gdrive_checker(link)
            print(f"Folder name {calculate['name']} is size {calculate['size']}")
            if calculate['bytes'] < BYTES_LIMIT:
                folder_sizeidname_tuples.append((int(calculate['bytes']), calculate['id'], calculate['name']))
            else:
                print("Getting Folder tree, adding subfolders to folder_sizeidname_tuples")
                #in the format, [[1024, ["id1", "id2"], "subsubFolderName"], ....]
                list_of_subfolders = findSubFoldersWithLessThanMaxBytes(calculate['id'], service)


pairings = []
picked_indices = dict()
folder_sizeidname_tuples.sort(key=lambda x: x[0])
for idx in range(len(folder_sizeidname_tuples)-1, -1, -1):
    folder_size, folder_id, folder_name = folder_sizeidname_tuples[idx]
    if picked_indices.get(idx) != None: continue
    list_grouping_this = list()
    candidate_folder_tuple = folder_sizeidname_tuples[idx]
    candidate_index = idx
    remaining_bytes = BYTES_LIMIT
    while remaining_bytes - candidate_folder_tuple[0] > 0:
        list_grouping_this.append(candidate_folder_tuple)
        picked_indices[candidate_index] = 1
        remaining_bytes = remaining_bytes - candidate_folder_tuple[0]
        index_found = searchTupleArray(folder_sizeidname_tuples, 0, len(folder_sizeidname_tuples), remaining_bytes, picked_indices)
        if index_found > 0:
            candidate_folder_tuple = folder_sizeidname_tuples[index_found]
            candidate_index = index_found
    pairings.append(list_grouping_this)

verifyAllElemsSumToLessThanMaxBytes(pairings)
print(pairings)
resource = {
    "oauth2": credentials,
    "id": GoogleDriveSizeCalculate.getIdFromUrl("https://drive.google.com/drive/folders/1rbz6Lv3sQpAnEebm5L7taLOOiMB8_DsX"),
    #"id": "1MEun1wOZExIqw89hl78X_Dd5W2mlzD-n",
    "fields": "files(name,id)",
}
res = getfilelist.GetFolderTree(resource) # or r = getfilelist.GetFolderTree(resource)
print(res)

# 2. Store this optimal pairing
# 3. Ask the user for N number of Google Drive folders to split the original folder into
# 4. Throw exception if not N number are given
# 5. Assign optimal groupings to google drive folders