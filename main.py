
"""
SynapseOS
AI Hand Gesture OS Control

GESTURES
    0 fingers -> Lock system
    1 finger  -> Move mouse
    PINCH     -> Left click
    2 fingers -> Scroll
    3 fingers -> Volume

Q -> Quit
"""

import math
import time

import cv2
import mediapipe as mp
import numpy as np
import pyautogui

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# =========================================================
# SETTINGS
# =========================================================

MOUSE_SMOOTH = 6
MARGIN = 20
PINCH_DIST = 36

CLICK_CD = 0.5
LOCK_CD = 1.2
HOLD_TIME = 0.20

SCROLL_SPEED = 15
VOL_SMOOTH = 4


# =========================================================
# PYAutoGUI
# =========================================================

pyautogui.FAILSAFE = False


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():

    print("ERROR: Could not open camera.")
    exit()

screenW, screenH = pyautogui.size()


# =========================================================
# STATE
# =========================================================

prevMouseX, prevMouseY = 0, 0
prevHandY = None

smoothVolPct = 50.0

lastClickTime = 0
lastLockTime = 0

gestureStart = 0
lastGesture = -1

# System starts ACTIVE for this test.
systemActive = True

prevTime = time.time()


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

volErrorMsg = ""

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
        "[Volume] Initialized OK - range:",
        minVol,
        "to",
        maxVol,
        "dB"
    )

except Exception as e:

    volErrorMsg = str(e)[:55]

    print(
        f"[Volume] Not available: {e}"
    )


# =========================================================
# HELPERS
# =========================================================

def count_fingers(lm):

    """
    Count raised fingers:
    index, middle, ring and pinky.
    Thumb excluded.
    """

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

    ov = img.copy()

    cv2.rectangle(
        ov,
        (x, y),
        (x + pw, y + ph),
        (8, 8, 8),
        -1
    )

    cv2.addWeighted(
        ov,
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

print("\n========================================")
print("             SYNAPSEOS")
print("       Hand Gesture Control")
print("========================================")
print("System: ACTIVE")
print("Press Q to quit.\n")


while True:

    ok, img = cap.read()

    if not ok:
        continue

    img = cv2.flip(img, 1)

    h, w = img.shape[:2]

    now = time.time()


    # =====================================================
    # MEDIAPIPE
    # =====================================================

    imgRGB = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    res = hands.process(imgRGB)


    lmList = []
    totalFingers = 0
    mode = "---"


    # =====================================================
    # HAND DETECTION
    # =====================================================

    if res.multi_hand_landmarks:

        handLms = res.multi_hand_landmarks[0]

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


            totalFingers = count_fingers(
                lmList
            )


            # =============================================
            # GESTURE STABILITY
            # =============================================

            if totalFingers != lastGesture:

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
            ):

                if (
                    now - lastLockTime
                    > LOCK_CD
                ):

                    systemActive = False

                    lastLockTime = now

                    prevHandY = None

                    print(
                        "[SynapseOS] SYSTEM LOCKED"
                    )


            # =============================================
            # ONLY ALLOW CONTROLS WHEN ACTIVE
            # =============================================

            if systemActive:


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


                    # Pinch visualization

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

                        mid = (
                            (x1 + x2) // 2,
                            (y1 + y2) // 2
                        )


                        cv2.circle(
                            img,
                            mid,
                            18,
                            (0, 255, 80),
                            cv2.FILLED
                        )


                        cv2.circle(
                            img,
                            mid,
                            18,
                            (255, 255, 255),
                            2
                        )


                        mode = "MOUSE [ CLICK ]"


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


                    sc = (
                        0,
                        220,
                        255
                    )


                    cv2.circle(
                        img,
                        (
                            indexTip[1],
                            indexTip[2]
                        ),
                        11,
                        sc,
                        cv2.FILLED
                    )


                    cv2.circle(
                        img,
                        (
                            midTip[1],
                            midTip[2]
                        ),
                        11,
                        sc,
                        cv2.FILLED
                    )


                    arrow_end = (
                        handX,
                        handY - 45
                        if deltaY > 0
                        else handY + 45
                    )


                    cv2.arrowedLine(
                        img,
                        (handX, handY),
                        arrow_end,
                        sc,
                        3,
                        tipLength=0.4
                    )


                # =========================================
                # 3 FINGERS -> VOLUME
                # =========================================

                elif (
                    totalFingers == 3
                    and volumeEnabled
                    and gestureReady
                ):

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
                        f"VOLUME {displayPct}%"
                    )


                    vc = vol_color(
                        displayPct
                    )


                    cv2.line(
                        img,
                        (
                            MARGIN,
                            wristY
                        ),
                        (
                            w - MARGIN,
                            wristY
                        ),
                        vc,
                        2
                    )


                    cv2.circle(
                        img,
                        (
                            wrist[1],
                            wristY
                        ),
                        16,
                        vc,
                        cv2.FILLED
                    )


                    cv2.circle(
                        img,
                        (
                            wrist[1],
                            wristY
                        ),
                        16,
                        (255, 255, 255),
                        2
                    )


                    # Volume bar

                    bar_x = w // 2 - 20
                    bar_y = 80

                    bar_w = 40
                    bar_h = h - 160


                    filled_h = int(
                        bar_h
                        * displayPct
                        / 100
                    )


                    fill_y = (
                        bar_y
                        + bar_h
                        - filled_h
                    )


                    cv2.rectangle(
                        img,
                        (
                            bar_x,
                            bar_y
                        ),
                        (
                            bar_x + bar_w,
                            bar_y + bar_h
                        ),
                        (30, 30, 30),
                        -1
                    )


                    cv2.rectangle(
                        img,
                        (
                            bar_x,
                            fill_y
                        ),
                        (
                            bar_x + bar_w,
                            bar_y + bar_h
                        ),
                        vc,
                        cv2.FILLED
                    )


                    cv2.rectangle(
                        img,
                        (
                            bar_x,
                            bar_y
                        ),
                        (
                            bar_x + bar_w,
                            bar_y + bar_h
                        ),
                        (200, 200, 200),
                        2
                    )


                    big_lbl = (
                        f"{displayPct}%"
                    )


                    fs = 2.2
                    thick = 4


                    (tw, th), _ = (
                        cv2.getTextSize(
                            big_lbl,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            fs,
                            thick
                        )
                    )


                    tx = (
                        w - tw
                    ) // 2


                    ty = (
                        bar_y
                        + bar_h
                        + th
                        + 12
                    )


                    cv2.putText(
                        img,
                        big_lbl,
                        (
                            tx + 2,
                            ty + 2
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fs,
                        (0, 0, 0),
                        thick + 2,
                        cv2.LINE_AA
                    )


                    cv2.putText(
                        img,
                        big_lbl,
                        (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        fs,
                        (255, 255, 255),
                        thick,
                        cv2.LINE_AA
                    )


                    lbl(
                        img,
                        "RAISE = LOUDER",
                        (
                            bar_x - 90,
                            bar_y - 10
                        ),
                        0.45,
                        vc
                    )


                    lbl(
                        img,
                        "LOWER = QUIETER",
                        (
                            bar_x - 90,
                            bar_y + bar_h + 14
                        ),
                        0.45,
                        vc
                    )


                elif (
                    totalFingers == 3
                    and not volumeEnabled
                ):

                    mode = "VOLUME N/A"


                elif totalFingers not in (
                    0,
                    1,
                    2,
                    3
                ):

                    mode = "IDLE"


            # =============================================
            # FINGER DOTS
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
    # ACTIVE ZONE BORDER
    # =====================================================

    border_col = (
        (0, 210, 0)
        if systemActive
        else (0, 0, 210)
    )


    cv2.rectangle(
        img,
        (MARGIN, MARGIN),
        (
            w - MARGIN,
            h - MARGIN
        ),
        border_col,
        1
    )


    # =====================================================
    # FPS
    # =====================================================

    currTime = time.time()


    fps = (
        1 / (currTime - prevTime)
        if currTime - prevTime > 0
        else 0
    )


    prevTime = currTime


    # =====================================================
    # HUD PANEL
    # =====================================================

    panel(
        img,
        8,
        8,
        330,
        245
    )


    # =====================================================
    # SYSTEM STATUS
    # =====================================================

    sc = (
        (0, 220, 0)
        if systemActive
        else (60, 60, 220)
    )


    ss = (
        "ACTIVE"
        if systemActive
        else "LOCKED"
    )


    lbl(
        img,
        f"STATUS : {ss}",
        (18, 34),
        0.60,
        sc,
        thick=2
    )


    lbl(
        img,
        f"MODE   : {mode}",
        (18, 58),
        0.55,
        (220, 220, 0)
    )


    lbl(
        img,
        f"FPS    : {int(fps)}",
        (18, 80),
        0.50,
        (140, 140, 140)
    )


    lbl(
        img,
        "GESTURES -----------------------",
        (18, 103),
        0.40,
        (85, 85, 85)
    )


    lbl(
        img,
        " FIST   ->  Lock",
        (18, 121),
        0.42,
        (135, 135, 135)
    )


    lbl(
        img,
        " 1 FIN  ->  Move Mouse",
        (18, 137),
        0.42,
        (135, 135, 135)
    )


    lbl(
        img,
        " PINCH  ->  Left Click",
        (18, 153),
        0.42,
        (135, 135, 135)
    )


    lbl(
        img,
        " 2 FIN  ->  Scroll",
        (18, 169),
        0.42,
        (135, 135, 135)
    )


    lbl(
        img,
        " 3 FIN  ->  Volume",
        (18, 185),
        0.42,
        (135, 135, 135)
    )


    lbl(
        img,
        " Q key  ->  Quit",
        (18, 201),
        0.42,
        (135, 135, 135)
    )


    # =====================================================
    # CAMERA WINDOW
    # =====================================================

    cv2.imshow(
        "SynapseOS",
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

cap.release()

cv2.destroyAllWindows()

hands.close()

print("\nSynapseOS closed.")
