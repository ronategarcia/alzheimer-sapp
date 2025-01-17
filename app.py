import tkinter as tk
from tkinter import filedialog, messagebox, Button
import sys

if sys.platform == 'darwin':
    from tkmacosx import Button

from PIL import Image, ImageTk  # Import this if you're using a non-PNG image or want to resize

from brain_wave import run_brain_wave
from eyes_tracking import start_tracking  # Ensure your eyes_tracking.py is correctly set up

app_name = "MindCheck Alzheimer's"  # Change this to your app name


def on_closing(window):
    # Perform any cleanup actions here if necessary
    print("Program is closing...")

    # Destroy the window and exit the program
    window.destroy()
    window.quit()


def open_file_dialog(window, label_image, label):
    filepath = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if filepath:
        start_tracking(window=window, label_image=label_image, label=label, video_path=filepath)
    else:
        messagebox.showwarning("No file selected", "Please select a valid video file.")


def create_eyes_tracking_interface(main_window):
    def start_eyes_tracking():
        start_tracking(window=window, label_image=label_image, label=label, main_window=main_window)

    # Hide the main menu window
    main_window.withdraw()

    # Create a new window for the eyes tracking interface
    window = tk.Toplevel()
    window.minsize(1200, 720)
    window.title("Alzheimer's Eye Tracking")
    # Set the close protocol to call `on_closing` when the "X" button is clicked
    window.protocol("WM_DELETE_WINDOW", lambda: go_back(window, main_window))

    label = tk.Label(window, text="Eyes Tracking Interface", font=("Arial", 24))
    label.pack(pady=100)
    # Create a label_image to display the video frames
    logo_image = Image.open('eyes.png')  # Replace "logo.png" with your logo file path
    logo_image = logo_image.resize((150, 150))  # Resize the image if needed
    logo_photo = ImageTk.PhotoImage(logo_image)

    label_image = tk.Label(window, image=logo_photo)
    label_image.image = logo_photo  # Keep a reference to avoid garbage collection
    label_image.pack(pady=10)

    # Back button to return to the main menu
    back_button = Button(window, text="← Back", command=lambda: go_back(window, main_window),
                            font=("Arial", 12), bg='#4CAF50', relief='raised')
    back_button.place(x=20, y=20)

    # Create buttons to open webcam or video file
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.BOTTOM, pady=40)

    button_webcam = Button(button_frame, text="Use Webcam", command=start_eyes_tracking, width=200, height=30,
                              bg='RED', fg='#ED7D3A', relief='raised')
    button_webcam.pack(side=tk.LEFT, padx=10)

    # button_file = Button(button_frame, text="Open Video File",
    #                         command=lambda: open_file_dialog(window, label_image, label), width=200, height=30)
    # button_file.pack(side=tk.LEFT, padx=10)


def create_brain_wave_interface(main_window):
    def start_brain_wave():
        label.config(text="Setting up EEG stream - This may take up to 10 seconds...")
        label.update()
        button_start.config(state=tk.DISABLED, bg='grey', fg='white', text="Processing...")
        button_start.update()
        run_brain_wave(main_window=main_window, window=window, label=label, label_image=label_image, button=button_start)

    # Hide the main menu window
    main_window.withdraw()
    # Create a new window for the brain wave interface
    window = tk.Toplevel()
    window.minsize(1200, 720)
    window.title("Brain Wave Interface")
    # Set the close protocol to call `on_closing` when the "X" button is clicked
    window.protocol("WM_DELETE_WINDOW", lambda: go_back(window, main_window))

    # Back button to return to the main menu
    back_button = Button(window, text="← Back to Main Menu", command=lambda: go_back(window, main_window),
                            font=("Arial", 12), bg='#4CAF50', relief='raised')
    back_button.place(x=20, y=20)

    label = tk.Label(window, text="Brain Wave Interface", font=("Arial", 24))
    label.pack(pady=100)
    # Create a label_image to display the video frames
    logo_image = Image.open('brain.png')  # Replace "logo.png" with your logo file path
    logo_image = logo_image.resize((150, 150))  # Resize the image if needed
    logo_photo = ImageTk.PhotoImage(logo_image)

    label_image = tk.Label(window, image=logo_photo)
    label_image.image = logo_photo  # Keep a reference to avoid garbage collection
    label_image.pack(pady=10)

    # Create buttons to open webcam or video file
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.BOTTOM, pady=40)

    button_start = Button(button_frame, text="Start", command=start_brain_wave, width=200, height=30,
                             bg='#2196F3', fg='white', relief='raised')
    button_start.pack(side=tk.LEFT, padx=10)


def go_back(current_window, main_window):
    current_window.destroy()  # Close the current window
    main_window.deiconify()  # Show the main menu window again


def main_menu():
    # Create the main menu window
    window = tk.Tk()
    window.minsize(800, 600)
    window.title("Main Menu")
    # Set the close protocol to call `on_closing` when the "X" button is clicked
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    # Add the logo image to the main menu
    try:
        logo_image = Image.open("brainlogo.png")  # Replace "logo.png" with your logo file path
        logo_image = logo_image.resize((150, 150))  # Resize the image if needed
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(window, image=logo_photo)
        logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
        logo_label.pack(pady=10)
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Add the app name
    app_name_label = tk.Label(window, text=app_name, font=("Arial", 28, "bold"))
    app_name_label.pack(pady=10)

    # Create buttons to navigate to the different interfaces
    label = tk.Label(window, text="Select an Option", font=("Arial", 24))
    label.pack(pady=20)

    button_eyes_tracking = Button(window, text="Eyes Tracking Interface",
                                     command=lambda: create_eyes_tracking_interface(window),
                                     width=300, height=40, bg="black", fg='white', relief='raised')
    button_eyes_tracking.pack(pady=20)

    button_brain_wave = Button(window, text="Brain Wave Interface",
                                  command=lambda: create_brain_wave_interface(window),
                                  width=300, height=40, bg='black', fg='white', relief='raised')
    button_brain_wave.pack(pady=20)

    # Run the main loop
    window.mainloop()


if __name__ == "__main__":
    main_menu()
