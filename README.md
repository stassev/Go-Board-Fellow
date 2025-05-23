# Go Board Fellow 
Author: Svetlin Tassev

## Overview  
A web interface for playing Go with a physical board against computer opponents (GnuGo/KataGo). Key features:  
- **Board scanning** via camera/image upload  
- **Perspective correction** using grid corner calibration  
- **Voice commands** ("your turn" triggers move calculation)
- **The calculated next turn is both printed and announced by audio**. Thus, one does not need to look at the screen to see the next move. 
- **SGF export** -- saves the state of the board.

---
## Screenshots:
 - This game was played live. Recording was done by my laptop camera.
 - 
![play_go](https://github.com/user-attachments/assets/9d6f1953-e20d-4cfe-b55e-a26713be790f)

- The original image is from wikipedia. I ran the code on it.
- 
![19](https://github.com/user-attachments/assets/91bd0fa7-7a43-476a-94d6-d2163b261d1a)


---

## System Requirements  

1. **Engines** (install one/both):  
   - **GnuGo**:  
     ```
     sudo apt install gnugo  # Debian/Ubuntu
     ```
   - **KataGo**:  
     - Install KataGo: [Latest release](https://github.com/lightvector/KataGo/releases)
     - Rename the [KataGo network](https://katagotraining.org/) of your choice to "kata1-strongest.bin.gz". For example:
       ```
       mv kata1-b40c256-s11840935168-d3818872351.bin.gz kata1-strongest.bin.gz
       ```

2. **Browser**: Chrome/Chromium is required for speech recognition. Other browsers may work but have not been tested.

3. **Audio files**: If you want the next move to be spoken by the browser so you don't have to look at the screen, you have to create a subfolder "audio" and place .wav files for each letter and number corresponding to the board letter/number coordinates. For example, "a.wav", "b.wav",..., "1.wav", "2.wav", ... You can generate those audio files using the script
    ```
    python record_letters_numbers.py
    ```
    
---

## Setup & Calibration  

### **Start Backend** (run one of these scripts in terminal):
For GnuGo

    python gnugo_server.py

    
For KataGo

    python katago_server.py

or 

    python katago_server_weak.py

### **Start Browser**

       chromium --allow-file-access-from-files index.html
   
   Other browsers work as well but may not support speech recognition.

### **Calibration Steps** 

Point your camera at the physical board and start the browser.

1. Click grid corners in clockwise order. For example: 
   - Top-left (must match A19 for 19x19 boards)  
   - Top-right (T19)  
   - Bottom-right (T1)  
   - Bottom-left (A1)
2. Adjust the positions of the calibration points so that they align with **stone centers**, not grid intersections. Those may not match due to perspective distortions.
3. Place a few stones of each color on the board to calibrate the colors (black, white, board color)
4. Click "Calibrate colors". This step would work as long as the board color is not too bright/dark (so it's similar to the stone colors), and as long as there are no specular reflections from the board.



---

## Gameplay Workflow  

The steps below assume you have done the calibration in the previous step. Do not move the board or camera between turns.

1. **Board Capture**. Pick one of the two:  
- Live camera: Click "Take Photo" → "Capture" (Automatically triggered by speech recognition if you say "your turn")
- Image upload: Use "Upload Image" button  

2. **Move Calculation**:  
- Automatic: Automatically triggered by speech recognition if you say "your turn"
- Manual: Click "Process Image".

3. **Next move**: It is printed out and is spoken by the webpage as long as you generate the audio files in a subfolder "audio".

3. **Interface Controls**:  

| Setting          | Functionality                         |
|------------------|---------------------------------------|
| Board Size       | 9x9 to 19x19 grid support             |
| Computer Color   | Set Black/White assignment            |
| Strength Level   | 1-10 difficulty scale (has effect with GnuGo and the weakened KataGo backends)          |

---

##  **Troubleshooting**:  
- Speech recognition issues: Check browser microphone permissions.
- Camera issues: Check browser camera permissions.
- Detection errors: Readjust grid to match centers of stones, not grid. They may not perfectly align because of perspective distortions.
- Engine failures: Verify backend processes are running correctly.
