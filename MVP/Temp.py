import wmi

w = wmi.WMI()
    
process_watcher = w.Win32_Process.watch_for("creation")
while True:
    new_process = process_watcher()
    print(new_process)
