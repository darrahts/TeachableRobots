import threading

def fcn1():
    print("hello")

t1 = threading.Thread(target=fcn1)


t1.start()
print(threading.activeCount())
t1.join()

t1 = threading.Thread(target=fcn1)

t1.start()
print(threading.activeCount())
t1.join()

print(threading.activeCount())
