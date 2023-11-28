import json

def load_database():
    try:
        with open('database.json', 'r') as file:
            database = json.load(file)
        return database
    except FileNotFoundError:
        print("File database.json tidak ditemukan.")
        return None

def save_database(database):
    with open('database.json', 'w') as file:
        json.dump(database, file, indent=2)

def login(username, password, database):
    if username in database and database[username]['password'] == password:
        print("Login berhasil!")
        database[username]['jumlah_login'] += 1
        save_database(database)
    else:
        print("Login gagal. Periksa kembali username dan password.")

def main():
    database = load_database()

    if database is not None:
        while True:
            print("\nSelamat datang! Silakan login.")
            username = input("Username: ")
            password = input("Password: ")

            login(username, password, database)

            ulangi = input("Apakah Anda ingin mencoba login lagi? (ya/tidak): ")
            if ulangi.lower() != 'ya':
                break

if __name__ == "__main__":
    main()
