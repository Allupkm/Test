import xmlrpc.client
import threading
import datetime
import time
import sys
import random
import logging
import socket

# Configure basic logging - switched to more minimal format for successful tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)

# Create locks for shared resources
print_lock = threading.Lock()
result_lock = threading.Lock()

# Track test results
results = {
    'TestAddNote': {'success': 0, 'failure': 0},
    'TestGetNote': {'success': 0, 'failure': 0},
    'TestGetWikipedia': {'success': 0, 'failure': 0},
    'TestGetTitles': {'success': 0, 'failure': 0},
    'TestInvalidMethod': {'success': 0, 'failure': 0},
    'TestInvalidParameters': {'success': 0, 'failure': 0}
}

# Create server proxy with timeout parameters
server = xmlrpc.client.ServerProxy('http://localhost:3000/RPC2', 
                                  transport=xmlrpc.client.Transport(use_builtin_types=True),
                                  allow_none=True)

# Function to call server method with retry mechanism
def call_with_retry(method, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Create a fresh connection for each attempt
            proxy = xmlrpc.client.ServerProxy('http://localhost:3000/RPC2', 
                                            transport=xmlrpc.client.Transport(use_builtin_types=True),
                                            allow_none=True)
            method_to_call = getattr(proxy, method)
            return method_to_call(*args)
        except socket.timeout:
            with print_lock:
                logging.warning(f"Attempt {attempt+1}/{max_retries}: Connection timed out, retrying...")
            time.sleep(0.5 * (attempt + 1))  # Exponential backoff
        except (ConnectionRefusedError, OSError) as e:
            with print_lock:
                logging.warning(f"Attempt {attempt+1}/{max_retries}: Connection refused ({e}), retrying...")
            time.sleep(0.5 * (attempt + 1))
        except xmlrpc.client.Fault as e:
            # This is a server-side error, no need to retry
            return f"Server error: {e}"
        except Exception as e:
            with print_lock:
                logging.warning(f"Attempt {attempt+1}/{max_retries}: Error: {e}, retrying...")
            time.sleep(0.5 * (attempt + 1))
    
    return f"Failed after {max_retries} attempts"

# Helper function for logging - succinct for success, detailed for failure
def log_result(test_name, success, message, details=None):
    with print_lock:
        if success:
            # For success, just log minimal info
            logging.info(f"{test_name} - Success")
        else:
            # For failure, log complete details
            logging.error(f"{test_name} - FAILURE: {message}")
            if details:
                logging.error(f"Details: {details}")

def TestAddNote():
    try:
        topic = f"Topic-{random.randint(1, 10)}"
        note = f"Note-{random.randint(1, 100)}"
        text = f"Text-{random.randint(1, 100)}"
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        result = call_with_retry('saveNote', topic, note, text, date)
        
        if "Failed after" not in str(result) and "Error" not in str(result):
            with result_lock:
                results['TestAddNote']['success'] += 1
            log_result('TestAddNote', True, result)
        else:
            with result_lock:
                results['TestAddNote']['failure'] += 1
            log_result('TestAddNote', False, result, f"Topic: {topic}, Note: {note}")
            
    except Exception as e:
        with result_lock:
            results['TestAddNote']['failure'] += 1
        log_result('TestAddNote', False, str(e), f"Topic: {topic}, Note: {note}")
    return

def TestGetNote():
    try:
        topic = f"Topic-{random.randint(1, 10)}"
        result = call_with_retry('getnotes', topic)
        
        if "Failed after" not in str(result) and "Error" not in str(result):
            with result_lock:
                results['TestGetNote']['success'] += 1
            note_count = len(result) if isinstance(result, list) else 0
            log_result('TestGetNote', True, f"{note_count} notes found")
        else:
            with result_lock:
                results['TestGetNote']['failure'] += 1
            log_result('TestGetNote', False, result, f"Topic: {topic}")
            
    except Exception as e:
        with result_lock:
            results['TestGetNote']['failure'] += 1
        log_result('TestGetNote', False, str(e), f"Topic: {topic}")
    return

def TestGetWikipedia():
    try:
        topics = ["Python", "XML-RPC", "Distributed Systems", "Web Services", "Multithreading"]
        topic = random.choice(topics)
        result = call_with_retry('getwikipedia', topic)
        
        if "Failed after" not in str(result) and "No Wikipedia information found" not in str(result):
            with result_lock:
                results['TestGetWikipedia']['success'] += 1
            log_result('TestGetWikipedia', True, topic)
        else:
            with result_lock:
                results['TestGetWikipedia']['failure'] += 1
            log_result('TestGetWikipedia', False, result, f"Topic: {topic}")
            
    except Exception as e:
        with result_lock:
            results['TestGetWikipedia']['failure'] += 1
        log_result('TestGetWikipedia', False, str(e), f"Topic: {topic}")
    return

def TestGetTitles():
    try:
        result = call_with_retry('getTopics')
        
        if "Failed after" not in str(result) and isinstance(result, list):
            with result_lock:
                results['TestGetTitles']['success'] += 1
            log_result('TestGetTitles', True, f"{len(result)} topics")
        else:
            with result_lock:
                results['TestGetTitles']['failure'] += 1
            log_result('TestGetTitles', False, result)
            
    except Exception as e:
        with result_lock:
            results['TestGetTitles']['failure'] += 1
        log_result('TestGetTitles', False, str(e))
    return

def TestInvalidMethod():
    """Test calling a method that doesn't exist - should fail gracefully"""
    try:
        result = call_with_retry('nonExistentMethod')
        
        # For this test, success is when it properly returns an error
        if "Server error" in str(result):
            with result_lock:
                results['TestInvalidMethod']['success'] += 1
            log_result('TestInvalidMethod', True, "Properly failed")
        else:
            with result_lock:
                results['TestInvalidMethod']['failure'] += 1
            log_result('TestInvalidMethod', False, "Did not fail as expected", result)
                
    except Exception as e:
        # This is actually a success for this test type
        with result_lock:
            results['TestInvalidMethod']['success'] += 1
        log_result('TestInvalidMethod', True, "Failed with exception as expected")
    return

def TestInvalidParameters():
    """Test calling methods with invalid parameters - should fail gracefully"""
    try:
        # Pick a test at random from our test cases
        test_type = random.choice([
            'nonexistent_wiki', 
            'nonexistent_topic', 
            'empty_topic', 
            'invalid_params'
        ])
        
        if test_type == 'nonexistent_wiki':
            # Test searching for Wikipedia articles that don't exist
            nonsense_topics = [
                "xyznonexistentwikipageasdfjkl",
                "thispageisnotawikipediapage123456789",
                "completelyrandomimaginarysubject98765"
            ]
            topic = random.choice(nonsense_topics)
            result = call_with_retry('getwikipedia', topic)
            
            # Success if it returns the correct "not found" message
            if "No Wikipedia information found" in str(result):
                with result_lock:
                    results['TestInvalidParameters']['success'] += 1
                log_result('TestInvalidParameters', True, "Nonexistent wiki handled correctly")
            else:
                with result_lock:
                    results['TestInvalidParameters']['failure'] += 1
                log_result('TestInvalidParameters', False, "Wrong response for nonexistent wiki", 
                          f"Topic: {topic}, Result: {result}")
                    
        elif test_type == 'nonexistent_topic':
            # Test getting notes for topics that don't exist
            topic = f"NonexistentTopic-{random.randint(1000, 9999)}"
            result = call_with_retry('getnotes', topic)
            
            # Success if it returns "No notes found"
            if "No notes found" in str(result):
                with result_lock:
                    results['TestInvalidParameters']['success'] += 1
                log_result('TestInvalidParameters', True, "Nonexistent topic handled correctly")
            else:
                with result_lock:
                    results['TestInvalidParameters']['failure'] += 1
                log_result('TestInvalidParameters', False, "Wrong response for nonexistent topic", 
                          f"Topic: {topic}, Result: {result}")
                    
        elif test_type == 'empty_topic':
            # Test with empty topic string
            result = call_with_retry('getnotes', '')
            
            # Success if it returns "No notes found" or any error message about empty topics
            if ("No notes found" in str(result) or 
                "Error" in str(result) or 
                "cannot be empty" in str(result) or
                "Topic cannot be empty" in str(result)):  # Add the exact message
                with result_lock:
                    results['TestInvalidParameters']['success'] += 1
                log_result('TestInvalidParameters', True, "Empty topic handled correctly")
            else:
                with result_lock:
                    results['TestInvalidParameters']['failure'] += 1
                log_result('TestInvalidParameters', False, "Wrong response for empty topic", 
                          f"Result: {result}")
                    
        elif test_type == 'invalid_params':
            # Test various invalid parameter combinations
            invalid_test = random.choice([
                'missing_params',
                'wrong_types',
                'all_empty'
            ])
            
            if invalid_test == 'missing_params':
                # Call saveNote with missing parameters
                result = call_with_retry('saveNote', 'TestTopic')  # Missing note, text, date
            elif invalid_test == 'wrong_types':
                # Call with wrong parameter types
                result = call_with_retry('getnotes', 123)  # Topic should be string
            else:  # all_empty
                # Call with all empty values
                result = call_with_retry('saveNote', '', '', '', '')
                
            # For invalid parameters, success is when it properly detects the problem
            # Add "cannot be empty" as another valid error message
            if ("Error" in str(result) or "Server error" in str(result) or
                "cannot be empty" in str(result)):
                with result_lock:
                    results['TestInvalidParameters']['success'] += 1
                log_result('TestInvalidParameters', True, f"Invalid params ({invalid_test}) handled correctly")
            else:
                with result_lock:
                    results['TestInvalidParameters']['failure'] += 1
                log_result('TestInvalidParameters', False, f"Wrong response for invalid params ({invalid_test})", 
                          f"Result: {result}")
                
    except Exception as e:
        with result_lock:
            results['TestInvalidParameters']['failure'] += 1
        log_result('TestInvalidParameters', False, "Unexpected exception", str(e))
    return

def main(args):
    try:
        Clients = int(args[1])  # Get the first command-line argument
        print(f"Starting test with {Clients} clients")
        
        # Check if server is available before starting tests
        try:
            call_with_retry('getTopics')
            print("Server connection successful. Starting tests...")
        except Exception as e:
            print(f"ERROR: Cannot connect to server. Please ensure the server is running on localhost:3000. Error: {e}")
            sys.exit(1)
            
        # Include all test functions
        test_functions = [
            TestAddNote, 
            TestGetNote, 
            TestGetWikipedia, 
            TestGetTitles,
            TestInvalidMethod,
            TestInvalidParameters
        ]
        
        # Assign weights for test selection
        weights = [0.2, 0.2, 0.1, 0.1, 0.1, 0.3]
        
        threads = []
        for i in range(Clients):
            # Use weighted random selection
            selected_test = random.choices(test_functions, weights=weights, k=1)[0]
            thread = threading.Thread(target=selected_test, name=f"Client-{i+1}-{selected_test.__name__}")
            threads.append(thread)
        
        start_time = time.time()
        for thread in threads:
            thread.start()
            # Add delay between thread starts to prevent overwhelming the server
            time.sleep(random.uniform(0.1, 0.3))
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Print test statistics
        print("\n--- Test Summary ---")
        print(f"Test completed in {total_time:.2f} seconds")
        print(f"Total clients: {Clients}")
        
        for test_name, counts in results.items():
            total = counts['success'] + counts['failure']
            if total > 0:
                success_rate = (counts['success'] / total) * 100
                if 'Invalid' in test_name:  # For invalid tests, note that success means proper error handling
                    print(f"{test_name}: {counts['success']} properly handled errors, {counts['failure']} unexpected successes ({success_rate:.1f}% proper error handling)")
                else:
                    print(f"{test_name}: {counts['success']} successful, {counts['failure']} failed ({success_rate:.1f}% success rate)")
        
    except (IndexError, ValueError):
        print("Usage: python multiclient.py <number_of_clients>")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)  # Pass command-line arguments to main