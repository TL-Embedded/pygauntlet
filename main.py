from gauntlet import Gauntlet
import time


if __name__ == "__main__":
    
    with Gauntlet("test", "results/dut") as test:
        test.step("Sleep").method(lambda: time.sleep(1) == None).equals(True).run()
        test.step("Voltage").set(11, "V").within(11.0, 11.5).run()
        test.step("Serial").method(lambda: "1024" if time.sleep(0.25) == None else "").equals("1024").run()
        
