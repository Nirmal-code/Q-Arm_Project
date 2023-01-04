#Below is the code given to connect to Qlabs

import time
import sys
import random

sys.path.append('../')

from Common_Libraries.p2_sim_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()
update_thread = repeating_timer(2, update_sim)


#Below is the function to move the arm to desired location.
#Creator:Nirmal
def move_end(container_id, location): #Location parameter corresponds to the location the arm must move to.
    while(True): #While the right arm is not greater than threshold, this iteration will continue.
        if arm.emg_right()>=0.5 and arm.emg_left()==0.0:
            arm.move_arm(location[0], location[1], location[2])
            break

#Below is the function to give the desired autoclave coordinates.
def autoclave_loc(container_id):
    if container_id==1: #Small Red Container
        auto_loc=[-0.61, 0.247, 0.4]
    elif container_id==2: #Small Green Container
        auto_loc=[-0.0, -0.65, 0.4]
    elif container_id==3: #Small Blue Container
        auto_loc=[0.0, 0.65, 0.4]
    elif container_id==4: #Large Red Container
        auto_loc=[-0.41, 0.15, 0.318]
    elif container_id==5: #Large Green Container
        auto_loc=[0.0, -0.428, 0.318]
    elif container_id==6: #Large Blue Container
        auto_loc=[0.0, 0.433, 0.318]
    return auto_loc

#Below is a function to control the gripper of the arm. It has the parameter open_close which corresponds to whether gripper is open or closed; True means closed, False mean opened.
def control_gripper(container_id, open_close):
    while(True): #While the left and right muscle sensor emulators are not greater than the threshold. 
        if open_close==False: #If the gripper is closed, then we want to open the gripper.
            if (arm.emg_left()>=0.5 and arm.emg_right()>=0.5):
                if (container_id==1 or container_id==2 or container_id==3):
                    arm.control_gripper(45)
                else:
                    arm.control_gripper(35)
                break
        elif open_close==True: #If gripper is open, we want to close the gripper.
            if (arm.emg_left()>=0.5 and arm.emg_right()>=0.5):
                if (container_id==1 or container_id==2 or container_id==3):
                    arm.control_gripper(-45)
                else:
                    arm.control_gripper(-35)
                break

#Below is a function to control the autobins; open or close them. Takes Parameter open_close to see whether bin is open or closed; false is closed, true is open.
def open_close_clave(container_id, open_close):
    if (container_id==4 or container_id==5 or container_id==6):#Checks if container is big. If not, skips over function
        while (True): #While the left muscle sensor emulator is not greater than threshold, code below will run.
            if arm.emg_right()==0.0 and arm.emg_left()>=0.5:
                if open_close==False: #If the bin isn't open, we must open the bin.
                    if container_id==4:
                        arm.open_red_autoclave(True)
                    elif container_id==5:
                        arm.open_green_autoclave(True)
                    else:
                        arm.open_blue_autoclave(True)
                else: #If the bin is open, we must close the bin.
                    if container_id==4:
                        arm.open_red_autoclave(False)
                    elif container_id==5:
                        arm.open_green_autoclave(False)
                    else:
                        arm.open_blue_autoclave(False)
                    time.sleep(1)
                break


            
arm.home() #At the beginning, always set arm to home position.
container_list=[1,2,3,4,5,6] #Contains an initial list will all container IDs.
spawn_loc=[0.534, 0.0, 0.03] #Coordinates the arm must go to, to pick up the container.
home=[0.416, 0.0, 0.483] #Coordinates for the home position of the arm.

while(len(container_list)!=0):#Code below will be iterated until all 6 containers have been spawned. 
    time.sleep(1)
    container_index=random.randint(0,len(container_list)-1)
    container_id=container_list[container_index] #Container ID stored as value of the container at the position, which is randomly selected from previous line, from the list of containers.
    arm.spawn_cage(container_id)
    print("Container ID is: ", container_id)

    move_end(container_id, spawn_loc) #Arm moves to container spawn coordinates.
    control_gripper(container_id, False) #Arm grips onto container.
    
    autoloc=autoclave_loc(container_id) #Necessary autoclave coordinates defined.

    move_end(container_id, autoloc) #Arm moves container to corresponding autoclave location.
    open_close_clave(container_id, False) #Open bin (if container is large).
    
    control_gripper(container_id, True) #Release container into autoclave.
    open_close_clave(container_id, True) #Close bin (if container large).

    
    move_end(container_id, home) #Arm moves to intial home position, ready for next container.

    container_list.pop(container_index) #Removes the placed container from the container list so it is not spawned again.
    
