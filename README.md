# CreateProcessAsCurrentUser-python

Description:
  This script enables you to run a process within the current user session. Special thanks to [murrayju/CreateProcessAsUser](https://github.com/murrayju/CreateProcessAsUser) for providing the inspiration and foundation, which I've implemented in Python.
  
  This script is very useful when your RMM tool supports Python scripting but lacks the capability to execute scripts with the privileges of the currently logged-in user.  It's also very useful when you need to initiate a process within the current user session from a different session, such as a Windows service running in session 0 with a GUI, enabling user 
  visibility and interaction.

**NOTE:**
  This script must run with system privilege to initiate process within the current user session

Examples of how to use this script:

  1. if you want to open up notepad++ in the current user session, call the start_process_as_current_user as shown below,
     ```python
      start_process_as_current_user(r"C:\Program Files\Notepad++\notepad++.exe")
     ```
  
  3. if you want to execute powershell commands in the current user session, call the start_process_as_current_user as shown below,
     ```python
      start_process_as_current_user(r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe', r'"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -WindowStyle Hidden -command "whoami /priv | Out-File -filepath C:\Users\coding\Desktop\testing.txt"')
     ```
      (or)
     ```python
      start_process_as_current_user(AppPath='powershell.exe', cmdLine=r'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -command "whoami /priv | Out-File -filepath C:\Users\coding\Desktop\testing.txt"', workDir=r"C:\Windows\System32\WindowsPowerShell\v1.0")
     ```
  5. if you want to execute cmd commands in the current user session, call the start_process_as_current_user as shown below,
     ```python
     start_process_as_current_user(AppPath=r'cmd.exe',cmdLine=r'cmd.exe /c "whoami /priv >> C:\Users\coding\Desktop\testing.txt"',workDir=r"C:\Windows\System32")
     ```

   
# Feature updates - 28/05/2024:
  ### Redirect Output and Error for Child Process:
    Now you can redirect output and error streams of the child process initiated by the script. so, you don't need to save the output in a file like this 'cmd.exe /c "whoami /priv >> C:\Users\coding\Desktop\testing.txt'. all you have to do to redirect output and error stream is to set CreatePIPE_and_Redirect_OUTPUT       to True. checkout the below example of how to do it:
    ```python
      start_process_as_current_user(AppPath=r'cmd.exe',cmdLine=r'cmd.exe /c "whoami /priv"',workDir=r"C:\Windows\System32", visible=False, CreatePIPE_and_Redirect_OUTPUT=True)
     ```
     if you run the above code, you will get the following output:
     <blockquote>
       Output for the process created using CreateProcessAsUserW:

        PRIVILEGES INFORMATION
        ----------------------
        
        Privilege Name                Description                          State
        ============================= ==================================== ========
        SeShutdownPrivilege           Shut down the system                 Disabled
        SeChangeNotifyPrivilege       Bypass traverse checking             Enabled
        SeUndockPrivilege             Remove computer from docking station Disabled
        SeIncreaseWorkingSetPrivilege Increase a process working set       Disabled
        SeTimeZonePrivilege           Change the time zone                 Disabled
        
        Exit code for the process created using CreateProcessAsUserW: 0
      </blockquote>

    If I mistakenly give the wrong syntax like this "whoiam /rpiv", you will get the following error:
    <blockquote>
    Error for the process created using CreateProcessAsUserW:
     'whoiam' is not recognized as an internal or external command,
    operable program or batch file.
    
    Exit code for the process created using CreateProcessAsUserW: 1
    </blockquote>
