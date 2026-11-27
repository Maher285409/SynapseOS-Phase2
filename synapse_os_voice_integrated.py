
"""
SynapseOS FINAL
AI Face Authentication + Hand Gesture OS Control

FACE AUTHENTICATION
    Your face recognized -> System ACTIVE
    Unknown face        -> System LOCKED

GESTURES
    1 finger  -> Move mouse
    PINCH     -> Left click
    2 fingers -> Scroll
    3 fingers -> Volume
    Fist      -> Lock SynapseOS

Q -> Quit
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import math
import time
import os
import threading

from voice_engine import VoiceEngine
from command_engine import CommandEngine

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# =========================================================
# SETTINGS
# =========================================================

FACE_MODEL = "face_model.yml"

FACE_THRESHOLD = 70

# Number of successful face checks needed to unlock
VERIFY_REQUIRED = 3

# Number of failed checks before locking
FAIL_REQUIRED = 3

# Face checking interval
FACE_CHECK_INTERVAL = 1.5

MOUSE_SMOOTH = 6
MARGIN = 20
PINCH_DIST = 36

CLICK_CD = 0.5
LOCK_CD = 1.2
HOLD_TIME = 0.20

SCROLL_SPEED = 15

VOL_SMOOTH = 4

# Voice control
VOICE_ENABLED = True


# =========================================================
# STARTUP
# =========================================================

print()
print("========================================")
print("           SYNAPSEOS FINAL")
print("   Face Authentication + Hand Control")
print("========================================")
print()


# =========================================================
# CHECK FACE MODEL
# =========================================================

if not os.path.exists(FACE_MODEL):

    print("[ERROR] face_model.yml not found.")

    print(
        "Run train_face.py first."
    )

    exit()


# =========================================================
# FACE DETECTOR
# =========================================================

CASCADE_PATH = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)


face_detector = cv2.CascadeClassifier(
    CASCADE_PATH
)


if face_detector.empty():

    print(
        "[ERROR] Face detector could not be loaded."
    )

    exit()


# =========================================================
# FACE RECOGNIZER
# =========================================================

recognizer = (
    cv2.face.LBPHFaceRecognizer_create()
)


recognizer.read(
    FACE_MODEL
)


print(
    "[Face] Recognition model loaded."
)


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)


cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)


cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)


cap.set(
    cv2.CAP_PROP_FPS,
    30
)


if not cap.isOpened():

    print(
        "[ERROR] Camera could not be opened."
    )

    exit()


screenW, screenH = pyautogui.size()


# =========================================================
# MEDIAPIPE HANDS
# =========================================================

mpHands = mp.solutions.hands


hands = mpHands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.85,
    min_tracking_confidence=0.80
)


mpDraw = mp.solutions.drawing_utils


dot_style = mpDraw.DrawingSpec(
    color=(0, 255, 120),
    thickness=2,
    circle_radius=3
)


conn_style = mpDraw.DrawingSpec(
    color=(180, 180, 180),
    thickness=1
)


# =========================================================
# VOLUME
# =========================================================

volumeEnabled = False

volume = None

minVol = 0.0
maxVol = 0.0


try:

    devices = AudioUtilities.GetSpeakers()

    dev = getattr(
        devices,
        "_dev",
        devices
    )

    interface = dev.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )

    volume = cast(
        interface,
        POINTER(IAudioEndpointVolume)
    )

    vr = volume.GetVolumeRange()

    minVol = vr[0]
    maxVol = vr[1]

    volumeEnabled = True

    print(
        "[Volume] Initialized OK."
    )


except Exception as e:

    print(
        "[Volume] Not available:",
        e
    )


# =========================================================
# VOICE CONTROL
# =========================================================

voiceEngine = None
commandEngine = None
voiceThread = None
voiceStopEvent = threading.Event()
appRunning = True


def voice_worker():

    global systemActive, faceVerified
    global faceSuccessCount, faceStatus, appRunning

    print("[Voice] Voice control thread started.")

    while not voiceStopEvent.is_set():

        # Voice commands are available ONLY after face verification.
        if voiceEngine is None or commandEngine is None:
            time.sleep(1)
            continue

        if not (systemActive and faceVerified):
            time.sleep(0.25)
            continue

        try:
            text = voiceEngine.listen()

            # Face may have become locked while we were listening.
            if not (systemActive and faceVerified):
                continue

            if not text:
                continue

            print("[Voice Command]", text)

            running = commandEngine.execute(text)

            if not running:
                # Treat explicit exit/quit as application shutdown.
                if text.strip() in ("exit", "quit") or "close synapseos" in text:
                    appRunning = False
                    voiceStopEvent.set()
                    break

                # Lock commands make SynapseOS inactive.
                systemActive = False
                faceVerified = False
                faceSuccessCount = 0
                faceStatus = "LOCKED"

                print("[SynapseOS] VOICE LOCK")

        except Exception as e:

            print("[Voice] Error:", e)
            time.sleep(1)


# =========================================================
# STATE
# =========================================================

# IMPORTANT:
# SynapseOS starts LOCKED.

systemActive = False

faceVerified = False

faceStatus = "LOCKED"

faceSuccessCount = 0

faceFailCount = 0

lastFaceCheck = 0


prevMouseX = 0
prevMouseY = 0

prevHandY = None

smoothVolPct = 50.0

lastClickTime = 0

lastLockTime = 0

gestureStart = 0

lastGesture = -1

prevTime = time.time()


# =========================================================
# INITIALIZE VOICE SYSTEM
# =========================================================

if VOICE_ENABLED:

    try:
        voiceEngine = VoiceEngine()
        commandEngine = CommandEngine()

        voiceThread = threading.Thread(
            target=voice_worker,
            daemon=True
        )

        voiceThread.start()

        print("[Voice] Control enabled.")
        print("[Voice] Commands activate after face verification.")

    except Exception as e:

        print("[Voice] Disabled:", e)
        voiceEngine = None
        commandEngine = None


# =========================================================
# HELPERS
# =========================================================

def count_fingers(lm):

    tips = [8, 12, 16, 20]

    pips = [6, 10, 14, 18]

    return sum(
        1
        for t, p in zip(tips, pips)
        if lm[t][2] < lm[p][2]
    )


def panel(
    img,
    x,
    y,
    pw,
    ph,
    alpha=0.65
):

    overlay = img.copy()

    cv2.rectangle(
        overlay,
        (x, y),
        (x + pw, y + ph),
        (8, 8, 8),
        -1
    )

    cv2.addWeighted(
        overlay,
        alpha,
        img,
        1 - alpha,
        0,
        img
    )


def lbl(
    img,
    text,
    pos,
    scale=0.52,
    color=(210, 210, 210),
    thick=1
):

    cv2.putText(
        img,
        text,
        pos,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thick,
        cv2.LINE_AA
    )


def vol_color(pct):

    r = int(
        np.interp(
            pct,
            [0, 50, 100],
            [0, 255, 255]
        )
    )

    g = int(
        np.interp(
            pct,
            [0, 50, 100],
            [210, 210, 0]
        )
    )

    return (0, g, r)


# =========================================================
# MAIN LOOP
# =========================================================

print()
print("[SynapseOS] System is LOCKED.")
print("[Face] Look at the camera to unlock.")
print()


while appRunning:

    ok, img = cap.read()


    if not ok:

        continue


    img = cv2.flip(
        img,
        1
    )


    h, w = img.shape[:2]

    now = time.time()


    # =====================================================
    # FACE AUTHENTICATION
    # =====================================================

    if (
        now - lastFaceCheck
        >= FACE_CHECK_INTERVAL
    ):

        lastFaceCheck = now


        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )


        detectedFaces = (
            face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
        )


        if len(detectedFaces) > 0:

            # Use largest face

            x, y, fw, fh = max(
                detectedFaces,
                key=lambda f: f[2] * f[3]
            )


            face = gray[
                y:y+fh,
                x:x+fw
            ]


            face = cv2.resize(
                face,
                (200, 200)
            )


            label, confidence = (
                recognizer.predict(face)
            )


            # =============================================
            # FACE VERIFIED
            # =============================================

            if confidence < FACE_THRESHOLD:

                faceSuccessCount += 1

                faceFailCount = 0

                faceStatus = (
                    f"VERIFYING "
                    f"{faceSuccessCount}/"
                    f"{VERIFY_REQUIRED}"
                )


                # Require several consecutive
                # successful checks.

                if (
                    faceSuccessCount
                    >= VERIFY_REQUIRED
                ):

                    faceVerified = True

                    systemActive = True

                    faceStatus = "VERIFIED"

                    faceFailCount = 0


            # =============================================
            # FACE UNKNOWN
            # =============================================

            else:

                faceFailCount += 1

                faceSuccessCount = 0

                faceStatus = "UNKNOWN"


                if (
                    faceFailCount
                    >= FAIL_REQUIRED
                ):

                    faceVerified = False

                    systemActive = False


            # =============================================
            # FACE BOX
            # =============================================

            boxColor = (
                (0, 255, 0)
                if faceVerified
                else (0, 0, 255)
            )


            cv2.rectangle(
                img,
                (x, y),
                (x + fw, y + fh),
                boxColor,
                2
            )


            cv2.putText(
                img,
                f"FACE: {faceStatus}",
                (x, y - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                boxColor,
                2
            )


            cv2.putText(
                img,
                f"Confidence: {confidence:.1f}",
                (x, y + fh + 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (255, 255, 255),
                1
            )


        else:

            # No face detected

            faceStatus = "NO FACE"

            faceSuccessCount = 0


            # We do NOT immediately lock
            # because the user may simply
            # turn away briefly.


    # =====================================================
    # HAND TRACKING
    # =====================================================

    imgRGB = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )


    res = hands.process(
        imgRGB
    )


    lmList = []

    totalFingers = 0

    mode = "---"


    if res.multi_hand_landmarks:

        handLms = (
            res.multi_hand_landmarks[0]
        )


        for _id, lm in enumerate(
            handLms.landmark
        ):

            lmList.append(
                [
                    _id,
                    int(lm.x * w),
                    int(lm.y * h)
                ]
            )


        mpDraw.draw_landmarks(
            img,
            handLms,
            mpHands.HAND_CONNECTIONS,
            dot_style,
            conn_style
        )


        if len(lmList) == 21:

            thumbTip = lmList[4]

            indexTip = lmList[8]

            midTip = lmList[12]

            wrist = lmList[0]


            x1 = thumbTip[1]

            y1 = thumbTip[2]

            x2 = indexTip[1]

            y2 = indexTip[2]


            pinchLen = math.hypot(
                x2 - x1,
                y2 - y1
            )


            totalFingers = (
                count_fingers(lmList)
            )


            # =============================================
            # GESTURE STABILITY
            # =============================================

            if (
                totalFingers
                != lastGesture
            ):

                gestureStart = now

                lastGesture = totalFingers

                prevHandY = None


            gestureReady = (
                now - gestureStart
            ) >= HOLD_TIME


            # =============================================
            # FIST -> LOCK
            # =============================================

            if (
                totalFingers == 0
                and gestureReady
                and faceVerified
            ):

                if (
                    now - lastLockTime
                    > LOCK_CD
                ):

                    systemActive = False

                    faceVerified = False

                    faceSuccessCount = 0

                    lastLockTime = now

                    prevHandY = None

                    faceStatus = "LOCKED"

                    print(
                        "[SynapseOS] "
                        "MANUAL LOCK"
                    )


            # =============================================
            # GESTURES ONLY WHEN ACTIVE
            # =============================================

            if (
                systemActive
                and faceVerified
            ):


                # =========================================
                # 1 FINGER -> MOUSE
                # =========================================

                if (
                    totalFingers == 1
                    and gestureReady
                ):

                    mode = "MOUSE"


                    rawX = np.interp(
                        x2,
                        [MARGIN, w - MARGIN],
                        [0, screenW]
                    )


                    rawY = np.interp(
                        y2,
                        [MARGIN, h - MARGIN],
                        [0, screenH]
                    )


                    curX = (
                        prevMouseX
                        + (
                            rawX
                            - prevMouseX
                        )
                        / MOUSE_SMOOTH
                    )


                    curY = (
                        prevMouseY
                        + (
                            rawY
                            - prevMouseY
                        )
                        / MOUSE_SMOOTH
                    )


                    pyautogui.moveTo(
                        curX,
                        curY
                    )


                    prevMouseX = curX

                    prevMouseY = curY


                    # Pinch line

                    cv2.line(
                        img,
                        (x1, y1),
                        (x2, y2),
                        (180, 0, 255),
                        2
                    )


                    # =====================================
                    # PINCH -> CLICK
                    # =====================================

                    if pinchLen < PINCH_DIST:

                        mode = (
                            "MOUSE [ CLICK ]"
                        )


                        cv2.circle(
                            img,
                            (
                                (x1 + x2) // 2,
                                (y1 + y2) // 2
                            ),
                            18,
                            (0, 255, 80),
                            cv2.FILLED
                        )


                        if (
                            now - lastClickTime
                            > CLICK_CD
                        ):

                            pyautogui.click()

                            lastClickTime = now


                # =========================================
                # 2 FINGERS -> SCROLL
                # =========================================

                elif (
                    totalFingers == 2
                    and gestureReady
                ):

                    mode = "SCROLL"


                    handY = (
                        indexTip[2]
                        + midTip[2]
                    ) // 2


                    handX = (
                        indexTip[1]
                        + midTip[1]
                    ) // 2


                    if prevHandY is None:

                        prevHandY = handY


                    deltaY = (
                        prevHandY
                        - handY
                    )


                    if abs(deltaY) > 2:

                        pyautogui.scroll(
                            int(
                                np.sign(deltaY)
                                * SCROLL_SPEED
                            )
                        )


                    prevHandY = handY


                # =========================================
                # 3 FINGERS -> VOLUME
                # =========================================

                elif (
                    totalFingers == 3
                    and volumeEnabled
                    and gestureReady
                ):

                    mode = "VOLUME"


                    wristY = wrist[2]


                    rawPct = int(
                        np.interp(
                            wristY,
                            [MARGIN, h - MARGIN],
                            [100, 0]
                        )
                    )


                    rawPct = max(
                        0,
                        min(100, rawPct)
                    )


                    smoothVolPct += (
                        rawPct
                        - smoothVolPct
                    ) / VOL_SMOOTH


                    displayPct = int(
                        smoothVolPct
                    )


                    volDb = float(
                        np.interp(
                            smoothVolPct,
                            [0, 100],
                            [minVol, maxVol]
                        )
                    )


                    volume.SetMasterVolumeLevel(
                        volDb,
                        None
                    )


                    mode = (
                        f"VOLUME "
                        f"{displayPct}%"
                    )


            # =============================================
            # FINGER INDICATORS
            # =============================================

            cv2.circle(
                img,
                (x1, y1),
                8,
                (255, 0, 200),
                cv2.FILLED
            )


            cv2.circle(
                img,
                (x2, y2),
                8,
                (0, 200, 255),
                cv2.FILLED
            )


    else:

        prevHandY = None


    # =====================================================
    # STATUS COLORS
    # =====================================================

    if systemActive:

        statusColor = (0, 220, 0)

        statusText = "ACTIVE"

    else:

        statusColor = (0, 0, 220)

        statusText = "LOCKED"


    # =====================================================
    # BORDER
    # =====================================================

    cv2.rectangle(
        img,
        (MARGIN, MARGIN),
        (
            w - MARGIN,
            h - MARGIN
        ),
        statusColor,
        2
    )


    # =====================================================
    # FPS
    # =====================================================

    currentTime = time.time()


    fps = (
        1
        / (currentTime - prevTime)
        if currentTime - prevTime > 0
        else 0
    )


    prevTime = currentTime


    # =====================================================
    # HUD
    # =====================================================

    panel(
        img,
        8,
        8,
        350,
        250
    )


    lbl(
        img,
        f"STATUS : {statusText}",
        (18, 34),
        0.60,
        statusColor,
        2
    )


    lbl(
        img,
        f"FACE   : {faceStatus}",
        (18, 60),
        0.52,
        (
            (0, 220, 0)
            if faceVerified
            else (0, 0, 255)
        ),
        2
    )


    lbl(
        img,
        f"MODE   : {mode}",
        (18, 84),
        0.52,
        (220, 220, 0)
    )


    lbl(
        img,
        f"FPS    : {int(fps)}",
        (18, 106),
        0.48,
        (150, 150, 150)
    )


    lbl(
        img,
        "GESTURES -----------------------",
        (18, 128),
        0.40,
        (90, 90, 90)
    )


    lbl(
        img,
        " FIST   -> Lock",
        (18, 147),
        0.42,
        (150, 150, 150)
    )


    lbl(
        img,
        " 1 FIN  -> Move Mouse",
        (18, 164),
        0.42,
        (150, 150, 150)
    )


    lbl(
        img,
        " PINCH  -> Left Click",
        (18, 181),
        0.42,
        (150, 150, 150)
    )


    lbl(
        img,
        " 2 FIN  -> Scroll",
        (18, 198),
        0.42,
        (150, 150, 150)
    )


    lbl(
        img,
        " 3 FIN  -> Volume",
        (18, 215),
        0.42,
        (150, 150, 150)
    )


    # =====================================================
    # WINDOW
    # =====================================================

    cv2.imshow(
        "SynapseOS FINAL",
        img
    )


    # =====================================================
    # QUIT
    # =====================================================

    if (
        cv2.waitKey(1) & 0xFF
        == ord("q")
    ):

        break


# =========================================================
# CLEANUP
# =========================================================

voiceStopEvent.set()

if voiceThread is not None and voiceThread.is_alive():
    voiceThread.join(timeout=1.0)

cap.release()


cv2.destroyAllWindows()

hands.close()


print()
print("SynapseOS closed.")
