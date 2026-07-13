from gauntlet import Gauntlet
import time


if __name__ == "__main__":
    
    with Gauntlet("", "results/dut") as test:
        test.test("Sleep", lambda: time.sleep(1) == None, equal = True)
        test.test("Voltage", lambda: 11.3, "V", minimum = 11.0)
        test.test("Serial", lambda: "1024" if time.sleep(0.25) == None else "", equal = "1024")
        
