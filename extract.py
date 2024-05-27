from bs4 import BeautifulSoup

# Load the saved HTML content
with open('path-to-your-file.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Create BeautifulSoup object to parse the HTML
soup = BeautifulSoup(html_content, 'lxml')

# Extract questions, answers, and explanations
questions = soup.select('.ays_quiz_question')
quiz_data = []

for question in questions:
    # Extract the question text
    question_text = question.get_text(strip=True)
    
    # Find the next sibling elements that contain the answers
    answers_divs = question.find_next_sibling('div', class_='ays-quiz-answers').find_all('div', class_='ays-field ays_list_view_item')
    answers = []
    correct_answers = []

    for answer_div in answers_divs:
        # Extract the answer text from the <label> tag
        answer_label = answer_div.find('label')
        if answer_label:
            answers.append(answer_label.get_text(strip=True))
        
        # Check if the answer is correct by looking at the hidden input value
        correct = answer_div.find('input', {'name': 'ays_answer_correct[]'}).get('value') == '1'
        if correct:
            correct_answers.append(answer_label.get_text(strip=True))

    # Extract the explanation text
    explanation_div = question.find_next_sibling('div', class_='ays_questtion_explanation')
    if explanation_div:
        explanation_parts = []
        for element in explanation_div:
            if element.name == 'p':
                # Extract text from <p> tags and replace newlines with <br>
                explanation_text = element.get_text(separator="<br>", strip=True)
                # Remove "Correct Answer – A, B", "Correct Answers – A, B", or "Answer – A, B" from the explanation
                if explanation_text.startswith("Correct Answer –") or explanation_text.startswith("Correct Answers –") or explanation_text.startswith("Answer –"):
                    explanation_text = explanation_text.split("<br>", 1)[-1].strip()
                explanation_parts.append(explanation_text)
            elif element.name == 'a':
                # Extract URLs and their text
                explanation_parts.append(f'<a href="{element.get("href")}" target="_blank" rel="noopener">{element.get_text(strip=True)}</a>')
            elif isinstance(element, str):
                # Handle plain string elements
                explanation_parts.append(element.strip())
            else:
                # Handle other HTML elements
                explanation_parts.append(element.get_text(strip=True))
        explanation = "<br>".join(explanation_parts)
    else:
        explanation = 'No explanation provided.'

    # Store structured data
    quiz_data.append({
        'question': question_text,
        'answers': answers,
        'correct_answers': correct_answers,
        'explanation': explanation
    })

# Format data for Anki
anki_data = []
for item in quiz_data:
    # Join question and answers for the front of the Anki card
    anki_question = item['question'] + "<br><br>" + "<br>".join(item['answers'])
    
    # Join correct answers and explanation for the back of the Anki card
    correct_answer_label = "Correct Answers:<br>" if len(item['correct_answers']) > 1 else "Correct Answer:<br>"
    anki_answer = correct_answer_label + "<br>".join(item['correct_answers']) + "<br><br>Explanation:<br>" + item['explanation']
    
    # Adjust formatting for the explanation
    anki_answer = anki_answer.replace("<br><br>Explanation:<br>", "<br><br>Explanation:")
    
    anki_data.append([anki_question, anki_answer])

# Save Anki data to a CSV file
import csv

with open('anki_quiz_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';')
    csvwriter.writerows(anki_data)

print("Anki data successfully saved to 'anki_quiz_data.csv'")
