import xml.etree.ElementTree as ET
import requests
import datetime
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
Database = 'database.xml'
# Server that can handle multiple requests at the same time
class THreadingSimpleXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
# Request handler for the server
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Server that can handle multiple requests at the same time
with THreadingSimpleXMLRPCServer(('localhost', 3000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()
    # Initialize the database or creates if one doesn't exist
    try:
        tree = ET.parse(Database)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        root = ET.Element('data')
        tree = ET.ElementTree(root)
        tree.write(Database, encoding="utf-8")

    # This Function is used to indent the xml file for better readability
    #Adds line breaks to xml file
    def indent(elem):
       for subelem in elem:
           indent(subelem)
       if len(elem):
           elem.text = '\n'
           elem.tail = '\n'
       else:
           elem.tail = '\n'
                
    # Function to create a new note/topic and save it to database
    def saveNote(topic, note, text, date):
        try: #Check if input is valid
            if topic.strip() == "" or note.strip() == "" or text.strip() == "":
                return "Topic, Note or Text cannot be empty"
            elif not isinstance(topic, str) or not isinstance(note, str) or not isinstance(text, str):
                return "Topic, Note and Text should be strings"
            try:
                datetime.datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                return "Incorrect date format, should be DD/MM/YYYY HH:MM:SS"
            root = tree.getroot() #Get root of xml file
            temptopic = None
            for temp in root.findall('topic'): #Check if topic already exists
                if temp.get('name') == topic:
                    temptopic = temp
                    break
            if temptopic is None: #If topic doesn't exist, create a new one
                temptopic = ET.SubElement(root, 'topic')
                temptopic.set('name', topic)
            tempnote = ET.SubElement(temptopic, 'note') #Create a new note
            tempnote.set('name', note)
            ET.SubElement(tempnote, 'text').text = text
            ET.SubElement(tempnote, 'timestamp').text = date
            indent(root) #Indent the xml file
            tree.write(Database, encoding="utf-8") #Save the xml file
            return "Note saved successfully"
        except Exception as e:
            return f"Error saving note: {e}"
    
    server.register_function(saveNote, 'saveNote')
    # Function to get notes by topic
    def getnotes(topic):
        try: #Check if input is valid
            if topic.strip() == "":
                return "Topic cannot be empty"
            elif not isinstance(topic, str):
                return "Topic should be a string"
            
            root = tree.getroot() #Get root of xml file
            notes = []
            for tempname in root.findall('topic'): # Check if topic exists
                if tempname.get('name') == topic:
                    break
            if tempname.get('name') != topic: #If topic doesn't exist, return error
                return "No notes found"
            for tempnote in tempname.findall('note'): #Get all notes for the topic
                notes.append((tempnote.get('name'), tempnote.find('text').text, tempnote.find('timestamp').text))
            return notes #Return all notes
        except Exception as e: 
            return f"Error getting notes: {e}"
    
    server.register_function(getnotes, 'getnotes')
    # Function to get all topics
    def getTopics():
        try:
            root = tree.getroot() #Get root of xml file
            topics = []
            for temp in root.findall('topic'): #Get all topics
                topics.append(temp.get('name'))
            return topics #Return all topics
        except Exception as e:
            return f"Error getting topics: {e}"
        
    server.register_function(getTopics, 'getTopics')
    # Function to get wikipedia information
    def getwikipedia(topic):
        try:
            if topic.strip() == "": #Check if input is valid
                return "Topic cannot be empty"
            elif not isinstance(topic, str):
                return "Topic should be a string"
             
            URL = "https://en.wikipedia.org/w/api.php" #URL for wikipedia API
            #Parameters for the API
            PARAMS = { 
                "action": "opensearch", 
                "namespace": "0",
                "search": topic,
                "limit": "1",
                "format": "json"
            }
            response = requests.get(url=URL, params=PARAMS) #Get the response from the API
            data = response.json()
        
            if data[3]: #Check if there is a wikipedia page for the topic
                resURL = data[3][0]
            else:
                return "No Wikipedia information found"
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") #Get current date
            #On Wikimedia wikis descriptions are disabled due to performance reasons, so the second array only contains empty strings. See T241437.
            saveNote(topic, resURL, "description is disabled by wikimedia", date) #Save the wikipedia page to the database
            return f"Topics wikipedia page {resURL}"
        except Exception as e:
            return f"Error getting wikipedia information: {e}"
    
    server.register_function(getwikipedia, 'getwikipedia')
    
    
    print("Server running on port 3000") 
    
    try: #Run the server
        server.serve_forever()
    except KeyboardInterrupt: #Stop the server
        print("Shutting down server...")
        server.server_close()
        print("Server stopped")
        
