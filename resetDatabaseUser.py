import json

# Menyimpan data yang baru ke dalam database
def save_database(database):
    with open('./Json/database.json', 'w') as file:
        json.dump(database, file, indent=2)

# Membuka file json berdasarkan opsi yang diinginkan
def openJson(opsi):
        pathFile = "./Json/database.json" if opsi == "database" else "./Json/server.json"
        try:
            with open(pathFile, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File database.json tidak ditemukan.")

def main():
    database = openJson("database")

    for username in database.items():
        database[username[0]]['isLogin'] = "false"
        database[username[0]]['jumlah_download'] = 0
        database[username[0]]['jumlah_upload'] = 0

    save_database(database)
    
main()