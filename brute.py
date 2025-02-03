import random
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MCQLearner:
    def __init__(self, url, learning_rate=0.1):
        self.url = url
        self.learning_rate = learning_rate
        self.q_table = {}
        self.driver = webdriver.Chrome()
        self.load_q_table()

    def load_q_table(self):
        try:
            with open('q_table.pkl', 'rb') as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            print("No existing Q-table found. Starting fresh.")

    def save_q_table(self):
        with open('q_table.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)

    def get_question_text(self, question_element):
        return question_element.find_element(By.CSS_SELECTOR, ".question-text").text

    def select_answer(self, question_text, options):
        if question_text not in self.q_table:
            self.q_table[question_text] = [0] * len(options)

        if random.random() < 0.1:  # Exploration
            return random.randint(0, len(options) - 1)
        else:  # Exploitation
            return self.q_table[question_text].index(max(self.q_table[question_text]))

    def update_q_table(self, question_text, selected_option, reward):
        current_q = self.q_table[question_text][selected_option]
        new_q = current_q + self.learning_rate * (reward - current_q)
        self.q_table[question_text][selected_option] = new_q

    def run_test(self):
        self.driver.get(self.url)
        questions = self.driver.find_elements(By.CSS_SELECTOR, ".question")

        for question in questions:
            question_text = self.get_question_text(question)
            options = question.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            selected_option = self.select_answer(question_text, options)
            options[selected_option].click()
            time.sleep(1)

        self.submit_test()
        self.process_results()

    def submit_test(self):
        try:
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_button.click()
            print("Test submitted successfully!")
        except:
            print("Submit button not found or not clickable.")

    def process_results(self):
        # This function should be implemented based on how the results are displayed
        # For this example, we'll assume correct answers are marked with a "correct" class
        questions = self.driver.find_elements(By.CSS_SELECTOR, ".question")
        for question in questions:
            question_text = self.get_question_text(question)
            selected_option = question.find_element(By.CSS_SELECTOR, "input[type='radio']:checked")
            options = question.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            selected_index = options.index(selected_option)

            if "correct" in selected_option.get_attribute("class"):
                reward = 1
            else:
                reward = -1

            self.update_q_table(question_text, selected_index, reward)

    def run_multiple_tests(self, num_tests):
        for i in range(num_tests):
            print(f"Running test {i+1}/{num_tests}")
            self.run_test()
            self.save_q_table()

        self.driver.quit()

# Usage
learner = MCQLearner("https://example.com/mcq-test")
learner.run_multiple_tests(10)  # Run the test 10 times to learn
