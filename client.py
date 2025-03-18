import xmlrpc.client
import datetime


server = xmlrpc.client.ServerProxy('http://localhost:3000/RPC2')


# Function to add a note
def AddNote():
    try:
        check = 0
        topic = ""
        note = ""
        text = ""
        while check < 3:
            if len(topic.strip()) == 0:
                topic = input("Enter topic: ")
                if len(topic.strip()) != 0:
                    check +=1
                else:
                    print("Topic cannot be empty")
                print()
            if len(note.strip()) == 0:
                note = input("Enter note: ")
                if len(note.strip()) != 0:
                    check +=1
                else:
                    print("Note cannot be empty")
                print()
            if len(text.strip()) == 0:
                text = input("Enter text: ").strip()
                if len(text.strip()) != 0:
                    check +=1
                else:
                    print("Text cannot be empty")
                print()
            
        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        response = server.saveNote(topic, note, text, date)
        print(response)
        print()
    except Exception as e:
        print(f"Error saving note: {e}")
    return
# Function to get notes by topic
def getNote():
    try:
        topic = input("Enter topic or press enter to exit: ")
        print()
        if topic == "":
            return
        notes = server.getnotes(topic)
        if type(notes) == str:
            print(notes)
        else:
            for note in notes:
                print(f"Name: {note[0]} \nText: {note[1]} \nDate:{note[2]} \n")
    except Exception as e:
        print(f"Error getting notes: {e}")
    return
# Function to get Wikipedia information
def wikipediainfo():
    try:
        topic = input ("Enter topic to search on Wikipedia or press enter to exit: ")
        print()
        if topic == "":
            return
        url = server.getwikipedia(topic)
        print(url)
    except Exception as e:
        print(f"Error getting Wikipedia information: {e}")
    print()
    return
# Function to display topics and a check to skip next function if there are no connection to the server
def displayTopics():
    try:
        topics = server.getTopics()
        if type(topics) == str:
            print(topics)
        elif len(topics) == 0:
            print("No topics found")
            
        else:
            print("Your topics: \n")
            for topic in topics:
                print(topic)
        print()
    except Exception as e:
        print(f"Error getting topics: {e}")
        return False
    return True
# Main function while loops until user exits
def main():
    while True:
        print("Menu:")
        print("1. Add a note")
        print("2. Get notes by topic")
        print("3. Get Wikipedia information to a topic")
        print("0. Exit")
        choice = input("Enter choice: ")
        print()
        if choice == '1':
            if displayTopics():
                AddNote()
        elif choice == '2':
            if displayTopics():
                getNote()
        elif choice == '3':
            if displayTopics():
                wikipediainfo()
        elif choice == '0':
            break
        else:
            print("Invalid choice \n")
            
main()