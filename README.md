# SynapseOS

### An AI-powered desktop control system

SynapseOS is a team-developed Python project that explores a more
natural way to interact with a computer. It brings together **facial
recognition, hand-gesture control, and voice commands** in one
desktop-control system.

The goal is simple: authenticate a user and let them interact with their
computer using gestures and spoken commands instead of relying only on a
mouse and keyboard.

## Meet the Team

SynapseOS is developed by:

- **Maher**
- **Laiba Maheen**
- **Umaittul Fatima**
- **Saima Kashaf**

Project repository:
[SynapseOS-Phase2](https://github.com/Maher285409/SynapseOS-Phase2)

## What SynapseOS Can Do

### Facial recognition

- Recognizes registered users through a webcam.
- Supports multiple registered users.
- Uses a trained LBPH face-recognition model.
- Checks the user's face before enabling protected controls.

### Hand-gesture control

Use a webcam to interact with the desktop through hand movements.

Gesture Action

---

Fist Lock / unlock action, as configured in the application
Point (one finger) Move the mouse cursor
Pinch Left click
Peace sign (two fingers) Scroll by moving the hand
Three fingers Control system volume

The exact response depends on the gesture logic and settings in the
version being run.

### Voice assistant

After face verification, SynapseOS can listen for spoken commands and
pass recognized speech to its command engine.

**Websites** - Open or close YouTube - Open Google - Open or close
Amazon and Flipkart - Open or close WhatsApp Web - Open or close Gmail,
GitHub, ChatGPT, Instagram, Facebook, Netflix, and Spotify

**System volume** - Increase or decrease volume - Increase or decrease
volume by a specified amount - Mute / unmute

**Search and information** - Search Google - Ask for the current time -
Ask for the date or day

**Windows applications** - Open Notepad - Open Calculator - Open Paint -
Open Task Manager - Open File Explorer

**Other actions** - Take a screenshot - Lock the computer - Ask for help
with supported commands - Exit SynapseOS

The available commands depend on the phrases implemented in
`command_engine.py`. The `close chrome` command closes all Chrome
windows.

## How to Run It

A typical session follows this flow:

1.  Start SynapseOS.
2.  The webcam starts and waits for a registered face.
3.  After successful face verification, the application enables its
    available controls.
4.  Use supported hand gestures to interact with the desktop.
5.  Speak a supported command to open an application or website, search,
    or control a system function.

## Technology Used

Technology Purpose

---

Python Main programming language
OpenCV-contrib Camera processing and LBPH face recognition
MediaPipe Hand-landmark detection
NumPy Image and coordinate processing
PyAutoGUI Mouse, keyboard, scrolling, and screenshot actions
PyCAW Windows audio-volume control
Faster Whisper Speech-to-text
SoundDevice Microphone audio recording
SciPy WAV audio file writing
PyAV Audio decoding used by Faster Whisper
pyttsx3 Text-to-speech responses

## Project Files

The main project files include:

```text
SynapseOS-Phase2/
├── synapse_os_voice_integrated.py
├── command_engine.py
├── voice_engine.py
├── face_register.py
├── train_face.py
├── face_auth.py
├── face_auth_opencv.py
├── face_engine.py
├── synapse_os_multi_user.py
├── synapse_os_final.py
├── main.py
├── launcher.pyw
├── test_command_engine.py
├── test_face_recognition.py
├── test_voice_engine.py
├── flowchart.png
├── README.md
└── .gitignore
```

Local face images, trained face data, downloaded speech models, and
Python virtual environments are kept out of the public repository.

## Setup

### Requirements

- Windows PC
- Python 3.12
- Webcam
- Microphone
- Internet connection for installing dependencies and using online
  services

Some system-control and audio features are Windows-specific.

### 1. Clone the repository

```powershell
git clone https://github.com/Maher285409/SynapseOS-Phase2.git
cd SynapseOS-Phase2
```

### 2. Create and activate a virtual environment

```powershell
py -3.12 -m venv synapse_env
.\synapse_env\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install opencv-contrib-python mediapipe==0.10.21 numpy pyautogui pycaw pyttsx3 scipy faster-whisper sounddevice av==18.1.0
```

The development environment used Python 3.12 and a compatible MediaPipe
0.10.x API with PyAV 18.1.0. If setting up a fresh environment, check
package compatibility if an installation or import error occurs.

### 4. Register users

Run:

```powershell
python face_register.py
```

Follow the prompts to capture face samples for each authorized user.

### 5. Train the face-recognition model

After registering users, run:

```powershell
python train_face.py
```

The training script should generate or update the local face-model
files:

- `face_model.yml`
- `face_labels.json`

These files are intentionally not included in the public repository.
Create them locally by registering users and training the model.

### 6. Launch SynapseOS

Run the integrated application:

```powershell
python synapse_os_voice_integrated.py
```

Wait for face authentication, then try the supported gestures and voice
commands.

## Privacy and Safety

- Keep registered face images and generated face-recognition data
  private.
- Do not upload personal face samples or authentication data to a
  public repository.
- Voice recordings may be temporarily written to the system's
  temporary directory by the voice engine.
- Be aware of the effects of commands that lock the computer, take
  screenshots, or close applications.
- Review the code before using the project on a shared computer.

## Troubleshooting

---

Issue What to check

---

Webcam does not open Check camera permissions and
whether another application is
using it.

Face model is not found Register users and run
`train_face.py`.

A registered user is not recognized Check lighting, camera position,
and the quality of the face
samples.

`cv2.face` is missing Check that `opencv-contrib-python`
is installed in the active
environment.

MediaPipe has no `solutions` Check that the installed MediaPipe
attribute version matches the API used by the
project.

Whisper audio error involving Check PyAV compatibility; the
`metadata_errors` development setup used
`av==18.1.0`.

Microphone does not record Check Windows microphone
permissions and the selected input
device.

PyCAW import fails Install PyCAW in the active virtual
environment; it is
Windows-specific.

---

## Future Improvements

Ideas for future development include:

- Right-click gesture
- Multi-monitor support
- Brightness control
- Custom gesture mapping
- Two-hand gesture support
- More natural conversational voice interaction
- User-configurable voice commands
- A desktop dashboard with status indicators

## Project Repository

**GitHub:** <https://github.com/Maher285409/SynapseOS-Phase2>

---

_Built as a collaborative project by Maher, Laiba Maheen, Umaittul
Fatima, and Saima Kashaf._
