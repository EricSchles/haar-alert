#!/usr/bin/python

'''
Haar Alert

Author: Morgan Phillips
Email : winter2718@gmail.com

@Copyleft 2012

'''
import cv
import argparse
import os
import glob
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def sendMessage(gmailUsername,gmailPassword,recipients,filename):

	message = MIMEMultipart()
	message['Subject'] = '[Haar Detect] Possible Match'
	message['From'] = gmailUsername
	message['To'] = recipients
	message.preamble = filename

    	fp = open(filename, 'rb')
    	img = MIMEImage(fp.read())
    	fp.close()
    	message.attach(img)

	server = smtplib.SMTP('smtp.gmail.com',587) 
	server.ehlo()
	server.starttls()
	server.ehlo()
        server.login(message['From'],gmailPassword)
	print "Sending "+filename
	server.sendmail(message['From'], message['To'], message.as_string())
	server.close()


'''
Parse our arguments!
'''

parser = argparse.ArgumentParser(description='Scan a directory for images with objects and email the results.')
parser.add_argument('-U','--Username',help='set username for gmail account')
parser.add_argument('-P','--Password',help='set password for gmail account')
parser.add_argument('-T','--To',help='comma delimited address list for email recipients')
parser.add_argument('-path','--search-path',required=True,help='directory to scan for images')
parser.add_argument('-ext','--extension',default='jpg',help='image extension to search for')
parser.add_argument('-sM','--send-message',default=True,help='set to Flase in order to turn off email alerts')
parser.add_argument('-M','--mark-files',default=True,help='set to False in order to turn off file marking.')
parser.add_argument('-X','--display',default=False,help='display images')
parser.add_argument('-X_t','--display-timer',default=1000,help='delay between displayed images in display mode (ms)')
parser.add_argument('-haar','--haar-cascade-file',default='haarcascades/haarcascade_frontalface_default.xml',help='a haarcascade file for detection of objects/faces (defaults to haarcascade_frontalface_default.xml)')
parser.add_argument('-scale','--scale-factor',default='1.25',help='scale factor for object/face detection')

args = vars(parser.parse_args())

'''
Scan directory and apply haar cascade
'''

path = args['search_path']
print "Scanning "+path
    
for infile in glob.glob( os.path.join(path, '*.'+args['extension']) ):

	extSearchPosition = 9+len(args['extension'])
	if infile[-extSearchPosition:] == 'hscanned.'+args['extension']:
       		pass
	else:
 
		print "current file is: " + infile

		image = cv.LoadImage(infile,1)

		storage = cv.CreateMemStorage()

		haar=cv.Load(args['haar_cascade_file'])

		detected = cv.HaarDetectObjects(image, haar, storage, float(args['scale_factor']), 2,cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))

		if detected:
			if args['send_message'] == 'True':
				sendMessage(args['Username'],args['Password'],args['To'],infile)
		
			for (x,y,w,h),n in detected:
				print "Object Match: "+infile+" @ " +str(x)+","+str(y)
				
				if args['display'] == 'True':
					cv.Rectangle(image,(x,y),(x+w,y+h),255)
		
		if args['mark_files'] == 'True':
			os.rename(infile,infile[:-len(args['extension'])]+'hscanned.'+args['extension'])
		
		if args['display'] == 'True':
			cv.ShowImage('fd.py',image)
			cv.WaitKey(int(args['display_timer']))
