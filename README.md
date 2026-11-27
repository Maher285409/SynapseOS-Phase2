# SynapseOS
### AI-Powered Desktop Control Using Face Recognition, Hand Gestures, and Voice Commands

SynapseOS is a Python-based desktop interaction project that combines facial authentication, real-time hand gesture recognition, and voice commands to make computer control more natural and accessible.

The system is designed to recognize registered users, enable gesture-based interaction, and respond to spoken commands after successful face verification.

---

## Features

### 1. Facial Recognition and Authentication
- Recognizes registered users using a trained face-recognition model.
- Supports multiple registered team members.
- Loads the trained model from `face_model.yml`.
- Keeps the system locked until a registered face is recognized.
- Uses repeated face checks to help stabilize authentication.

### 2. Hand Gesture Control
Use a webcam to interact with your computer through hand movements.

| Gesture | Fingers / movement | Action |
|---|---|---|
| Fist | 0 fingers raised | Lock / unlock action, as configured in the application |
| Point | 1 finger raised | Move the mouse cursor |
| Pinch | Thumb and index finger close together | Left click |
| Peace sign | 2 fingers raised | Scroll by moving the hand up or down |
| Three fingers | 3 fingers raised | Control system volume; raise hand to increase volume |

> Gesture behavior depends on the gesture logic and settings in the version of the application you run.

### 3. Voice Assistant
After face verification, SynapseOS can listen for spoken commands and pass recognized text to its command engine.

**Website commands**
- Open or close YouTube
- Open Google
- Open or close Amazon
- Open or close Flipkart
- Open or close WhatsApp Web
- Open or close Gmail, GitHub, ChatGPT, Instagram, Facebook, Netflix, and Spotify

**Volume commands**
- Increase volume
- Increase volume by a specified amount, such as 30
- Decrease volume by a specified amount
- Mute / unmute (toggle)

**Information and search**
- Ask for the current time
- Ask for today's date or day
- Search Google, for example: "Search for Python tutorials"

**Windows application commands**
- Open Notepad
- Open Calculator
- Open Paint
- Open Task Manager
- Open File Explorer

**Other commands**
- Take a screenshot
- Lock the computer
- Ask "Help" or "What can you do?"
- Exit SynapseOS

> Voice command availability depends on the phrases implemented in `command_engine.py`. Website closing is limited to dedicated website windows launched by SynapseOS. The `close chrome` command closes all Chrome windows.

---

## Demo

A typical session works as follows:

1. Start SynapseOS.
2. The webcam starts and the system waits for a registered face.
3. After successful face verification, hand gesture control and voice commands become available.
4. Use supported gestures to move the cursor, click, scroll, and control volume.
5. Speak a supported command to open a website or application, search Google, check the time, or control system functions.

Add your own screenshots or demonstration video here.

---

## Tech Stack

| Technology / library | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV-contrib | Camera processing and LBPH face recognition |
| MediaPipe | Real-time hand landmark detection |
| NumPy | Image and coordinate processing |
| PyAutoGUI | Mouse, keyboard, scrolling, and screenshot actions |
| PyCAW | Windows audio endpoint volume control |
| Faster Whisper | Speech-to-text recognition |
| SoundDevice | Microphone audio recording |
| SciPy | WAV audio file writing |
| PyAV | Audio decoding used by Faster Whisper |
| pyttsx3 | Text-to-speech responses |

---

## Project Structure

The exact files may vary depending on your local project version. The main modules include:

```text
SynapseOS/
├── synapse_os_voice_integrated.py   # Integrated application entry point
├── command_engine.py                # Spoken command handling
├── voice_engine.py                  # Audio recording and speech recognition
├── face_register.py                 # Register face samples
├── train_face.py                    # Train the multi-user face model
├── face_model.yml                   # Trained face-recognition model
├── face_labels.json                 # Face label-to-user mapping
├── faces/                           # Registered face image folders
│   ├── Fatima/
│   ├── Laiba/
│   ├── Maher1/
│   └── Saima/
├── synapse_env/                     # Python virtual environment (local)
└── README.md
```

Do not commit your virtual environment, private face images, or other personal data to a public repository.

---

## Requirements

- Windows PC
- Python 3.12 (the development environment used for the current setup)
- Working webcam
- Working microphone
- Internet connection for installing packages and opening online services

The project uses Windows-specific audio and system-control functionality, including PyCAW and Windows workstation locking.

---

## Installation and Setup

### 1. Clone the repository

Replace `YOUR_USERNAME` with your GitHub username and use the actual repository URL.

```bash
git clone https://github.com/YOUR_USERNAME/SynapseOS.git
cd SynapseOS
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -3.12 -m venv synapse_env
.\synapse_env\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the packages used by the current implementation:

```powershell
python -m pip install --upgrade pip
python -m pip install opencv-contrib-python mediapipe==0.10.21 numpy pyautogui pycaw pyttsx3 scipy faster-whisper sounddevice av==18.1.0
```

The project was tested with a compatible MediaPipe 0.10.x API and PyAV 18.1.0 in the development environment. Package compatibility can change; if you prepare a fresh environment, verify the versions together.

### 4. Register users

Run the face-registration script:

```powershell
python face_register.py
```

Follow its prompts to create a face folder and capture face samples for each authorized user.

### 5. Train the face-recognition model

After registering the users, run:

```powershell
python train_face.py
```

The training script should generate or update:

- `face_model.yml`
- `face_labels.json`

Make sure the model and label file are present before launching the integrated application.

### 6. Run SynapseOS

```powershell
python synapse_os_voice_integrated.py
```

Look at the webcam and wait for face authentication. Once authenticated, test the supported gestures and voice commands.

---

## Configuration

Gesture sensitivity, smoothing, face-authentication thresholds, and recording duration are controlled by values in the relevant Python modules.

Examples from the hand-gesture controller version:

```python
MOUSE_SMOOTH = 6
SCROLL_SPEED = 15
PINCH_DIST = 36
VOL_SMOOTH = 4
```

These values are examples from the gesture-controller configuration. Your integrated application may use different variable names or settings. Check the active script before changing them.

---

## How It Works

### Face authentication
1. OpenCV captures frames from the webcam.
2. The face-recognition module detects and processes a face.
3. The trained LBPH model predicts the registered user's label.
4. SynapseOS checks the prediction against its authentication threshold.
5. After successful verification, the application enables its protected controls.

### Hand gesture recognition
1. MediaPipe detects 21 hand landmarks.
2. The application checks finger positions and hand movement.
3. The detected gesture is mapped to a supported action.
4. PyAutoGUI or the Windows audio interface performs the corresponding desktop action.

### Voice recognition
1. SoundDevice records microphone audio.
2. SciPy writes the recording to a WAV file.
3. Faster Whisper transcribes the audio.
4. The recognized text is passed to `command_engine.py`.
5. The command engine matches supported phrases and performs the requested action.
6. pyttsx3 can provide spoken responses when available.

---

## Privacy and Safety

- Face images are used by the local face-registration and recognition workflow.
- Keep registered face images and generated face data private.
- Do not publish personal face samples or authentication data in a public repository.
- Voice recordings are temporarily written to the system temporary directory by the current voice engine.
- Be careful when using commands that lock the computer, take screenshots, or close applications.
- Review the code before using the project on a shared or production computer.

---

## Troubleshooting

| Problem | What to check |
|---|---|
| Webcam does not open | Check camera permissions and whether another application is using it |
| Face model not found | Confirm `face_model.yml` exists and run the training script |
| A registered user is not recognized | Check lighting, camera position, and face samples; retrain if needed |
| `cv2.face` is missing | Confirm `opencv-contrib-python` is installed in the active environment |
| MediaPipe has no `solutions` attribute | Check that the installed MediaPipe version matches the API used by the application |
| Whisper audio error involving `metadata_errors` | Check PyAV compatibility; the tested setup used `av==18.1.0` |
| Microphone does not record | Check Windows microphone permissions and the selected input device |
| PyCAW import fails | Install PyCAW in the active virtual environment; it is Windows-specific |

---

## Future Enhancements

- Right-click gesture
- Multi-monitor support
- Brightness control
- Custom gesture mapping
- Two-hand gesture support
- More natural conversational voice interaction
- User-configurable voice commands
- Improved desktop dashboard and status indicators

---

## Contributors

Add the names and GitHub profiles of the project contributors here.

- **Your Name** — Project development
- **Team Member 2**
- **Team Member 3**
- **Team Member 4**

---

## License

Choose and add a license before publishing this repository. Until a license is added, do not assume others have permission to reuse or distribute the project.
