import os
import socket
import re
import time


class ConfigWizard:
    def __init__(self):
        self.config = {}

    def ask_server(self):
        self.config['server'] = input('Enter server address: ')
        while not self.config['server']:
            self.config['server'] = input('Server address not provided. Enter server address: ')

    def ask_port(self):
        self.config['port'] = input('Enter port number: ')
        while not self.config['port']:
            self.config['port'] = input('Port number not provided. Enter port number: ')

    def ask_nick(self):
        self.config['nick'] = input('Enter bot nickname: ')
        while not self.config['nick']:
            self.config['nick'] = input('Bot nickname not provided. Enter bot nickname: ')

    def ask_channel(self):
        self.config['channel'] = input('Enter the channel for the bot to operate on: ')
        while not self.config['channel']:
            self.config['channel'] = input('Channel not provided. Enter the channel for the bot to operate on: ')

    def ask_bind_ip(self):
        self.config['bind_ip'] = input('Enter IP address to bind: ')

    def run(self):
        print('Welcome to the configuration wizard!')
        self.ask_server()
        self.ask_port()
        self.ask_nick()
        self.ask_channel()
        self.ask_bind_ip()

def extract_nick_from_whois(response):
    for line in response.split('\n'):
        if line.startswith(':') and '311' in line:
            parts = line.split()
            if len(parts) > 3:
                # Use regular expression to extract nick from WHOIS response
                m = re.search(r'^.*is\s+([^\s]+)', line)
                if m:
                    return m.group(1)
    return None

def create_config():
    wizard = ConfigWizard()
    wizard.run()
    with open('config.txt', 'w') as f:
        for key, value in wizard.config.items():
            f.write(f"{key}={value}\n")


def create_owner():
    owner = input('Enter the name of the bot owner: ')
    while not owner:
        owner = input('Bot owner name not provided. Enter the name of the bot owner: ')
    with open('owner.txt', 'w') as f:
        f.write(owner + '\n')


def check_files():
    files_to_check = ['config.txt', 'owner.txt', 'fb.txt']
    for file in files_to_check:
        if not os.path.isfile(file):
            if file == 'config.txt':
                print('config.txt not found.')
                print('Starting config.txt wizard...')
                create_config()
            elif file == 'owner.txt':
                print('owner.txt not found.')
                create_owner()
            elif file == 'fb.txt':
                print('fb.txt not found.')
                with open('fb.txt', 'w') as f:
                    pass


def load_config():
    config = {}
    with open('config.txt', 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key] = value
    return config


def load_owners():
    owners = []
    with open('owner.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                owners.append(r"{}".format(line.replace('*', '.*')))
    return owners


def load_fb():
    fb_data = {}
    with open('fb.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                if line.startswith('#'):
                    channel, host, flag = line.split()
                    if channel not in fb_data:
                        fb_data[channel] = []
                    fb_data[channel].append((host, flag))
    return fb_data


def is_owner(sender, owners):
    return any(re.search(owner, sender) for owner in owners)

def add_fb(fb_data, channel, host, flag, irc):
    if channel not in fb_data:
        fb_data[channel] = []
    entry = (host, flag)
    if entry not in fb_data[channel]:
        fb_data[channel].append(entry)
        with open('fb.txt', 'a') as f:
            f.write(f"{channel} {host} {flag}\n")
        if flag == 'd':
            process_channel(channel, host, irc)
        return True
    else:
        return False


def process_channel(channel, host, irc):
    irc.send(('WHO ' + channel + '\r\n').encode())
    time.sleep(2)
    response = irc.recv(2048).decode()
    lines = response.split('\n')

    for line in lines:
        if line.startswith(':') and '352' in line:
            parts = line.split()
            if len(parts) > 7:
                nick = parts[7]
                ident_host = parts[4] + '@' + parts[5]
                if re.match(re.escape(host), "*!" + ident_host):
                    ban_mask = '*!*' + ident_host
                    irc.send(('MODE ' + channel + ' +b ' + ban_mask + '\r\n').encode())
                    irc.send(('KICK ' + channel + ' ' + nick + ' :Proton Shitlisted!\r\n').encode())
                    break


def remove_fb(fb_data, channel, host, flag, irc):
    if channel in fb_data:
        entry = (host, flag)
        if entry in fb_data[channel]:
            fb_data[channel].remove(entry)
            with open('fb.txt', 'r') as f:
                lines = f.readlines()
            with open('fb.txt', 'w') as f:
                for line in lines:
                    if f"{channel} {host} {flag}" not in line:
                        f.write(line)

            if flag == 'd':
                remove_ban(channel, host, irc)

            return True
    return False


def format_fb(fb_data):
    formatted_fb = ['List of fbs:']
    for channel, hosts in fb_data.items():
        for host, flag in hosts:
            formatted_fb.append(f"{channel} {host} {flag}")
    return formatted_fb


def process_fb(sender, channel, fb_data, irc):
    modified_sender = "*!" + sender.split('!')[1]
    channel = channel.replace(':#', '#')
    for fb_channel, fb_hosts in fb_data.items():
        if fb_channel == channel:
            for host_pattern, flag in fb_hosts:
                if re.match(re.escape(host_pattern), modified_sender):
                    if flag == 'f':
                        irc.send(('MODE ' + channel + ' +o ' + sender.split('!')[0] + '\r\n').encode())
                    elif flag == 'd':
                        ban_mask = '*!*' + sender.split('!')[1]
                        irc.send(('MODE ' + channel + ' +b ' + ban_mask + '\r\n').encode())
                        irc.send(('KICK ' + channel + ' ' + sender.split('!')[0] + ' :Proton Shitlisted!\r\n').encode())
                    break

def remove_ban(channel, host, irc):
    ban_mask = '*!*' + host.split('!')[1]
    irc.send(('MODE ' + channel + ' -b ' + ban_mask + '\r\n').encode())

def jump_server(config, irc, channels, new_server_address):
    new_server = new_server_address.strip()

    # get list of channels before QUIT
    irc.send(('WHOIS ' + config['nick'] + ' ' + config['nick'] +'\r\n').encode())
    time.sleep(2)
    response = irc.recv(2048).decode()
    if "319" in response:
        for line in response.split("\n"):
            if line.startswith(":") and "319" in line:
                channel_list = line.split(":")[2]
                channels = set(channel.strip("@+").replace("@#", "#") for channel in channel_list.split())
                break

    irc.send(('QUIT :Jumping to new server\r\n').encode())
    irc.close()

    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((new_server, int(config['port'])))
    irc.send(('NICK ' + config['nick'] + '\r\n').encode())
    irc.send(('USER ' + config['nick'] + ' 0 * :' + config['nick'] + '\r\n').encode())
    
    # rejoin channels
    for channel in channels:
        irc.send(('JOIN ' + channel + '\r\n').encode())

    return irc

def main():
    # Check if required files exist, create them if they don't
    if not os.path.isfile('config.txt'):
        create_config()
    if not os.path.isfile('owner.txt'):
        create_owner()
    if not os.path.isfile('fb.txt'):
        open('fb.txt', 'a').close()

    config = load_config()
    owners = load_owners()
    fb_data = load_fb()
    channels = set()

    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if 'bind_ip' in config:
        irc.bind((config['bind_ip'], 0))
    irc.connect((config['server'], int(config['port'])))
    irc.send(('NICK ' + config['nick'] + '\r\n').encode())
    irc.send(('USER ' + config['nick'] + ' 0 * :' + config['nick'] + '\r\n').encode())
    irc.send(('JOIN ' + config['channel'] + '\r\n').encode())


    while True:
        message = irc.recv(2048).decode()
        if not message.strip():
            print("Received an empty message.")
            continue
        print(f"Received message: {message}")

        if "Closing Link" in message:
            print("Connection closed by server with message:", message)
            irc.close()
            break

        if message.startswith('PING'):
            irc.send(('PONG ' + message.split()[1] + '\r\n').encode())

        elif 'JOIN' in message:
            sender = message.split('!')[0][1:] + '!' + message.split('!')[1].split()[0]
            channel = message.split('JOIN ')[1].strip()
            process_fb(sender, channel, fb_data, irc)

        elif re.search(r'PRIVMSG', message):
            sender = message.split('!')[0][1:] + '!' + message.split('!')[1].split()[0]
            command = message.split('PRIVMSG')[1].strip().split(' :')[1]

            if is_owner(sender, owners):
                if command.startswith('.op '):
                    nick_to_op = command.split(' ')[1]
                    irc.send(('MODE ' + config['channel'] + ' +o ' + nick_to_op + '\r\n').encode())

                elif command.startswith('.k '):
                    command_split = command.split(' ', 2)
                    nick_to_kick = command_split[1]
                    if len(command_split) > 2:
                        kick_reason = command_split[2]
                    else:
                        kick_reason = 'Proton Has You'

                    # Get the channel from the message
                    channel = message.split()[2]

                    # Check if nick_to_kickban is in the channel
                    irc.send(('WHO ' + channel + '\r\n').encode())
                    time.sleep(0.5)
                    response = irc.recv(2048).decode()
                    lines = response.split('\n')

                    for line in lines:
                        if line.startswith(':') and '352' in line:
                            parts = line.split()
                            if len(parts) > 7:
                                nick = parts[7]
                                if nick == nick_to_kick:
                                    irc.send(('KICK ' + channel + ' ' + nick + ' :' + kick_reason + '\r\n').encode())
                                    break
                elif command == '.mk':
                    # Get the channel from the message
                    channel = message.split()[2]

                    # Get the list of users in the channel
                    irc.send(('WHO ' + channel + '\r\n').encode())
                    time.sleep(0.5)
                    response = irc.recv(2048).decode()
                    lines = response.split('\n')
                    irc.send(('WHOIS').encode())
                    time.sleep(0.5)
                    response = irc.recv(2048).decode()
                    bot_nick = extract_nick_from_whois(response)
                    kick_list = []
                    owner_nick = sender.split('!')[0]

                    for line in lines:
                        if line.startswith(':') and '352' in line:
                            parts = line.split()
                            if len(parts) > 7:
                                nick = parts[7]
                                ident_host = parts[4] + '@' + parts[5]
                                if nick != bot_nick:
                                    if nick != owner_nick:
                                        kick_list.append(nick)

                    # Kick users one by one
                    for nick in kick_list:
                        irc.send(('KICK ' + channel + ' ' + nick + ' :protoGen Mass Kick\r\n').encode())
                        time.sleep(0.2)  # wait half a second between kicks to avoid flooding the server


                # Add new .kb command
                elif command.startswith('.kb '):
                    command_split = command.split(' ', 2)
                    nick_to_kickban = command_split[1]
                    if len(command_split) > 2:
                        kick_reason = command_split[2]
                    else:
                        kick_reason = 'Proton Has You'

                    # Get the channel from the message
                    channel = message.split()[2]

                    # Check if nick_to_kickban is in the channel
                    irc.send(('WHO ' + channel + '\r\n').encode())
                    time.sleep(0.5)
                    response = irc.recv(2048).decode()
                    lines = response.split('\n')

                    for line in lines:
                        if line.startswith(':') and '352' in line:
                            parts = line.split()
                            if len(parts) > 7:
                                nick = parts[7]
                                ident_host = parts[4] + '@' + parts[5]
                                if nick == nick_to_kickban:
                                    if '~' in ident_host:
                                        ban_mask = '*!*@' + parts[5]
                                    else:
                                        ban_mask = '*!*' + ident_host
                                    irc.send(('MODE ' + channel + ' +b ' + ban_mask + '\r\n').encode())
                                    irc.send(('KICK ' + channel + ' ' + nick + ' :' + kick_reason + '\r\n').encode())
                                    break


                elif command.startswith('.deop '):
                    nick_to_deop = command.split(' ')[1]
                    irc.send(('MODE ' + config['channel'] + ' -o ' + nick_to_deop + '\r\n').encode())

                elif command.startswith('.+fb '):
                    command_split = command.split()
                    if "#" in command and "!" in command:                    
                        if len(command_split) == 4:
                            channel, host, flag = command_split[1:]
                            if add_fb(fb_data, channel, host, flag, irc):
                                irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :Added ' + command.split(' ')[1] + ' to fb list.\r\n').encode())
                            else:
                                irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :fb entry already exists.\r\n').encode())
                        else:
                            irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :Not enough arguments for .+fb command. Please provide 3 arguments.\r\n').encode())
                    else:
                        irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :Incorrect data format. Please use the following format: #channel *!ident@host flag\r\n').encode())

                elif command.startswith('.-fb '):
                    command_split = command.split()
                    if "#" in command and "!" in command:
                        if len(command_split) == 4:
                            channel = command_split[1]
                            host = command_split[2]
                            flag = command_split[-1]
                            if remove_fb(fb_data, channel, host, flag, irc):
                                irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :Removed ' + command.split(' ')[1] + ' from fb list.\r\n').encode())
                            else:
                                irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :fb entry not found.\r\n').encode())
                        else:
                            irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :Not enough arguments for .-fb command. Please provide at least 3 arguments.\r\n').encode())
                    else:
                        irc.send(('PRIVMSG ' + sender.split('!')[0] + ' :Incorrect data format. Please use the following format: #channel *!ident@host flag\r\n').encode())

                elif command.startswith('.fb'):
                    fb_list = format_fb(fb_data)
                    for line in fb_list:
                        irc.send(('PRIVMSG ' + sender + ' :' + line + '\r\n').encode())

                elif command.startswith('.join '):
                    channel = command.split(' ')[1]
                    irc.send(('JOIN ' + channel + '\r\n').encode())

                elif command.startswith('.part '):
                    channel = command.split(' ')[1]
                    irc.send(('PART ' + channel + ' :' + 'Arrivederci roma' + '\r\n').encode())

                elif command.startswith('.lc'):
                    irc.send(('WHOIS ' + config['nick'] + ' ' +  config['nick'] +'\r\n').encode())
                    time.sleep(2)
                    response = irc.recv(2048).decode()
                    if "319" in response:
                        channel_list = ""
                        for line in response.split("\n"):
                            if line.startswith(":") and "319" in line:
                                channel_list = line.split(":")[2]
                                break
                        irc.send(('PRIVMSG ' + sender + ' :Channels: ' + channel_list + '\r\n').encode())
                        print(f"Sent channel list to {sender}")
                    else:
                        irc.send(('PRIVMSG ' + sender + ' :Unable to retrieve channel list.\r\n').encode())
                        print(f"Unable to retrieve channel list for {sender}")

                elif command.startswith('.jump '):
                    new_server_address = command.split(' ')[1]
                    irc = jump_server(config, irc, channels, new_server_address)

# Add additional commands here
if __name__ == '__main__':
    main()
