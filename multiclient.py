import xmlrpc.client
import threading
import datetime
import time
import sys

server = xmlrpc.client.ServerProxy('http://localhost:3000/RPC2')

def TestAddNote():
    try:
        None
    except Exception as e:
        print(f"Error saving note: {e}")
    return

def TestGetNote():
    try:
        None
    except Exception as e:
        print(f"Error getting notes: {e}")
    return

def TestGetWikipedia():
    try:
        None
    except Exception as e:
        print(f"Error saving note: {e}")
    return

def TestGetTitles():
    try:
        None
    except Exception as e:
        print(f"Error getting notes: {e}")
    return

def main(args):
    try:
        Clients = int(args[1])  # Get the first command-line argument
        print(Clients)
    except (IndexError, ValueError):
        print("Usage: python multiclient.py <number_of_clients>")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)  # Pass command-line arguments to main