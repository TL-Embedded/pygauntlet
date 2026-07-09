from gauntlet import Gauntlet
import time


if __name__ == "__main__":
    
    with Gauntlet() as test:
        test.test("Sleep", lambda: time.sleep(1) == None)
        test.test_within("Voltage", lambda: 11.3, 10.0, 12.6, "V")
        test.test_equal("Serial", lambda: "1024" if time.sleep(0.25) == None else "", "1024")
        
