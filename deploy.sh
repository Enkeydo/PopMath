#!/bin/bash

# --- CONFIGURATION ---
WIN_PATH="/mnt/d/texso/Documents/PyPractice/drpeppercalc"
WSL_PATH="$HOME/DrPepperCalc"
APP_NAME="popmath"
RECIPIENTS="Habitualbreaker@google.com,Texsoroban@gmail.com"

echo "-----------------------------------------------"
echo "  DR PEPPER CALC: DEPLOYMENT BRIDGE v1.2       "
echo "-----------------------------------------------"

# 1. SYNC WINDOWS TO WSL
echo "[1/6] Syncing main.py from Windows..."
cp "$WIN_PATH/main.py" "$WSL_PATH/main.py"

# 2. VERSION CHECK
echo "[2/6] Checking version in main.py..."
EXTRACTED_VER=$(grep "__version__ =" "$WSL_PATH/main.py" | cut -d '"' -f 2)
echo "Detected Version: $EXTRACTED_VER"
echo "-----------------------------------------------"

# 3. MANUAL TRIGGER FOR BUILD
read -p ">>> Start Buildozer? (y/n): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo "[3/6] Starting Build (Logging to final_build.log)..."
    buildozer -v android debug 2>&1 | tee "$WSL_PATH/final_build.log"
else
    echo "Build cancelled. Exiting."
    exit 0
fi

# 4. RENAME THE APK IN THE LINUX BIN FOLDER
echo "[4/6] Renaming APK in Linux bin/ folder..."
NEWEST_APK_PATH=$(ls -t "$WSL_PATH/bin/"*.apk 2>/dev/null | head -1)

if [ -z "$NEWEST_APK_PATH" ]; then
    echo "ERROR: No APK found. Check final_build.log."
    exit 1
fi

FINAL_NAME="${APP_NAME}-${EXTRACTED_VER}.apk"
mv "$NEWEST_APK_PATH" "$WSL_PATH/bin/$FINAL_NAME"
echo "Renamed in Linux: bin/$FINAL_NAME"

# 5. MOVE TO WINDOWS
echo "[5/6] Copying $FINAL_NAME to Windows..."
cp "$WSL_PATH/bin/$FINAL_NAME" "$WIN_PATH/$FINAL_NAME"

# 6. EMAIL THE FILE
echo "[6/6] Emailing APK to $RECIPIENTS..."
echo "New build for $APP_NAME version $EXTRACTED_VER is attached." | \
mutt -s "Build Success: $FINAL_NAME" -a "$WSL_PATH/bin/$FINAL_NAME" -- $RECIPIENTS

echo "-----------------------------------------------"
echo "SUCCESS! Build complete, renamed, and emailed."
echo "Linux: $WSL_PATH/bin/$FINAL_NAME"
echo "Windows: $WIN_PATH/$FINAL_NAME"
echo "-----------------------------------------------"
