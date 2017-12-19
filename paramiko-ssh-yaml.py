#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import select
import yaml
import paramiko

def parse_args(): 
    
    parser = argparse.ArgumentParser(description='Python paramiko script that uses a YAML file to run multiple commands\
    on a set of hosts, takes the stdout of those commands & saves the output to a file.')
    parser.add_argument('--config','-c', help='YAML Configuration File', required=True)
    
    args = parser.parse_args()
    
    return args



def main():
    
    args = parse_args()

    with open(args.config, "r") as f:
        try:
            data = yaml.load(f)
        except yaml.YAMLError as e:
            print(e)

    username = data["global_config"]["username"]
    password = data["global_config"]["password"]
    port = data["global_config"]["port"]
    
    for host in data["hosts"]:
    
        hostname = host
        
        print("[>] Attempting Connection to: {}".format(hostname))
        
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(hostname, port=port, username=username, password=password, timeout=5)
            channel = client.get_transport().open_session()

            for command in data["commands"]:
                try:
                    stdin, stdout, stderr = client.exec_command(command)
                    while not stdout.channel.exit_status_ready():
                        if stdout.channel.recv_ready():
                            rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                            if len(rl) > 0: 
                                out = (stdout.channel.recv(1024))
                    with open("{}.log".format(hostname) ,"a") as fd:
                        fd.write("".join(out))
                        fd.close()

                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)
        finally:
            client.close()
            print("[>] Client Session to : {} closed".format(hostname))

if __name__ == '__main__':
    main()
