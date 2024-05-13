# CreateProcessAsCurrentUser-python

Description:
  This script enables you to run a process within the current user session. Special thanks to [murrayju/CreateProcessAsUser](https://github.com/murrayju/CreateProcessAsUser) for providing the inspiration and foundation, which I've implemented in Python.
  
  This script is very useful when your RMM tool supports Python scripting but lacks the capability to execute scripts with the privileges of the currently logged-in user.  It's also very useful when you need to initiate a process within the current user session from a different session, such as a Windows service running in session 0 with a GUI, enabling user 
  visibility and interaction.

**NOTE:**
  This script must run with system privilege to initiate process within the current user session

Examples of how to use this script:

  1. if you want to open up notepad++ in the current user session, call the start_process_as_current_user as shown below,
  
      start_process_as_current_user(r"C:\Program Files\Notepad++\notepad++.exe")
  
  2. if you want to execute powershell commands in the current user session, call the start_process_as_current_user as shown below,
  
      start_process_as_current_user(r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe', r'"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -WindowStyle Hidden -command "whoami /priv | Out-File -filepath C:\Users\coding\Desktop\testing.txt"')
  
      (or)
  
      start_process_as_current_user(AppPath='powershell.exe', cmdLine=r'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -command "whoami /priv | Out-File -filepath C:\Users\coding\Desktop\testing.txt"', workDir=r"C:\Windows\System32\WindowsPowerShell\v1.0")
  
  3. if you want to execute cmd commands in the current user session, call the start_process_as_current_user as shown below,
     
     start_process_as_current_user(AppPath=r'cmd.exe',cmdLine=r'cmd.exe /c "whoami /priv >> C:\Users\coding\Desktop\testing.txt',workDir=r"C:\Windows\System32")


   
