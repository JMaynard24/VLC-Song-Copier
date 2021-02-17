import ctypes
import psutil


# -----------------------------------------------------------------------------


# DLLs needed
kernel32 = ctypes.windll.kernel32

# Process Permissions
PROCESS_QUERY_INFORMATION = (0x0400)
PROCESS_VM_OPERATION = (0x0008)
PROCESS_VM_READ = (0x0010)
PROCESS_VM_WRITE = (0x0020)

# Windows API's
OpenProcess = kernel32.OpenProcess
CloseHandle = kernel32.CloseHandle
GetLastError = kernel32.GetLastError
ReadProcessMemory = kernel32.ReadProcessMemory
WriteProcessMemory = kernel32.WriteProcessMemory


# -----------------------------------------------------------------------------


class ReadWriteMemory:

    def OpenProcess(self, myProcess):
        dwDesiredAccess = (PROCESS_QUERY_INFORMATION |
                           PROCESS_VM_OPERATION |
                           PROCESS_VM_READ |
                           PROCESS_VM_WRITE)
        bInheritHandle = False
        for Process in psutil.process_iter():
            if Process.name() == myProcess:
                dwProcessId = Process.pid

                hProcess = OpenProcess(dwDesiredAccess,
                                       bInheritHandle,
                                       dwProcessId
                                       )
                return hProcess
            elif Process.name is None:
                hProcess = None

    def CloseHandle(self, hProcess):
        CloseHandle(hObject)

    def GetLastError(self):
        GetLastError()
        return GetLastError()

    def PointerOffset(self, lpBaseAddress):
        pass

    def ReadProcessMemory(self, hProcess, lpBaseAddress):
        try:
            lpBaseAddress = lpBaseAddress
            ReadBuffer = ctypes.c_uint()
            lpBuffer = ctypes.byref(ReadBuffer)
            nSize = ctypes.sizeof(ReadBuffer)
            lpNumberOfBytesRead = ctypes.c_ulong(0)

            ReadProcessMemory(hProcess, lpBaseAddress, lpBuffer, nSize, lpNumberOfBytesRead)
            return ReadBuffer.value
        except(BufferError, ValueError, TypeError):
            CloseHandle
            e = 'Handle Closed, Error', hProcess, GetLastError()
            return e

    def WriteProcessMemory(self, hProcess, lpBaseAddress, Value):
        try:
            lpBaseAddress = lpBaseAddress
            Value = Value
            WriteBuffer = ctypes.c_uint(Value)
            lpBuffer = ctypes.byref(WriteBuffer)
            nSize = ctypes.sizeof(WriteBuffer)
            lpNumberOfBytesWritten = ctypes.c_ulong(0)

            WriteProcessMemory(
                hProcess,
                lpBaseAddress,
                lpBuffer,
                nSize,
                lpNumberOfBytesWritten
            )
        except(BufferError, ValueError, TypeError):
            CloseHandle
            e = 'Handle Closed, Error', hProcess, GetLastError()
            return e


# -----------------------------------------------------------------------------


rwm = ReadWriteMemory()
