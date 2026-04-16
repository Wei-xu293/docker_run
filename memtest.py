# memtest.py
import sys
import time
import os

def get_rss_mb():
    """Return RSS (resident memory) in MB using /proc/self/statm."""
    with open('/proc/self/statm', 'r') as f:
        # fields: size, resident, share, text, lib, data, dt
        resident_pages = int(f.readline().split()[1])
        page_size = os.sysconf('SC_PAGE_SIZE')  # usually 4096
        return (resident_pages * page_size) / (1024 * 1024)

def main():
    if len(sys.argv) < 2:
        print("Usage: memtest.py <size_mb>")
        sys.exit(1)
    
    size_mb = int(sys.argv[1])
    # Allocate a list of bytearrays (each 1 MB)
    data = [bytearray(1024 * 1024) for _ in range(size_mb)]
    
    rss = get_rss_mb()
    print(f"RSS: {rss:.2f} MB")
    
    # Keep the memory alive for a moment (so docker stats can capture)
    time.sleep(5)

if __name__ == "__main__":
    main()