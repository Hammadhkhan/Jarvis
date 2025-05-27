import unittest
from unittest.mock import patch, MagicMock
import datetime

# Assuming backend.command and backend.feature are structured in a way that allows this import
# If 'backend' is a package, this should work.
# We might need to adjust sys.path if running this script directly and Python can't find 'backend'
try:
    from backend.command import takeAllCommands, speak as original_speak
    # We also need to mock eel, which is used by speak and other functions
    # and potentially by takeAllCommands itself.
    # Let's assume eel is globally available or imported in backend.command
except ModuleNotFoundError:
    # This block is for local testing if 'backend' is not in PYTHONPATH
    # For the agent's environment, the try block should ideally succeed.
    import sys
    sys.path.append('..') # Adjust if your test file is elsewhere relative to 'backend'
    from backend.command import takeAllCommands, speak as original_speak


class TestCommands(unittest.TestCase):

    # Patch 'speak' and 'eel.DisplayMessage' and 'eel.receiverText' and 'eel.ShowHood'
    # and 'eel.senderText' in the module where they are called from by takeAllCommands
    # Patch 'takecommand' to avoid actual speech recognition
    @patch('backend.command.takecommand')
    @patch('backend.command.eel.ShowHood')
    @patch('backend.command.eel.senderText')
    @patch('backend.command.eel.receiverText')
    @patch('backend.command.eel.DisplayMessage')
    @patch('backend.command.speak')
    def test_time_command_via_takeAllCommands(self, mock_speak, mock_eel_DisplayMessage, 
                                             mock_eel_receiverText, mock_eel_senderText, 
                                             mock_eel_ShowHood, mock_takecommand):
        """
        Tests the 'time' command when processed by takeAllCommands.
        """
        # Configure mock_takecommand to return a specific query
        # This is not strictly needed if we pass the message directly to takeAllCommands
        # but it's good to have if takeAllCommands were to call takecommand internally
        # in a different way for some commands.
        # mock_takecommand.return_value = "what time is it"

        # Call the function with a message that should trigger the time command
        test_query = "what time is it"
        takeAllCommands(test_query)

        # Assert that speak was called
        self.assertTrue(mock_speak.called, "speak() was not called.")

        # Assert that speak was called at least once (it might be called multiple times)
        self.assertGreaterEqual(mock_speak.call_count, 1, "speak() was not called at least once.")

        # Get all calls to speak
        speak_calls_args = [call_args[0][0] for call_args in mock_speak.call_args_list]
        
        # Check if any of the calls to speak contain the time response
        time_response_found = any(arg.startswith("The current time is ") for arg in speak_calls_args)
        self.assertTrue(time_response_found, 
                        f"No call to speak started with 'The current time is '. Actual calls: {speak_calls_args}")

        if time_response_found:
            # Find the specific call argument
            time_arg = next(arg for arg in speak_calls_args if arg.startswith("The current time is "))
            
            # Optional: More detailed check of the time format
            # Example: "The current time is 01:23 PM"
            try:
                # Extract the time part: "01:23 PM" from "The current time is 01:23 PM"
                time_str_from_speak = time_arg.replace("The current time is ", "")
                # Parse it to ensure it's a valid time
                parsed_time = datetime.datetime.strptime(time_str_from_speak, "%I:%M %p")
                
                # Get current time for comparison (this can be tricky due to execution delay)
                now = datetime.datetime.now()
                expected_time_str_now = now.strftime("%I:%M %p")
                expected_time_one_min_ago = (now - datetime.timedelta(minutes=1)).strftime("%I:%M %p")

                self.assertTrue(
                    time_str_from_speak == expected_time_str_now or \
                    time_str_from_speak == expected_time_one_min_ago,
                    f"The spoken time '{time_str_from_speak}' does not match current time '{expected_time_str_now}' or one minute ago '{expected_time_one_min_ago}'."
                )
            except ValueError:
                self.fail(f"The time string '{time_str_from_speak}' spoken by the command is not in the expected format '%I:%M %p'.")
        
        # Assert that eel.senderText was called with the query
        mock_eel_senderText.assert_called_with(test_query)
        # Assert eel.ShowHood was called
        self.assertTrue(mock_eel_ShowHood.called, "eel.ShowHood() was not called.")


if __name__ == '__main__':
    # This is to ensure that the test can find the backend module if run directly
    # For the agent's environment, this might not be necessary if the CWD is /app
    import sys
    import os
    # Assuming the test file is in backend/test_commands.py
    # and the backend package is in /app/backend
    # We want /app to be in sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # This should be /app if tests are in /app/backend
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Attempt to import again in case the path adjustment was needed
    # This is mostly for robust local execution.
    try:
        from backend.command import takeAllCommands
    except ModuleNotFoundError:
        print("Failed to import backend.command even after path adjustment.")
        print(f"Current sys.path: {sys.path}")
        print(f"Project root calculated: {project_root}")
        # Fallback if running in an unexpected structure or if backend is not a package
        if os.path.basename(project_root) == "backend" and os.path.dirname(project_root) not in sys.path:
             sys.path.insert(0, os.path.dirname(project_root))


    unittest.main()
