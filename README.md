## protoGen - Simple Irc Bot - my first adventure with Python :)

## README - Polski

### Uruchamianie protoGen Irc Bot z linni poleceń:

#### Opis
Uruchamianie bota IRC protoGen z linii poleceń. Wymagane parametry to adres IP do połączenia, adres serwera IRC, port serwera IRC, nazwa bota i kanał na którym ma się pojawić po połączeniu.

#### Instrukcja uruchomienia z linii poleceń
Wpisz następujące polecenie w wierszu poleceń aby uruchomić bota:
```python3 protoGen.py -b ip_z_jakim_mamy_się_łączyć_do_sieci_irc -s adres_serwera_irc -p port_serwera_irc -n nick_bota -c "#knanał_na_który_ma_wejść_bot_po_połączniu"```

Parametry:
- `-h`: wyświetla pomoc
- `-b`: adres IP, z którym bot ma się połączyć do sieci IRC
- `-s`: adres serwera IRC
- `-p`: port serwera IRC
- `-n`: nazwa bota
- `-c`: kanał, na którym bot ma się pojawić po połączeniu

Przykład:
python3 protoGen.py -b 0.0.0.0 -s irc.belwue.de -p 6667 -n protoGen -c "#protoGen"

- Pamiętaj, aby nazwę kanału przekazywać w formie `-c "#kanał"`, a nie `-c #kanał`.
- Aby wyświetlić pomoc, wpisz `python3 protoGen.py -h`.

---

#### Info na temat plików i ich roli

- **config.txt**: Zawiera informacje o konfiguracji bota, takie jak adres serwera, numer portu, nick bota, kanał i adres IP do powiązania. Bot sprawdza, czy plik istnieje podczas uruchamiania, w przeciwnym razie uruchamia kreatora konfiguracji.
- **owner.txt**: Przechowuje listę właścicieli bota. Bot sprawdza, czy plik istnieje podczas uruchamiania, w przeciwnym razie tworzy plik i dodaje pierwszego właściciela.
- **fb.txt**: Przechowuje informacje o listach FB. Bot sprawdza, czy plik istnieje podczas uruchamiania, w przeciwnym razie tworzy pusty plik. Flaga f - autoop, flaga d - kick ban 

#### Zmienne w config.txt

- **server**: Adres serwera IRC.
- **port**: Numer portu serwera IRC.
- **nick**: Nick bota.
- **channel**: Kanał, na którym bot ma działać.
- **bind_ip**: Adres IP do powiązania (opcjonalne).


#### Dostępne komendy:

- **.op nick**: Przyznaje uprawnienia operatora (op) podanemu nickowi.
- **.deop nick**: Odbiera uprawnienia operatora (op) podanemu nickowi.
- **.+own host**: Dodaje nowego właściciela bota z podanym hostem.
- **.-own host**: Usuwa właściciela bota z podanym hostem.
- **.own**: Wyświetla listę właścicieli bota.
- **.k nick powód (opcjonalnie)**: Wyrzuca podany nick z kanału z podanym powodem (opcjonalnie).
- **.mk**: Masowe wyrzucanie użytkowników z kanału (oprócz bota i właściciela bota).
- **.kb nick powód (opcjonalnie)**: Wyrzuca i banuje podany nick z kanału z podanym powodem (opcjonalnie).
- **.+fb #kanał *!ident@host flaga**: Dodaje wpis do listy FB.
- **.-fb #kanał *!ident@host flaga**: Usuwa wpis z listy FB.
- **.fb**: Wyświetla listę FB - Firends/Ban.
- **.join #kanał**: Dołącza do podanego kanału.
- **.part #kanał**: Opuszcza podany kanał.
- **.lc**: Wyświetla listę kanałów, na których bot jest obecny.
- **.jump adres_serwera**: Przeskakuje na inny serwer IRC z podanym adresem.
---
## README - English

### Running protoGen Irc Bot from the command line:

#### Description
Running the IRC bot protoGen from the command line. Required parameters are the IP address to connect, IRC server address, IRC server port, bot name, and the channel on which the bot should appear after connecting.

#### Instructions
Enter the following command in the command line to run the bot:
```python3 protoGen.py -b ip_to_connect_to_irc_network -s irc_server_address -p irc_server_port -n bot_name -c "#channel_to_join_after_connection"```

Parameters:
- `-h`: displays help
- `-b`: IP address to connect to the IRC network
- `-s`: IRC server address
- `-p`: IRC server port
- `-n`: bot name
- `-c`: channel on which the bot should appear after connecting

Example:
python3 protoGen.py -b 0.0.0.0 -s irc.belwue.de -p 6667 -n protoGen -c "#protoGen"


- Remember to pass the channel name in the form of `-c "#channel"`, not `-c channel`.
- To display help, enter `python3 protoGen.py -h`.


#### Bot Configuration and File Information

This bot uses the following txt files for its operation:

1. **config.txt**: Contains configuration details like server address, port number, bot nickname, channel to operate on, and IP address to bind (if applicable).
2. **owner.txt**: Contains a list of bot owners with their hostmasks.
3. **fb.txt**: Stores information about users and their flags (e.g., f for auto-op, d for auto-ban-kick).

At startup, the bot checks if the necessary files exist. If not, it creates the files and runs a configuration wizard for `config.txt` and prompts the user to enter the bot owner's name for `owner.txt`.

The `config.txt` file has the following variables:

- `server`: The server address.
- `port`: The port number to connect to the server.
- `nick`: The bot's nickname.
- `channel`: The channel on which the bot will operate.
- `bind_ip` (optional): The IP address to bind the bot to.

Note: Please make sure to keep these files updated and secure, as they contain sensitive information related to the bot's operation.

#### Commands

- **.op nick**: Grants operator (op) privileges to the given nickname.
- **.deop nick**: Revokes operator (op) privileges from the given nickname.
- **.+own host**: Adds a new bot owner with the given host.
- **.-own host**: Removes a bot owner with the given host.
- **.own**: Displays the list of bot owners.
- **.k nick reason (optional)**: Kicks the given nickname from the channel with the provided reason (optional).
- **.mk**: Mass kicks users from the channel (except the bot and bot owner).
- **.kb nick reason (optional)**: Kicks and bans the given nickname from the channel with the provided reason (optional).
- **.+fb #channel *!ident@host flag**: Adds an entry to the FB list.
- **.-fb #channel *!ident@host flag**: Removes an entry from the FB list.
- **.fb**: Displays the FB list.
- **.join #channel**: Joins the specified channel.
- **.part #channel**: Leaves the specified channel.
- **.lc**: Displays the list of channels the bot is present on.
- **.jump server_address**: Jumps to another IRC server with the provided address.
