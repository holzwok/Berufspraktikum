import os

if os.name == 'nt':
    print "hallo windows"
    import pywintypes #@UnresolvedImport @UnusedImport
    #import pythoncom
    #import win32api
    from win32com.client import Dispatch
else:
    print "hallo unix"
    
print "juhuu..."

desktop = 'C:\\Users\\MJS\\My Dropbox\\Studium\\Berufspraktikum\\working_directory'

outpath = os.path.join(desktop, "bla.lnk")
target = os.path.join(desktop, "orig", r"Sic1_3xGFP__thumb_w1NIBA.TIF")
wDir = r"C:\Users\MJS\My Dropbox\Studium\Berufspraktikum\working_directory\orig"
#icon = r"P:\Media\Media Player Classic\mplayerc.exe"
 
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(outpath)
shortcut.Targetpath = target
shortcut.WorkingDirectory = wDir
#shortcut.IconLocation = icon
shortcut.save()

print "done"
