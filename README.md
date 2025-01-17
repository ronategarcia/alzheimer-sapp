# MindCheck Alzheimer's

[App Image](brainlogo "MindCheck Alzheimer's")

The Alzheimer’s App is an innovative tool designed to assist in analyzing and visualizing brain wave activity and eye-tracking data, providing valuable insights for early detection and monitoring of Alzheimer’s disease. The app integrates EEG data processing, eye movement analysis, and visual feedback to offer an interactive and user-friendly experience. Utilizing advanced algorithms, it transforms complex data into actionable insights displayed through intuitive visualizations

## Details
The project contains the following files and components for the Alzheimer’s app:

- **`app.py`**: Likely the main script to run the application.
- **`brain.png`**, **`brainlogo.png`**, **`eyes.png`**: Images used in the application interface.
- **`brain_wave.py`**, **`eyes_tracking.py`**, **`get_brain_wave_feedback.py`**, **`show_eeg.py`**: Python scripts handling various functionalities like brain wave analysis, eye tracking, and EEG display.
- **`muse2_eeg_data.txt`**: A data file, possibly containing sample EEG data.
- **`requirements.txt`**: Specifies the Python dependencies required to run the app.
- **`result_page.py`**: Handles result visualization or output display.

### Steps to Use the App
1. **Install Dependencies**:
   - Ensure Python is installed on your system.
   - Use the `requirements.txt` file to install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Run the Application**:
   - Launch the app using the `app.py` file:
     ```bash
     python app.py
     ```

3. **Explore the Features**:
   - **Brain Wave Analysis**: Likely uses `brain_wave.py` and `get_brain_wave_feedback.py` to process and visualize EEG data.
   - **Eye Tracking**: Implements functionality from `eyes_tracking.py` to monitor and analyze eye movements.
   - **Results**: The output is visualized or displayed through `result_page.py`.

4. **Input Data**:
   - The app might require EEG data from `muse2_eeg_data.txt`. Ensure the data file is available in the correct directory.

5. **View Results**:
   - Outputs and visualizations, such as brain wave patterns or eye-tracking results, are shown within the app.

