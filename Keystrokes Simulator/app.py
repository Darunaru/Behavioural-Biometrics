from flask import Flask, render_template, request
import pandas as pd
import json

app = Flask(__name__)

data = []  # List to store collected keystroke data
id_counter = 1  # Counter to assign unique IDs



# Load the existing data from the Excel file, if it exists
try:
    df = pd.read_excel('keystrokes.xlsx')
    data = df.to_dict('records')
    id_counter = df['ID'].max() + 1
    email_ids = {email: entry_id for email, entry_id in zip(df['Email'], df['ID'])}
except FileNotFoundError:
    data = []
    id_counter = 1
    email_ids = {}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get the parameters from the form
    username = request.form.get('username')
    email = request.form.get('email')
    keystrokes_json = request.form.get('keystrokes')

    # Convert the JSON string to a list of keystrokes
    keystrokes = json.loads(keystrokes_json)

    # Calculate key hold time, key flight time, key press/release timings, and key combinations
    hold_times = []
    flight_times = []
    press_release_timings = []
    combinations = []
    for i in range(len(keystrokes)-1):
        hold_time = keystrokes[i+1]['time'] - keystrokes[i]['time']
        hold_times.append(hold_time)

        if keystrokes[i]['action'] == 'press' and keystrokes[i+1]['action'] == 'release':
            flight_time = keystrokes[i+1]['time'] - keystrokes[i]['time']
            flight_times.append(flight_time)
            press_release_timings.append((keystrokes[i]['time'], keystrokes[i+1]['time']))
            combinations.append((keystrokes[i]['key'], keystrokes[i+1]['key']))

    # Check if the email ID already has an assigned ID
    if email in email_ids:
        entry_id = email_ids[email]
    else:
        # Assign a new ID for the email ID
        global id_counter
        entry_id = id_counter
        id_counter += 1
        email_ids[email] = entry_id

    # Create a dictionary with the collected data
    entry_data = {
        'ID': entry_id,
        'Username': username,
        'Email': email,
        'Hold Times': hold_times,
        'Flight Times': flight_times,
        'Press/Release Timings': press_release_timings,
        'Key Combinations': combinations
    }

    # Append the data to the list
    data.append(entry_data)

    # Create a DataFrame with the collected data
    df = pd.DataFrame(data)
    
    # Perform operations on the collected data
    # Calculate total hold times for the current entry
    total_hold_times = sum(hold_times)
    df.loc[df['Email'] == email, 'Total Hold Times'] = total_hold_times

    # Calculate total flight times for the current entry
    total_flight_times = sum(flight_times)
    df.loc[df['Email'] == email, 'Total Flight Times'] = total_flight_times

    # Calculate total key combinations for the current entry
    total_key_combinations = len(combinations)
    df.loc[df['Email'] == email, 'Total Key Combinations'] = total_key_combinations



    # Save the DataFrame to an Excel file
    df.to_excel('keystrokes.xlsx', index=False)

    result = f"Data for Entry ID {entry_id} (Email: {email}) saved successfully!\n"
    result += f"Total Hold Times: {total_hold_times} milliseconds\n"
    result += f"Total Flight Times: {total_flight_times} milliseconds\n"
    result += f"Total Key Combinations: {total_key_combinations}\n"
    result += "Perform additional operations here..."

    return result

if __name__ == '__main__':
    app.run(debug=True)
