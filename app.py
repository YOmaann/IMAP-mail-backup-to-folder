import json
from imap_tools import MailBox
import os
from pathlib import Path

with open('config.json') as file :
    # print(data)

    data = file.read()
    tmp = json.loads(data)
    USER = tmp["username"]
    PASSWORD = tmp["password"]
    SERVER = tmp["server"]
    FOLDER = tmp["folder"]
    OUT_FOLDER = tmp["output_folder"]

    print(FOLDER)

with open('read.json', 'r') as read_mails :
    data = read_mails.read()
    tmp = json.loads(data)
    UIDS = tmp["uids"]
    

# print(USER, PASSWORD, SERVER)
with MailBox(SERVER).login(USER, PASSWORD, FOLDER) as mb:
    print(f"Reading mails in {mb.folder.list()}..")
    
    MAIL_COUNT = 0
    BACKED_COUNT = 0
    BACKED_UIDS = []
    for msg in mb.fetch(mark_seen=False):
        #reverse limit mark_seen
        MAIL_COUNT += 1
        uid_tmp = msg.uid

        if uid_tmp not in UIDS:
            BACKED_COUNT += 1
            print(f"backing up mail #{uid_tmp}..")
            msg_sub = msg.subject
            msg_from = msg.from_
            msg_text = msg.text
            msg_html = msg.html
            msg_date = msg.date

            out_folder = f"[{msg_date}] {msg_sub} - {uid_tmp}".replace(":", "").replace("\\", "").replace("?", "").replace(".", " ").replace("|", "")
            out_folder_path = f"{OUT_FOLDER}/{out_folder}"

            # out_folder_path = os.path.abspath(out_folder_path)

            # out_folder_path = codecs.decode(out_folder_path, "unicode_escape")
            # print(out_folder_path)
            path_obj = Path(out_folder_path)

            if not path_obj.exists():
                os.makedirs(out_folder_path)

            to_write = f"UID = {uid_tmp}\n\n"
            to_write += f"FROM = {msg_from}\n\n"
            to_write += f"SUBJECT = {msg_sub}\n\n"
            to_write += f"Content :\n{msg_text}"

            with open(f"{out_folder_path}/{uid_tmp}.txt", 'w', encoding = "utf-8") as f:
                f.write(to_write)
            with open(f"{out_folder_path}/{uid_tmp}.html", 'w', encoding="utf-8") as f:
                f.write(msg_html)
            BACKED_UIDS.append(uid_tmp)
            print("done!")

    # mail_count = 
    print(f"Mail count = {MAIL_COUNT}")
    print(f"Backed up mails count = {BACKED_COUNT}")

    
print("cleaning up..")
UNBACKED_UIDS = [x for x in UIDS if x not in BACKED_UIDS]
json_data = {
        "uids" : UIDS + BACKED_UIDS
    }
js_obj = json.dumps(json_data)
with open("read.json", "w") as backed_mails :
    backed_mails.write(js_obj)

print("closing..")
