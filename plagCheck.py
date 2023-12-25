import sys
import subprocess

if len(sys.argv) < 3:
    print("Usage: python [filepath]/plagCheck.py [platform] [contest code]")
    sys.exit()
platform, contest_code = sys.argv[1:]

if platform.lower() == "atcoder":
    subprocess.run(f"python3 atcoderMossReport.py {contest_code}", shell = True)
elif platform.lower() == "codechef":
    pass
else:
    print("Please provide correct platform: atcoder / codechef")
