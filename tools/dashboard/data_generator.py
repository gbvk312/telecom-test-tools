import random
from datetime import datetime, timedelta
import pandas as pd

TEST_SUITES = ['authentication', 'checkout', 'search', 'user_profile', 'inventory', 'payments']
STATUSES = ['Passed', 'Failed', 'Running', 'Skipped']
LOG_LEVELS = ['INFO', 'WARNING', 'ERROR', 'DEBUG']

class MockTestGenerator:
    def __init__(self, target_num_tests=100):
        self.tests = []
        self.logs = []
        self.target_num_tests = target_num_tests
        self.total_tests_generated = target_num_tests
        self._initialize_data()

    def _initialize_data(self):
        """Generate some initial historical data."""
        now = datetime.now()
        for i in range(self.target_num_tests):
            suite = random.choice(TEST_SUITES)
            status = random.choices(STATUSES, weights=[0.7, 0.15, 0.1, 0.05])[0]
            start_time = now - timedelta(minutes=random.randint(1, 60), seconds=random.randint(0, 59))
            
            # Running tests shouldn't have an end time yet
            if status == 'Running':
                duration = None
                end_time = None
            else:
                duration = random.uniform(0.1, 15.0)
                end_time = start_time + timedelta(seconds=duration)

            test_id = f"test_{suite}_{i:04d}"
            
            self.tests.append({
                'Test ID': test_id,
                'Suite': suite,
                'Status': status,
                'Start Time': start_time,
                'End Time': end_time,
                'Duration (s)': duration
            })

            # Generate logs for this test
            self._generate_logs_for_test(test_id, status, start_time, end_time)

    def _generate_logs_for_test(self, test_id, status, start_time, end_time):
        """Generate fake logs depending on the status."""
        num_logs = random.randint(2, 10)
        current_time = start_time
        
        for _ in range(num_logs):
            level = 'INFO'
            message = f"Executing step for {test_id}"
            
            if random.random() < 0.2:
                level = 'DEBUG'
                message = f"Detailed info for {test_id} at {current_time.strftime('%H:%M:%S')}"
                
            if status == 'Failed' and current_time == end_time:
                # Add an error log at the end if it failed
                pass # Handled after the loop
            
            self.logs.append({
                'Timestamp': current_time,
                'Test ID': test_id,
                'Level': level,
                'Message': message
            })
            
            if end_time:
                 current_time += timedelta(seconds=(end_time - start_time).total_seconds() / num_logs)
            else:
                 current_time += timedelta(seconds=random.uniform(0.5, 2.0))

        if status == 'Failed':
             self.logs.append({
                 'Timestamp': end_time or datetime.now(),
                 'Test ID': test_id,
                 'Level': 'ERROR',
                 'Message': f"Assertion failed: Expected True, got False in {test_id}"
             })

    def tick(self):
        """Simulate time passing: running tests finish, new tests might start."""
        now = datetime.now()
        
        # Finish some running tests
        for test in self.tests:
            if test['Status'] == 'Running':
                if random.random() < 0.3: # 30% chance a running test finishes on this tick
                    test['Status'] = random.choices(['Passed', 'Failed'], weights=[0.8, 0.2])[0]
                    test['End Time'] = now
                    test['Duration (s)'] = (now - test['Start Time']).total_seconds()
                    
                    if test['Status'] == 'Failed':
                        self.logs.append({
                            'Timestamp': now,
                            'Test ID': test['Test ID'],
                            'Level': 'ERROR',
                            'Message': f"Assertion failed dynamically in {test['Test ID']}"
                        })
                    else:
                        self.logs.append({
                            'Timestamp': now,
                            'Test ID': test['Test ID'],
                            'Level': 'INFO',
                            'Message': f"Test completed successfully: {test['Test ID']}"
                        })
                else:
                    if random.random() < 0.2:
                        self.logs.append({
                            'Timestamp': now,
                            'Test ID': test['Test ID'],
                            'Level': 'INFO',
                            'Message': f"Executing intermediate step for {test['Test ID']}"
                        })

        # Occasionally start a new test
        if random.random() < 0.4:
            new_id = self.total_tests_generated
            self.total_tests_generated += 1
            suite = random.choice(TEST_SUITES)
            test_id = f"test_{suite}_{new_id:04d}"
            
            self.tests.append({
                'Test ID': test_id,
                'Suite': suite,
                'Status': 'Running',
                'Start Time': now,
                'End Time': None,
                'Duration (s)': None
            })
            
            self.logs.append({
                'Timestamp': now,
                'Test ID': test_id,
                'Level': 'INFO',
                'Message': f"Starting execution of {test_id}"
            })
            
        # Manage memory length
        if len(self.tests) > 1000:
            self.tests = self.tests[-1000:]
        if len(self.logs) > 5000:
            self.logs = self.logs[-5000:]

    def get_test_df(self):
        return pd.DataFrame(self.tests)

    def get_logs_df(self):
        return pd.DataFrame(self.logs)

# Singleton instance for the Streamlit session state
def get_generator():
    import streamlit as st
    if 'mock_generator' not in st.session_state:
        st.session_state.mock_generator = MockTestGenerator()
    return st.session_state.mock_generator
