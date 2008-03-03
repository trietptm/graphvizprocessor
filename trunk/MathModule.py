from math import *

def GetBulletPos(sx,sy,dx,dy,angle_C,bullet_len):
	x=float(dx-sx)
	y=float(dy-sy)
	if x!=0:
		angle_A=abs(atan(y/x)*(180/pi))
	else:
		angle_A=90
	if x>0 and y>0:
		pass
	elif x<=0 and y>0:
		angle_A=180-angle_A
	elif x<=0 and y<=0:
		angle_A=180+angle_A
	elif x>0 and y<=0:
		angle_A=360-angle_A
	
	angle_D=angle_A+180-angle_C
	angle_E=angle_A+180+angle_C	
	x1=dx+bullet_len*cos(angle_D*(pi/180))
	y1=dy+bullet_len*sin(angle_D*(pi/180))
	x2=dx+bullet_len*cos(angle_E*(pi/180))
	y2=dy+bullet_len*sin(angle_E*(pi/180))
	return [x1,y1,x2,y2,dx,dy]

if __name__=='__main__':
	print GetBulletPos(10,10,30,50,15,5)
	print GetBulletPos(10,10,30,11,15,5)
	print GetBulletPos(10,10,11,50,15,5)
	print GetBulletPos(30,50,10,10,15,5)
	print GetBulletPos(10,60,30,50,15,5)
	print GetBulletPos(30,50,10,60,15,5)