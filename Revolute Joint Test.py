#Author- Shi Yuyan
#Description-Collect standard positions of roll and pitch for reference

import adsk.core, adsk.fusion, traceback, math, time, csv

#change all angles in range 180-360 to be in range 0-180
def angle_change(n):
	if n > 180 and n <= 360:
		n = n - 360
	elif n > 360:
		print("angle_error; angle is larger than 360")
	return n

def run(context):
  ui = None
  try:
    #access current design, create shortcuts to access components 
    app = adsk.core.Application.get()
    ui  = app.userInterface
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent #root is the main assembly here

    #create shortcuts for left, right joint, pitch and roll 
    #if your joint is in a subassembly, make sure to navigate to the subassembly instead of root
    right_joint = root.joints.itemByName('right_servo') 
    left_joint = root.joints.itemByName('left_servo')
    roll = root.joints.itemByName('roll')
    pitch = root.joints.itemByName('pitch')

    #instruct the UI to pop out a folder window to save the data under a csv file
    fileDialog = ui.createFileDialog()
    fileDialog.isMultiSelectEnabled = False
    fileDialog.title = "Specify result filename"
    fileDialog.filter = 'CSV files (*.csv)'
    fileDialog.filterIndex = 0
    dialogResult = fileDialog.showSave()
    if dialogResult == adsk.core.DialogResults.DialogOK:
        filename = fileDialog.filename
    else:
        return

    #open the csv file and edit the csv file
    with open(filename, 'w', newline='') as csvfile:
      fieldnames = ['left_rel_angle', 'right_rel_angle', 'roll', 'pitch']               #define the fieldnames
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)                     #write the csv file with designated fieldnames
      writer.writeheader()                       #write fieldnames on the first row of the csv file 

      #create right and left revolut joint shortcut 
      right_rev = adsk.fusion.RevoluteJointMotion.cast(right_joint.jointMotion)
      left_rev = adsk.fusion.RevoluteJointMotion.cast(left_joint.jointMotion)
      
      for i in range(-70,72,2):                     #write right servo angle every 5 degree from -70 to 72(non-inclusive)
        right_rel = i 
        for j in range(-70,72,2):                   #write left servo angle every 5 degree from -70 to 72(non-inclusive)
          left_rel = j
          
          #check for mini servo leg to not bend the other way; filter out unwanted inputs
          if (abs(i) >= 55 or abs(j) >= 55) and abs(i+j) <= 30:
            print('risky input!')
            roll_resultant = None
            pitch_resultant = None

          else:
            left_joint.isLocked = False                                             #unlock left joint
            right_joint.isLocked = False                                            #unlock right joint
            right_rev.rotationValue = right_rel * (math.pi/180.0)                   #drive right revolut joint to right_rel

            #set left servo revolute joint to left_rel
            left_joint.isLocked = False                                             #unlock left joint
            right_joint.isLocked = True                                             #lock right joint
            left_rev.rotationValue = left_rel * (math.pi/180.0)                     #drive right revolut joint to right_rel

            #command to allow Fusion to update graphics; disable this if you do not want to see the graphics 
            adsk.doEvents()
          
            #verify that joints moved as intended 
            right_output = float(math.degrees(right_joint.jointMotion.rotationValue))  #read right servo revolut joint angle from model
            right_output = angle_change(right_output)
            left_output = float(math.degrees(left_joint.jointMotion.rotationValue))    #read left servo revolut joint angle from model
            left_output = angle_change(left_output)

            #if either left or right servo readings differ by more than 0.5 degrees
            if abs(left_output-left_rel) > 0.5 or abs(right_output-right_rel) > 0.5:
            
            # #filter out unwanted inputs
            # if (abs(left_rel) >= 45 or abs(left_rel) >= 45) and abs(left_rel) <= 30:
            #   print('risky input!')

            #try driving the joints again, this time starting with left servo joint
            # else:
              left_joint.isLocked = False                                             
              right_joint.isLocked = False
              left_rev.rotationValue = left_rel * (math.pi/180.0)

              left_joint.isLocked = True                                            
              right_joint.isLocked = False
              right_rev.rotationValue = right_rel * (math.pi/180.0)

            #read rght and left servo angle from model
            right_output = float(math.degrees(right_joint.jointMotion.rotationValue))
            right_output = angle_change(right_output)
            left_output = float(math.degrees(left_joint.jointMotion.rotationValue))
            left_output = angle_change(left_output)

            #if left and right servo angles differ from input by more than 0.5 degrees, put roll and pitch values are None
            if abs(left_output-left_rel) > 0.5:
              print('left joint error, input:{:.3f}, output:{:.3f},'.format(left_rel, left_output))
              roll_resultant = None
              pitch_resultant = None
              print('error')
            elif abs(right_output-right_rel) > 0.5:
              print('right joint error, input:{:.3f}, output:{:.3f},'.format(right_rel, right_output))
              roll_resultant = None
              pitch_resultant = None
              print('error')
          
            #measure the roll and pitch values and write the corresponding left right servo, roll pitch values to the csv file
            else:
              #measure resultant pitch and roll values
              pitch_resultant = round(math.degrees(pitch.jointMotion.rotationValue))
              pitch_resultant = angle_change(pitch_resultant)
              roll_resultant = round(math.degrees(roll.jointMotion.rotationValue))
              roll_resultant = angle_change(roll_resultant)

          print('left_rel_angle:', left_rel, 'right_rel_angle:', right_rel, 'Roll:', roll_resultant,'Pitch:', pitch_resultant)
          writer.writerow({'left_rel_angle': left_rel, 'right_rel_angle': right_rel, 'roll': roll_resultant, 'pitch': pitch_resultant})
    csvfile.close()
    print('Finished collecting all data points')

  #if there are any errors in the process, fusion UI will pop up window with error message
  except:
    if ui:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
