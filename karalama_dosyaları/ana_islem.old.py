"""
main file for the project

program : detect 2d objects in screenshot and return their coordinates
 (2d objects are from images in imgs folder)
"""

import multiprocessing

import pynput
from tespit_islem import tespitDongusu


# creating main loop function and key press check functions
def main():
    global threshold
    global detection_process
    """
    main loop that controls key presses and calls other functions
    """
    threshold = 0.55
    parent_conn, child_conn = multiprocessing.Pipe()
    detection_process = multiprocessing.Process(target=tespitDongusu, args=(child_conn, threshold))

    def on_press(key):
        global threshold
        global detection_process
        """
        if key is 's' start detection loop
        elif key is 'd' stop detection loop
        else if key is 'q' quit program
        """
        if key == pynput.keyboard.KeyCode.from_char("s"):
            if detection_process.is_alive():
                print("sending stop event to detection process")
                parent_conn.send("stop")
                event = parent_conn.recv()
                log = "detection process stopped" if event == "stopping" else "something went wrong, event :" + event
                print(log)
                if event == "stopping":
                    print("detection process stopped")
                    return
                else:
                    print("something went wrong")
                    return
            else:
                print("starting detection process")
                detection_process.start()

        elif key == pynput.keyboard.KeyCode.from_char("d") and detection_process.is_alive():
            if detection_process.is_alive():
                print("detection is already running sendign close event")
                parent_conn.send("close")
                event = parent_conn.recv()
                if event == "closing":
                    print("detection process closed")
                    detection_process.terminate()
                    detection_process.join()
                    return
                else:
                    print("something went wrong")
                    return
            print("stopping detection")
            # stop detection loop
        elif key == pynput.keyboard.KeyCode.from_char("q"):
            print("quitting program")
            # quit program
            exit()

    # firstly create listener for key presses
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()


# calling main loop function
if __name__ == "__main__":
    main()
