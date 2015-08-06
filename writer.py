from time import sleep

def logwrite(filename = "test.log", rg = 100):
    for i in range(rg):
        with open(filename, "a+") as f:
            f.write("test1 %d value #%d#\n"%(i, i%10))
            #print("line %d value #%d#"%(i, i%10))
        sleep(1)
        
if __name__ == "__main__":
    logwrite()
