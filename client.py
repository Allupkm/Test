import xmlrpc.client
import datetime


server = xmlrpc.client.ServerProxy('http://localhost:3000/RPC2') #Connect to server


# Function to add a note
def AddNote():
    try:
        check = 0
        topic = ""
        note = ""
        text = ""
        while check < 3: #Check if input is valid
            if len(topic.strip()) == 0:
                topic = str(input("Enter topic: "))
                if len(topic.strip()) != 0:
                    check +=1
                else:
                    print("Topic cannot be empty")
                print()
            if len(note.strip()) == 0:
                note = str(input("Enter note: "))
                if len(note.strip()) != 0:
                    check +=1
                else:
                    print("Note cannot be empty")
                print()
            if len(text.strip()) == 0:
                text = str(input("Enter text: "))
                if len(text.strip()) != 0:
                    check +=1
                else:
                    print("Text cannot be empty")
                print()
            
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        response = server.saveNote(topic, note, text, date) #Save the note
        print(response)
        print()
    except Exception as e:
        print(f"Error saving note: {e}")
    return
# Function to get notes by topic
def getNote():
    try:
        topic = str(input("Enter topic or press enter to exit: "))
        print()
        if topic == "":
            return
        notes = server.getnotes(topic)
        if type(notes) == str: #Check if there are any notes
            print(notes)
        else:
            for note in notes: #Print all notes
                print(f"Name: {note[0]} \nText: {note[1]} \nDate:{note[2]} \n")
    except Exception as e:
        print(f"Error getting notes: {e}")
    return
# Function to get Wikipedia information
def wikipediainfo():
    try:
        topic = str(input ("Enter topic to search on Wikipedia or press enter to exit: "))
        print()
        if topic == "":
            return
        url = server.getwikipedia(topic) #Get wikipedia information
        print(url)
    except Exception as e:
        print(f"Error getting Wikipedia information: {e}")
    print()
    return
# Function to display topics and a check to skip next function if there are no connection to the server
def displayTopics():
    try:
        topics = server.getTopics() #Get all topics
        if type(topics) == str:#Check if there are any topics
            print(topics) 
        elif len(topics) == 0: #If there are no topics
            print("No topics found")
            return False
        else:
            print("Your topics: \n") #Print all topics
            for topic in topics:
                print(topic)
        print()
        return True
    except Exception as e:
        print(f"Error getting topics: {e}")
# Main function while loops until user exits
def main():
    while True:
        print("Menu:") #Menu
        print("1. Add a note")
        print("2. Get notes by topic")
        print("3. Get Wikipedia information to a topic")
        print("0. Exit")
        choice = input("Enter choice: ")
        print()
        if choice == '1':
            displayTopics() #Check if there are any topics
            AddNote() #Add a note
        elif choice == '2':
            if displayTopics():
                getNote()
        elif choice == '3':
            displayTopics()
            wikipediainfo()
        elif choice == '0':
            break
        else:
            print("Invalid choice \n")
            
main()