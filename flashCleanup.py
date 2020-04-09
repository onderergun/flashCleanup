import csv
from jsonrpclib import Server
import ssl
from getpass import getpass
import os
import argparse

ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument('--username', required=True)
parser.add_argument('--inventoryname', required=True)


args = parser.parse_args()
switchuser = args.username
inventory = args.inventoryname
switchpass = getpass()

def dirflash(switchuser, switchpass, ssh_host):
    command_string = "dir *.swi"
    urlString = "https://{}:{}@{}/command-api".format(switchuser, switchpass, ssh_host)
    switchReq = Server(urlString)
    response = switchReq.runCmds( 1, ["enable", command_string],"text" )
    responsePr = response [1]["output"]
    linebyline=responsePr.splitlines()
    images=[]
    for line in linebyline:
        nowhite=line.split()
        if len(nowhite)==6:
            if nowhite[5][-3:] == "swi":
                images.append(nowhite[5])
            if "free" in nowhite[5]:
                freebytes=nowhite[3].split('(')[1]
                freeMbytes=(int(freebytes))/1000000
    return (images,freeMbytes)

def getCurrentImage(switchuser, switchpass, ssh_host):
    command_string = "show boot-config"
    urlString = "https://{}:{}@{}/command-api".format(switchuser, switchpass, ssh_host)
    switchReq = Server(urlString)
    response = switchReq.runCmds( 1, ["enable", command_string] )
    responsePr = response [1]["softwareImage"]
    currentimage=responsePr.split('/')[1]
    return currentimage

def deleteFile(switchuser, switchpass, ssh_host, image):
    command_string = "delete flash:"+image
    urlString = "https://{}:{}@{}/command-api".format(switchuser, switchpass, ssh_host)
    switchReq = Server(urlString)
    response = switchReq.runCmds( 1, ["enable", command_string] )
    return response

with open(inventory) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for iter,row in enumerate(csv_reader):
       if iter == 0 :
           for num,column in enumerate(row):
               if column == "IP Address" or column == "IPAddress":
                   hostIndex=num
       else:
           ssh_host=row[hostIndex]
           print ssh_host
           flashcontents=dirflash(switchuser,switchpass,ssh_host)
           currentimage= getCurrentImage(switchuser, switchpass, ssh_host)
           print "Current image is: ",currentimage
           images = flashcontents[0]
           freeMbytes=flashcontents[1]
           if len(images)==1:
               if images[0] == currentimage:
                   print "There are no images to delete"
                   print freeMbytes, "MBytes free"
           if len(images)>1:
               for image in images:
                   if image != currentimage:
                       print "deleting ", image
                       deleteFile(switchuser, switchpass, ssh_host, image)
                       if deleteFile == {}:
                           print "Success"
               print "There are no more images to delete"
               flashcontents=dirflash(switchuser,switchpass,ssh_host)
               freeMbytes=flashcontents[1]
               print freeMbytes, "MBytes free"
