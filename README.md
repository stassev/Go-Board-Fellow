# Go Board Fellow 
Author: Svetlin Tassev

## Overview  
A web interface for playing Go on a physical board against a computer opponent (GnuGo/KataGo). Key features:  
- **Board scanning** via camera/image upload  
- **Stone detection**
- **Voice commands** (Saying "Next" triggers move calculation)
- **The calculated next turn is both printed and announced by audio**. Thus, one does not need to look at the screen to see the next move. 
- **SGF export** -- saves the state of the board.


---

## System Requirements  

1. **Engines** (install one/both):  
   - **GnuGo**:  
     ```
     sudo pacman -S gnugo  # Archlinux/Manjaro
     ```
   - **KataGo**:  
     - Install KataGo: [Latest release](https://github.com/lightvector/KataGo/releases)
     ```
     pamac install katago-cpu  # or other versions. This works on Manjaro
     ```
     - Download the [KataGo network](https://katagotraining.org/) of your choice and rename to "kata1-strongest.bin.gz". For example:
       ```
       mv kata1-b40c256-s11840935168-d3818872351.bin.gz kata1-strongest.bin.gz
       ```

2. **Browser**: Chrome/Chromium is required for speech recognition. Other browsers may work but have not been tested.

3. **Audio files (optional)**: If you want the next move to be spoken by the browser so you don't have to look at the screen, you have to create a subfolder "audio" and place .wav files for each letter and number corresponding to the board letter/number coordinates. For example, "a.wav", "b.wav",..., "1.wav", "2.wav", ... You can generate those audio files using the script
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

       chromium --allow-file-access-from-files --use-fake-ui-for-media-stream --test-type index.html
   
Other browsers work as well but may not support speech recognition. Note that "use-fake-ui-for-media-stream" is used if you are planning on using your phone as a camera.

### **Using Android phone as webcam (optional)**

1. Connect phone with usb cable to computer.
2. Execute (change parameters as needed; requires v4l2loopback module to be installed):

       sudo modprobe -r v4l2loopback
       sudo modprobe v4l2loopback devices=1 video_nr=2 card_label="Virtual_Webcam" exclusive_caps=1
       scrcpy --v4l2-sink=/dev/video2 --capture-orientation=0

3. Start phone camera.
4. Start Chrome/Chromium with:

       chromium --allow-file-access-from-files --use-fake-ui-for-media-stream --test-type index.html
       
5. Select camera from browser from dropdown menu.

### **Calibration Steps** 

Point your camera at the physical board and start the browser.

1. Place a few stones of each color on the board to calibrate the colors (black, white, board color). Place some of the stones at the grid corners to calibrate the grid.
2. Click the grid corners in the order specified below. To minimize perspective distortion issues, don't click on the grid itself, but rather on the centers of the 4 stones at the edges of the grid. The order of the grid coordinates that need to be clicked is:
   - A19 for 19x19 boards
   - T19
   - T1
   - A1
3. Adjust the positions of the calibration points so that they align with **stone centers**, not grid intersections. Those may not match due to perspective distortions.
4. Click "Calibrate colors". This step should work as long as the board color is not too bright/dark (so it's similar to the stone colors), and as long as there are no specular reflections from the board. The automatic calibration works well for uniformly lit boards. If not, use manual calibration by deselecting the "Automatic calibration" checkbox.

---

## Gameplay Workflow  

The steps below assume you have done the calibration in the previous step. Do not move the board or camera between turns.

1. **Board Capture**. Pick one of the two:  
- Live camera: Click "Take Photo" → "Capture" (Automatically triggered by speech recognition if you say "Next")
- Image upload: Use "Upload Image" button  

2. **Move Calculation**:  
- Automatic: Automatically triggered by speech recognition if you say "Next"
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
- Detection errors: Readjust grid to match centers of stones, not grid. They may not perfectly align because of perspective distortions. If stones are not identified correctly, try manual color calibration.
- Engine failures: Verify backend processes are running correctly.


---
## Screenshots:
 - This game was played live. Recording was done by my laptop camera.

![play_go](https://github.com/user-attachments/assets/9d6f1953-e20d-4cfe-b55e-a26713be790f)

 - The original image is from wikipedia. I ran the code on it.
  
![19](https://github.com/user-attachments/assets/91bd0fa7-7a43-476a-94d6-d2163b261d1a)

 - Set-up with phone as camera
  
![setup](https://github.com/user-attachments/assets/5aabd32f-e8f7-4c66-ae46-687b9265ca47)

 - Screenshot of Go Board Fellow using phone as camera:

![screen](https://github.com/user-attachments/assets/bc3c8952-afea-46d2-88fb-851a9ce70899)

