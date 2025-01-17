import queue
import threading
import tkinter as tk

from PIL import Image, ImageTk  # Import this if you're using a non-PNG image or want to resize

from get_brain_wave_feedback import create_run

# Create a global queue for communication between the thread and the main UI
feedback_queue = queue.Queue()


def go_back(current_window, main_window):
    current_window.destroy()  # Close the current window
    main_window.deiconify()  # Show the main menu window again


def show_result_eyes_tracking(main_window, current_window, text, title, img_path='logo.png'):
    # Create a new window for the brain wave interface
    current_window.destroy()
    window = tk.Toplevel()
    window.minsize(1200, 720)
    window.title(title)
    window.protocol("WM_DELETE_WINDOW", lambda: go_back(window, main_window))
    # Back button to return to the main menu
    back_button = tk.Button(window, text="← Back to Main Menu", command=lambda: go_back(window, main_window),
                            font=("Arial", 12), bg='#4CAF50', relief='raised')
    back_button.place(x=20, y=20)
    logo_path = img_path
    print(logo_path)
    logo_image = Image.open(logo_path)  # Replace "logo.png" with your logo file path
    logo_image = logo_image.resize((150, 150))  # Resize the image if needed
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(window, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=10)

    label = tk.Label(window, text=text, font=("Arial", 24))
    label.pack(pady=100)


def show_result_brain_wave(main_window, current_window, file_path):
    def fetch_feedback():
        try:
            # Assume create_run is the function that analyzes the EEG data and returns the response
            response = create_run(file_path)
            print(response)

            # Place the response into the queue
            feedback_queue.put(response)
        except RuntimeError:
            print("The main loop has ended or the window was destroyed.")

    def process_queue():
        # Check if there is something in the queue
        try:
            response = feedback_queue.get_nowait()
            update_ui(response)
        except queue.Empty:
            # If the queue is empty, schedule to check again
            window.after(100, process_queue)  # Check every 100ms

    def update_ui(response):
        # Check if the window still exists
        if window.winfo_exists():
            label.config(text="AAlzheimer\'s Brain Wave - EEG", font=("Arial", 24))

            # Create a Text widget
            text_widget = tk.Text(window, wrap='word', font=("Arial", 20))
            text_widget.pack(pady=100, padx=100)
            text_widget.insert(tk.END, response)
            # Make the Text widget read-only
            text_widget.config(state='disabled')

            # Create a vertical scrollbar and link it to the Text widget
            scrollbar = tk.Scrollbar(window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill='y')
            text_widget.config(yscrollcommand=scrollbar.set)

    # Start the feedback-fetching thread
    t1 = threading.Thread(target=fetch_feedback)
    t1.start()

    # Create a new window for the brain wave interface
    title = "Alzheimer's Brain Wave Data - EEG"
    text = 'Analyzing the EEG data...'
    img_path = 'brain.png'
    current_window.destroy()
    window = tk.Toplevel()
    window.minsize(1200, 720)
    window.title(title)

    # Back button to return to the main menu
    back_button = tk.Button(window, text="← Back to Main Menu", command=lambda: go_back(window, main_window),
                            font=("Arial", 12), bg='#4CAF50', relief='raised')
    back_button.place(x=20, y=20)

    # Display the logo
    logo_image = Image.open(img_path)
    logo_image = logo_image.resize((150, 150))
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(window, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=10)

    # Label displaying "Analyzing the EEG data..."
    label = tk.Label(window, text=text, font=("Arial", 24))
    label.pack(pady=100)

    # Start processing the queue in the main thread
    window.after(100, process_queue)  # Check the queue every 100ms
