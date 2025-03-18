import xml.etree.ElementTree as ET
import requests
import datetime
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
Database = 'database.xml'

class THreadingSimpleXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


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
        try:
            root = tree.getroot()
            temptopic = None
            for temp in root.findall('topic'):
                if temp.get('name') == topic:
                    temptopic = temp
                    break
            if temptopic is None:
                temptopic = ET.SubElement(root, 'topic')
                temptopic.set('name', topic)
            tempnote = ET.SubElement(temptopic, 'note')
            tempnote.set('name', note)
            ET.SubElement(tempnote, 'text').text = text
            ET.SubElement(tempnote, 'timestamp').text = date
            indent(root)
            tree.write(Database, encoding="utf-8")
            return "Note saved successfully"
        except Exception as e:
            return f"Error saving note: {e}"
    
    server.register_function(saveNote, 'saveNote')
    # Function to get notes by topic
    def getnotes(topic):
        try:
            root = tree.getroot()
            notes = []
            for tempname in root.findall('topic'):
                if tempname.get('name') == topic:
                    break
            if tempname.get('name') != topic:
                return "No notes found"
            for tempnote in tempname.findall('note'):
                notes.append((tempnote.get('name'), tempnote.find('text').text, tempnote.find('timestamp').text))
            return notes
        except Exception as e:
            return f"Error getting notes: {e}"
    
    server.register_function(getnotes, 'getnotes')
    # Function to get all topics
    def getTopics():
        try:
            root = tree.getroot()
            topics = []
            for temp in root.findall('topic'):
                topics.append(temp.get('name'))
            return topics
        except Exception as e:
            return f"Error getting topics: {e}"
        
    server.register_function(getTopics, 'getTopics')
    # Function to get wikipedia information
    def getwikipedia(topic):
        try:
            URL = "https://en.wikipedia.org/w/api.php"
            PARAMS = {
                "action": "opensearch",
                "namespace": "0",
                "search": topic,
                "limit": "1",
                "format": "json"
            }
            response = requests.get(url=URL, params=PARAMS)
            data = response.json()
        
            if data[3]:
                resURL = data[3][0]
            else:
                return "No Wikipedia information found"
            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            #On Wikimedia wikis descriptions are disabled due to performance reasons, so the second array only contains empty strings. See T241437.
            saveNote(topic, resURL, "description is disabled by wikimedia", date)
            return f"Topics wikipedia page {resURL}"
        except Exception as e:
            return f"Error getting wikipedia information: {e}"
    
    server.register_function(getwikipedia, 'getwikipedia')
    
    
    print("Server running on port 3000")
    
    server.serve_forever()