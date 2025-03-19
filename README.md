# Assignment 2
This repository contains all of the files for Assignment 2. The assignment involves implementing a client-server model using XML-RPC for remote procedure calls. Below is an overview of the files included and their functionality. However multiclient.py is not part of the assigment and should not be taken into account when evaluating the assignment.

## 1. <code> client.py </code>
This script acts like the client-side application, interacting with the server using XML-RPC. It allows users to send request to server to add note, get topics, get wikipedia info and display topics. This is extremely simplefied and runs a loop which is shown in the console. **This is part of the assignment**
## 2. <code> server.py </code>
The server-side script that hosts the XML-RPC server. It handles client requests, processes data, and manages interactions with the database. **This is part of the assignment**
## 3. <code> database.xml </code>
This file serves as a database for storing notes. It contains structured example entries demonstrating how data is stored and managed within the system. **This is part of the assignment**
## 4. <code> multiclient.py </code>
This script server to test server and database by simulating multiple concurrent client connections. It tests different server by creating different calls and checking if the response is correct. In addition, it checkes error handling and invalid calls. **This is not part of the assignment and should be left out of evaluation**
