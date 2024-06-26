import os
import ctypes
from ctypes import wintypes
from enum import IntEnum


class ProcessCreationException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

CREATE_UNICODE_ENVIRONMENT = 0x00000400
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_CONSOLE = 0x00000010
INVALID_SESSION_ID = 0xFFFFFFFF
WTS_CURRENT_SERVER_HANDLE = ctypes.c_void_p()
STARTF_USESHOWWINDOW = 0x00000001
STARTF_USESTDHANDLES = 0x00000100



advapi32 = ctypes.windll.advapi32
userenv = ctypes.windll.userenv
kernel32 = ctypes.windll.kernel32
wtsapi32 = ctypes.windll.wtsapi32




class SW(IntEnum):
    SW_HIDE = 0,
    SW_SHOWNORMAL = 1,
    SW_NORMAL = 1,
    SW_SHOWMINIMIZED = 2,
    SW_SHOWMAXIMIZED = 3,
    SW_MAXIMIZE = 3,
    SW_SHOWNOACTIVATE = 4,
    SW_SHOW = 5,
    SW_MINIMIZE = 6,
    SW_SHOWMINNOACTIVE = 7,
    SW_SHOWNA = 8,
    SW_RESTORE = 9,
    SW_SHOWDEFAULT = 10,
    SW_MAX = 10

class WTS_CONNECTSTATE_CLASS(IntEnum):
    WTSActive = 0
    WTSConnected = 1
    WTSConnectQuery = 2
    WTSShadow = 3
    WTSDisconnected = 4
    WTSIdle = 5
    WTSListen = 6
    WTSReset = 7
    WTSDown = 8
    WTSInit = 9

class SECURITY_IMPERSONATION_LEVEL(IntEnum):
    SecurityAnonymous = 0
    SecurityIdentification = 1
    SecurityImpersonation = 2
    SecurityDelegation = 3

class TOKEN_TYPE(IntEnum):
    TokenPrimary = 1
    TokenImpersonation = 2

class WTS_SESSION_INFO(ctypes.Structure):
    _fields_ = [
        ('SessionID', ctypes.c_uint),
        ('pWinStationName', ctypes.c_char_p),
        ('State', ctypes.c_uint)  
    ]
class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", ctypes.c_void_p),
        ("hThread", ctypes.c_void_p),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]           
                            
class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_uint),
        ("lpReserved", ctypes.c_char_p),
        ("lpDesktop", ctypes.c_wchar_p),
        ("lpTitle", ctypes.c_char_p),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", ctypes.c_void_p),
        ("hStdOutput", ctypes.c_void_p),
        ("hStdError", ctypes.c_void_p),
    ]

class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", ctypes.c_void_p),
        ("bInheritHandle", ctypes.c_bool)
    ]

def Create_PIPE():
    saAttr = SECURITY_ATTRIBUTES()
    saAttr.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
    saAttr.bInheritHandle = True
    saAttr.lpSecurityDescriptor = None
    stdout_read_pipe = wintypes.HANDLE()
    stdout_write_pipe = wintypes.HANDLE()
    stderr_read_pipe = wintypes.HANDLE()
    stderr_write_pipe = wintypes.HANDLE()

    if not kernel32.CreatePipe(ctypes.byref(stdout_read_pipe), ctypes.byref(stdout_write_pipe), ctypes.byref(saAttr), 0):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel32.CreatePipe(ctypes.byref(stderr_read_pipe), ctypes.byref(stderr_write_pipe), ctypes.byref(saAttr), 0):
        raise ctypes.WinError(ctypes.get_last_error())
    
    if not kernel32.SetHandleInformation(stdout_read_pipe, 0x00000001, 0):
        raise Exception("failed to set handle information for stdout_read_pipe")
    
    if not kernel32.SetHandleInformation(stderr_read_pipe, 0x00000001, 0):
        raise Exception("failed to set handle information for stderr_read_pipe")
    
    return (stdout_read_pipe, stderr_read_pipe, stdout_write_pipe, stderr_write_pipe)

def Peek_PIPE(pipe):
    buffer = ctypes.create_string_buffer(1)
    lpBytesRead= wintypes.DWORD()
    lpTotalBytesAvail = wintypes.DWORD()
    lpBytesLeftThisMessage = wintypes.DWORD()
    psuccess = kernel32.PeekNamedPipe(pipe, buffer, ctypes.sizeof(buffer), ctypes.byref(lpBytesRead), ctypes.byref(lpTotalBytesAvail), ctypes.byref(lpBytesLeftThisMessage))
    if psuccess and buffer.raw != b'\x00':
        return True
    else:
        return False


def read_pipe(pipe):
    output = b''
    while True:
        buffer = ctypes.create_string_buffer(4096)
        read = ctypes.wintypes.DWORD()
        success = kernel32.ReadFile(pipe, buffer, ctypes.sizeof(buffer), ctypes.byref(read), None)
        if not success:
            error_code = ctypes.get_last_error()
            if error_code == 0:
                break
            else:
                raise ctypes.WinError(error_code)
        output += buffer.raw[:read.value]
        if read.value == 0:
            break
    return output.decode('utf-8')

def wait_for_process_and_pipe(handles):
    WAIT_OBJECT_0 = 0
    handle_array = (wintypes.HANDLE * len(handles))(*handles)
    while True:
        wait_result = kernel32.WaitForMultipleObjects(3, handle_array, False, 0xFFFFFFFF)
        if wait_result == WAIT_OBJECT_0:
            break
        elif wait_result > WAIT_OBJECT_0:
            if Peek_PIPE(handle_array[1]):
                output = read_pipe(handle_array[1])
                print("Output for the process created using CreateProcessAsUserW:\n %s"%(output))
                
            if Peek_PIPE(handle_array[2]):
                error = read_pipe(handle_array[2])
                print("Error for the process created using CreateProcessAsUserW:\n %s"%(error))


def get_current_user_token(hUserToken):
    bResult = False
    activeSessionId = INVALID_SESSION_ID
    hImpersonationToken = ctypes.c_void_p()
    pSessionInfo = ctypes.c_void_p()
    sessionCount = ctypes.c_int()
    
    if wtsapi32.WTSEnumerateSessionsW(WTS_CURRENT_SERVER_HANDLE, 0, 1, ctypes.byref(pSessionInfo), ctypes.byref(sessionCount)):
        arrayElementSize = ctypes.sizeof(WTS_SESSION_INFO)
        current = pSessionInfo.value

        for i in range(sessionCount.value):
            si = WTS_SESSION_INFO.from_address(current)
            current = ctypes.cast(current, ctypes.c_void_p).value + arrayElementSize

            if si.State == WTS_CONNECTSTATE_CLASS.WTSActive:
                activeSessionId = si.SessionID

        wtsapi32.WTSFreeMemory(pSessionInfo)

    if activeSessionId == INVALID_SESSION_ID:
        activeSessionId = kernel32.WTSGetActiveConsoleSessionId()

    if wtsapi32.WTSQueryUserToken(activeSessionId, ctypes.byref(hImpersonationToken)):
        bResult = advapi32.DuplicateTokenEx(hImpersonationToken, 0, None, SECURITY_IMPERSONATION_LEVEL.SecurityImpersonation, TOKEN_TYPE.TokenPrimary, ctypes.byref(hUserToken))

        kernel32.CloseHandle(hImpersonationToken)

    return bResult

def start_process_as_current_user(AppPath, cmdLine=None, workDir=None, visible=True, CreatePIPE_and_Redirect_OUTPUT=False):
    hUserToken = ctypes.c_void_p()
    StartInfo = STARTUPINFO()
    ProcInfo = PROCESS_INFORMATION()
    Ptr_Env_Vars = ctypes.c_void_p()
    StartInfo.cb = ctypes.sizeof(STARTUPINFO)
    bInheritHandles = False

    try:
        if not get_current_user_token(hUserToken):
            raise ProcessCreationException("GetSessionUserToken failed.")
        dwCreationFlags = CREATE_UNICODE_ENVIRONMENT | (CREATE_NEW_CONSOLE if visible else CREATE_NO_WINDOW)
        StartInfo.dwFlags = STARTF_USESHOWWINDOW
        StartInfo.wShowWindow = SW.SW_HIDE if not visible else SW.SW_SHOWNORMAL
        StartInfo.lpDesktop = u"winsta0\\default"

        if CreatePIPE_and_Redirect_OUTPUT:
            out_read, err_read, out_write, err_write = Create_PIPE()
            StartInfo.hStdOutput = out_write
            StartInfo.hStdError = err_write
            StartInfo.dwFlags = STARTF_USESTDHANDLES
            bInheritHandles = True

        if not userenv.CreateEnvironmentBlock(ctypes.byref(Ptr_Env_Vars), hUserToken, False):
            raise ProcessCreationException("CreateEnvironmentBlock failed.")

        if workDir:
            os.chdir(workDir)

        if not advapi32.CreateProcessAsUserW(hUserToken, AppPath, cmdLine, None, None, bInheritHandles, dwCreationFlags, Ptr_Env_Vars, workDir, ctypes.byref(StartInfo), ctypes.byref(ProcInfo)):
            raise ProcessCreationException("CreateProcessAsUser failed.  Error Code -" + str(ctypes.GetLastError()))
        
        if CreatePIPE_and_Redirect_OUTPUT:
            kernel32.CloseHandle(out_write)
            kernel32.CloseHandle(err_write)

            wait_for_process_and_pipe((ProcInfo.hProcess, out_read, err_read))

            kernel32.CloseHandle(out_read)
            kernel32.CloseHandle(err_read)
        else:
            kernel32.WaitForSingleObject(ProcInfo.hProcess, 0xFFFFFFFF)

        Exitcode = wintypes.DWORD()
        esuccess = kernel32.GetExitCodeProcess(ProcInfo.hProcess, ctypes.byref(Exitcode))
        if esuccess:
            print("Exit code for the process created using CreateProcessAsUserW: " + str(Exitcode.value))
        else:
            print("Failed to get return code for the process created using CreateProcessAsUserW")

    finally:
        kernel32.CloseHandle(hUserToken)
        if Ptr_Env_Vars:
            userenv.DestroyEnvironmentBlock(Ptr_Env_Vars)  
        kernel32.CloseHandle(ProcInfo.hThread)
        kernel32.CloseHandle(ProcInfo.hProcess)
    
    return True

#print(start_process_as_current_user(r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe', r'"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -WindowStyle Hidden -command "whoami /priv | Out-File -filepath C:\Users\coding\Desktop\testing.txt"'))

#print(start_process_as_current_user(r"C:\Program Files\Notepad++\notepad++.exe"))

#print(start_process_as_current_user(r'C:\Windows\System32\cmd.exe',r'"C:\Windows\System32\cmd.exe" /c "whoami /priv >> C:\Users\coding\Desktop\testing.txt"'))

#start_process_as_current_user(AppPath=r'cmd.exe',cmdLine=r'cmd.exe /c "call C:\Users\coding\Desktop\testing.bat"',workDir=r"C:\Windows\System32", visible=False, CreatePIPE_and_Redirect_OUTPUT=True)

#print(start_process_as_current_user(AppPath=r'cmd.exe', workDir=r"C:\Windows\System32"))
