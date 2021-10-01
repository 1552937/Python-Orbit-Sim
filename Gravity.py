# Nathaniel Morin
# 8/22/2021

import pygame
import sys
import math
import random
import copy
from tkinter import *
from Body import Body

pygame.init()

root = Tk()
root.title("Orbit Preset")

displayInfo = [] # stores what should be drawn (vectors, gravity forces, etc.)

def enter():
	global displayInfo
	displayInfo = [bool(vec_int.get()), bool(grav_int.get()), bool(aggGrav_int.get()), \
	bool(trail_int.get()), bool(centerOfMass_int.get())]
	root.destroy()

vec_int = IntVar()
grav_int = IntVar()
aggGrav_int = IntVar()
trail_int = IntVar()
centerOfMass_int = IntVar()

vec_check = Checkbutton(root, text = 'Draw vectors', variable = vec_int)
grav_check = Checkbutton(root, text = 'Draw gravity', variable = grav_int)
aggGrav_check = Checkbutton(root, text = 'Draw net grav', variable = aggGrav_int)
trail_check = Checkbutton(root, text = 'Draw trail', variable = trail_int)
centerOfMass_check = Checkbutton(root, text = 'Draw center of mass', variable = centerOfMass_int)

enter_button = Button(root, text = "Enter", command = enter, padx = 70, pady = 10, borderwidth = 4)

vec_check.grid(row = 0, column = 0, sticky = "W", padx = 40)
grav_check.grid(row = 1, column = 0, sticky = "W", padx = 40)
aggGrav_check.grid(row = 2, column = 0, sticky = "W", padx = 40)
trail_check.grid(row = 3, column = 0, sticky = "W", padx = 40)
centerOfMass_check.grid(row = 4, column = 0, sticky = "W", padx = 40)

enter_button.grid(row = 5, column = 0)

root.mainloop()

# what happens if the window was exited without pressing 'enter'
# the list 'displayInfo' would be empty if this happened
displayInfo = [False, False, False, False] if displayInfo == [] else displayInfo

# variables
screenWidth = 800
screenHeight = 800

clock = pygame.time.Clock()

fps = 30
frame_count = 0

game_font  = pygame.font.SysFont('calibri', 40, bold = True)
frame_text_location = (10, 10)
mass_text_location = (10, 50)
typedNum_text_location = (10, 90)

backUp = True
numKeysUp = True
rightArrowUp = True

camera_speed = 12

SQRT2_RECIP = 1/math.sqrt(2)

WHITE = pygame.Color(255, 255, 255) 

screen = pygame.display.set_mode((screenWidth, screenHeight))

background = pygame.Rect((0, 0), (screenWidth, screenHeight))
background_color = pygame.Color(30, 30, 30)

bodies = []

# planet formation
def generateRandomBodies(numBodies, massRange):
	return [Body((random.randint(0, screenWidth), random.randint(0, screenHeight)),\
		[0,0],\
		random.randint(massRange[0], massRange[1]),\
		screen,\
		released = True,\
		fixed = False) for _ in range(numBodies)]

bodies = generateRandomBodies(250, (20_000, 50_000))

# # oscellation							
# oscMass = 500
# bodies = [Body((200, 400), [0, 0], oscMass, screen, released=True, fixed=True), \
# Body((600, 400), [0, 0], oscMass, screen, released=True, fixed=True), \
# Body((400, 100), [0, 0], 30, screen, released = True)]

# # circular orbit
# dist = 200
# mass1, mass2 = 8100, 100
# magnitude2 = math.sqrt((Body.G*mass1)/dist)*mass2
# print(magnitude2)
# pos1 = (400, 400)
# pos2 = (pos1[0]+dist, pos1[1])
# angle2 = Body.findRadianAngleFromCoords(pos1, pos2) + math.pi/2
# bodies = [Body((400, 400), [0, 0], mass1, screen, released=True, fixed=True), \
# Body((400+dist, 400), Body.findVectorFromMagnitudeAndAngle(magnitude2, angle2), mass2, screen, released = True, fixed = False)]

initialState = [ele for ele in bodies]

numberKeys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, \
pygame.K_8, pygame.K_9] # needs to be in order 
prospectiveMass = 0
typedNum = ""

leftClickBodyMass = 500_000
rightClickBodyMass = 7_500_000

launch_line_length_scaler = 7.5

def generateNewBody(pos, mass):
	return Body(pos, [0, 0], mass, screen)

# made for clarity
def numberKeyIsPressed(pressed):
	return sum([pressed[nKey] for nKey in numberKeys]) > 0

# made for clarity
def numberKeyPressed(pressed):
	return [pressed[nKey] for nKey in numberKeys].index(True)

# moves the camera a certain amount in the x and/or y directions
def moveCamera(dx=0, dy=0):
	for body in bodies:
		body.pos = (body.pos[0]-dx, body.pos[1]-dy)
		for i in range(len(body.trailList)):
			body.trailList[i] = (body.trailList[i][0]-dx, body.trailList[i][1]-dy)

game_over = False

while not game_over:
	# Quitting the game if it is exited
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			game_over = True

	pressed = pygame.key.get_pressed()

	clock.tick(fps)

	# drawing the background
	screen.fill(background_color)

	# exiting the game if escape is pressed
	if pressed[pygame.K_ESCAPE]:
		game_over = True

	# clearing the screen if space is pressed
	if pressed[pygame.K_SPACE]:
		frame_count = 0
		if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
			bodies.clear()
		else:
			bodies = [ele.reset() for ele in initialState]

	# moving the camera with the 'w', 'a', 's', and 'd' keys
	if pressed[pygame.K_w]:
		if pressed[pygame.K_a] or pressed[pygame.K_d]:
			if pressed[pygame.K_a]:
				moveCamera(-1*camera_speed*SQRT2_RECIP, -1*camera_speed*SQRT2_RECIP)
			if pressed[pygame.K_d]:
				moveCamera(camera_speed*SQRT2_RECIP, -1*camera_speed*SQRT2_RECIP)
		else:
			moveCamera(dy=-1*camera_speed)
	if pressed[pygame.K_a] and not pressed[pygame.K_w]:
		if pressed[pygame.K_s]:
			moveCamera(-1*camera_speed*SQRT2_RECIP, camera_speed*SQRT2_RECIP)
		else:
			moveCamera(dx=-1*camera_speed)
	if pressed[pygame.K_s] and not pressed[pygame.K_a]:
		if pressed[pygame.K_d]:
			moveCamera(camera_speed*SQRT2_RECIP, camera_speed*SQRT2_RECIP)
		else:
			moveCamera(dy=camera_speed)
	if pressed[pygame.K_d] and not pressed[pygame.K_w] and not pressed[pygame.K_s]:
		moveCamera(dx=camera_speed)

	# drawing the center of mass
	if displayInfo[4] and len(bodies) > 0:
		Body.drawCenterOfMass(bodies, screen)

	# creating a new body
	if event.type == pygame.MOUSEBUTTONDOWN and backUp: # fATgWvCQY@3r.if
		click_loc = pygame.mouse.get_pos()
		if pygame.mouse.get_pressed()[2]:
			newMass = rightClickBodyMass
		else:
			newMass = leftClickBodyMass
		prospectiveMass = newMass
		newBody = generateNewBody(click_loc, newMass)
		# making the new generated body 'fixed' if shift is pressed
		newBody.fixed = pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]
		bodies.append(newBody)
		backUp = False

	# displaying the magnitude indicator line and listening for keypresses related to generating bodies
	if not backUp:
		heldBody = bodies[-1]
		newMass = heldBody.mass
		# increasing and decreasing the mass of a held 'Body' with the up and down arrow keys
		if pressed[pygame.K_UP]:
			newMass = heldBody.mass + 1
		elif pressed[pygame.K_DOWN]:
			newVolume = (heldBody.mass-1)/Body.density
			newRad = (3*newVolume/(4*math.pi))**(1/3)
			# preventing the mass from becoming zero
			if not type(newRad) == complex and not heldBody.mass == 1:
				newMass = heldBody.mass-1
		# allowing the user to type in a mass for a body while it is held
		if numKeysUp and numberKeyIsPressed(pressed):
			num = numberKeyPressed(pressed)
			typedNum += str(num)
			numKeysUp = False
		# entering the typed num
		# 'and not typedNum == ""' is necessary because the enter press could be registered multiple times,
		# and "" cannot be parsed as an 'int'
		if pressed[pygame.K_RETURN] and not typedNum == "":
			newMass = int(typedNum)
			typedNum = ""
		# setting the new mass
		if newMass != heldBody.mass:
			prospectiveMass = newMass
			heldBody.setMass(newMass)
		# displaying the mass of the held body
		mass_label_text = "Mass: {}".format(prospectiveMass)
		mass_label = game_font.render(mass_label_text, 1, WHITE)
		screen.blit(mass_label, mass_text_location)
		# displaying number that is currently being typed ('typedNum')
		if not typedNum == "":
			typedNum_label_text = "Typed: {}".format(typedNum)
			typedNum_label = game_font.render(typedNum_label_text, 1, WHITE)
			screen.blit(typedNum_label, typedNum_text_location)

		# getting the location of the mouse
		held_loc = pygame.mouse.get_pos()
		exaggerated_max_speed = Body.max_speed * launch_line_length_scaler
		# distance from the mouse position to the center of the body
		held_distance = Body.findDistance(heldBody.pos, held_loc)
		# Stopping the magnitude indicator thing from exceeding its max length while also maintaing in the angle from the mouse to the center of the circle
		if held_distance > exaggerated_max_speed:
			held_radian_angle = Body.findRadianAngleFromCoords(heldBody.pos, held_loc)
			displayed_x = exaggerated_max_speed * math.cos(held_radian_angle) + heldBody.pos[0]
			displayed_y = exaggerated_max_speed * math.sin(held_radian_angle) + heldBody.pos[1]
			held_loc = (displayed_x, displayed_y)
			held_distance = exaggerated_max_speed
		# drawing the magnitude indicator line
		# multiplying Body.max_speed by 7.5 shows how fast a body would travel in 0.25 seconds as opposed to 0.033 seconds, as this is easier to see when dragging the line
		pygame.draw.line(screen, pygame.Color(255, int(255 - (held_distance / exaggerated_max_speed * 255)), 0), heldBody.pos, held_loc, 5)

	if not numberKeyIsPressed(pressed):
		numKeysUp = True

	# launching the body
	if event.type == pygame.MOUSEBUTTONUP and not backUp:
		heldBody = bodies[-1]
		# distance from the center of the body to the location that the mouse was released
		launch_magnitude_raw = Body.findDistance(heldBody.pos, held_loc)
		# getting the magnitude of the line
		launch_magnitude = launch_magnitude_raw / launch_line_length_scaler
		# getting the angle of the launch
		launch_angle = math.radians((math.degrees(Body.findRadianAngleFromCoords(heldBody.pos, held_loc)) + 180) % 360)
		# assigning new dx and dy values to the body
		new_dx, new_dy = launch_magnitude * math.cos(launch_angle), launch_magnitude * math.sin(launch_angle)
		heldBody.vec = [new_dx*heldBody.mass, new_dy*heldBody.mass]
		heldBody.released = True
		backUp = True
		typedNum = ""

	# tab button is not pressed, pause the game
	# if the right arrow is tapped while paused, advance one frame
	if pressed[pygame.K_TAB] and not (pressed[pygame.K_RIGHT] and rightArrowUp):
		if not pressed[pygame.K_RIGHT]:
			rightArrowUp = True
	else:
		frame_count += 1
		# moving the bodies
		for body in bodies:
			body.update()

		Body.checkForBodyCollision(bodies)
		Body.applyGravity(bodies)

		rightArrowUp = False

	# drawing the balls
	for b in bodies:
		b.draw(drawVec = displayInfo[0], drawGrav = displayInfo[1], drawAgg = displayInfo[2], drawTrail = displayInfo[3])	

	frame_label_text = "Frame: {}".format(frame_count)
	frame_label = game_font.render(frame_label_text, 1, WHITE)
	screen.blit(frame_label, frame_text_location)

	pygame.display.update()
	pygame.display.flip()