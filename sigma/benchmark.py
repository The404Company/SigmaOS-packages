import os
import sys
import time
import math
import random
import platform
import json
import datetime
import multiprocessing
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define colors
SUCCESS = Fore.GREEN
ERROR = Fore.RED
WARNING = Fore.YELLOW
INFO = Fore.CYAN
HEADER = Fore.YELLOW
COMMAND = Fore.GREEN
DESCRIPTION = Fore.WHITE
BENCHMARK_TITLE = Fore.YELLOW
BENCHMARK_SCORE = Fore.GREEN
BENCHMARK_TIME = Fore.CYAN
BENCHMARK_INFO = Fore.WHITE
BENCHMARK_GOOD = Fore.GREEN
BENCHMARK_AVG = Fore.YELLOW
BENCHMARK_BAD = Fore.RED

def get_sigmaos_root():
    """Returns the path to the SigmaOS root directory"""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(package_dir))

def save_benchmark_result(benchmark_type, score):
    """Save benchmark result to a history file"""
    results_dir = os.path.join(get_sigmaos_root(), "benchmark_results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    results_file = os.path.join(results_dir, "benchmark_history.json")
    
    # Load existing results or create new
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
        except:
            results = {"benchmarks": []}
    else:
        results = {"benchmarks": []}
    
    # Add new result
    results["benchmarks"].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": benchmark_type,
        "score": score,
        "system": platform.system(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    })
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=4)

def cpu_benchmark(iterations=1000000):
    """Run a CPU benchmark"""
    print(f"{BENCHMARK_TITLE}Running CPU Benchmark... ({iterations:,} iterations){Style.RESET_ALL}")
    
    start_time = time.time()
    
    # Prime number calculation
    def is_prime(n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True
    
    count = 0
    n = 2
    
    # Progress bar setup
    update_interval = max(1, iterations // 20)
    progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    for i in range(iterations):
        if is_prime(n):
            count += 1
        n += 1
        
        # Update progress bar
        if i % update_interval == 0:
            progress = i / iterations
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            spinner = progress_chars[i // update_interval % len(progress_chars)]
            sys.stdout.write(f"\r{spinner} Progress: [{bar}] {progress:.1%}")
            sys.stdout.flush()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    score = int(iterations / elapsed_time)
    
    # Clear progress line and print result
    sys.stdout.write("\r" + " " * 60 + "\r")
    print(f"{BENCHMARK_SCORE}CPU Score: {score:,}{Style.RESET_ALL}")
    print(f"{BENCHMARK_TIME}Time: {elapsed_time:.2f} seconds{Style.RESET_ALL}")
    print(f"{BENCHMARK_INFO}Found {count:,} prime numbers{Style.RESET_ALL}")
    
    # Save result
    save_benchmark_result("cpu", score)
    
    return score

def memory_benchmark(size=10000000):
    """Run a memory benchmark"""
    print(f"{BENCHMARK_TITLE}Running Memory Benchmark... ({size//1000000}M elements){Style.RESET_ALL}")
    
    try:
        start_time = time.time()
        
        # Array allocation and random access
        print(f"{BENCHMARK_INFO}Allocating memory...{Style.RESET_ALL}")
        data = [i for i in range(size)]
        
        # Random memory access
        print(f"{BENCHMARK_INFO}Testing random access...{Style.RESET_ALL}")
        sum_value = 0
        for _ in range(1000000):  # 1M random accesses
            index = random.randint(0, size - 1)
            sum_value += data[index]
        
        # Sequential memory access
        print(f"{BENCHMARK_INFO}Testing sequential access...{Style.RESET_ALL}")
        sum_seq = 0
        for i in range(0, size, 10):  # Step by 10 to not take too long
            sum_seq += data[i]
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        score = int(size / elapsed_time)
        
        print(f"{BENCHMARK_SCORE}Memory Score: {score:,}{Style.RESET_ALL}")
        print(f"{BENCHMARK_TIME}Time: {elapsed_time:.2f} seconds{Style.RESET_ALL}")
        
        # Save result
        save_benchmark_result("memory", score)
        
        return score
    
    except MemoryError:
        print(f"{ERROR}Memory allocation failed. Try a smaller size.{Style.RESET_ALL}")
        return 0

def disk_benchmark(size=100000000, chunk_size=1000000):
    """Run a disk benchmark"""
    print(f"{BENCHMARK_TITLE}Running Disk Benchmark... ({size//1000000}M bytes){Style.RESET_ALL}")
    
    benchmark_file = os.path.join(get_sigmaos_root(), "benchmark_temp.dat")
    
    try:
        # Write test
        print(f"{BENCHMARK_INFO}Testing write speed...{Style.RESET_ALL}")
        start_time = time.time()
        
        with open(benchmark_file, 'wb') as f:
            for i in range(0, size, chunk_size):
                f.write(os.urandom(chunk_size))  # Write random bytes
                # Show progress
                if i % (chunk_size * 10) == 0:
                    sys.stdout.write(f"\rWritten: {i/1000000:.1f}M / {size/1000000:.1f}M")
                    sys.stdout.flush()
        
        write_time = time.time() - start_time
        write_speed = size / write_time / 1000000  # MB/s
        
        sys.stdout.write("\r" + " " * 60 + "\r")
        print(f"{BENCHMARK_INFO}Write Speed: {write_speed:.2f} MB/s{Style.RESET_ALL}")
        
        # Read test
        print(f"{BENCHMARK_INFO}Testing read speed...{Style.RESET_ALL}")
        start_time = time.time()
        
        with open(benchmark_file, 'rb') as f:
            for i in range(0, size, chunk_size):
                data = f.read(chunk_size)
                # Show progress
                if i % (chunk_size * 10) == 0:
                    sys.stdout.write(f"\rRead: {i/1000000:.1f}M / {size/1000000:.1f}M")
                    sys.stdout.flush()
        
        read_time = time.time() - start_time
        read_speed = size / read_time / 1000000  # MB/s
        
        sys.stdout.write("\r" + " " * 60 + "\r")
        print(f"{BENCHMARK_INFO}Read Speed: {read_speed:.2f} MB/s{Style.RESET_ALL}")
        
        # Calculate score based on read and write speed
        score = int((read_speed + write_speed) * 100)
        
        print(f"{BENCHMARK_SCORE}Disk Score: {score:,}{Style.RESET_ALL}")
        print(f"{BENCHMARK_TIME}Total Time: {write_time + read_time:.2f} seconds{Style.RESET_ALL}")
        
        # Cleanup
        if os.path.exists(benchmark_file):
            os.remove(benchmark_file)
        
        # Save result
        save_benchmark_result("disk", score)
        
        return score
    
    except Exception as e:
        print(f"{ERROR}Disk benchmark failed: {e}{Style.RESET_ALL}")
        if os.path.exists(benchmark_file):
            try:
                os.remove(benchmark_file)
            except:
                pass
        return 0

def parallel_task(n):
    """A task to be executed in parallel for multi-core benchmark"""
    result = 0
    for i in range(n):
        result += math.sqrt(i)
    return result

def multicore_benchmark(processes=None, workload=1000000):
    """Run a multi-core CPU benchmark"""
    if processes is None:
        processes = multiprocessing.cpu_count()
    
    print(f"{BENCHMARK_TITLE}Running Multi-Core Benchmark... ({processes} cores){Style.RESET_ALL}")
    
    try:
        start_time = time.time()
        
        # Create a pool of worker processes
        with multiprocessing.Pool(processes) as pool:
            tasks = [workload] * processes
            results = pool.map(parallel_task, tasks)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Score is calculations per second adjusted by core count
        score = int((workload * processes) / elapsed_time)
        
        print(f"{BENCHMARK_SCORE}Multi-Core Score: {score:,}{Style.RESET_ALL}")
        print(f"{BENCHMARK_TIME}Time: {elapsed_time:.2f} seconds{Style.RESET_ALL}")
        
        # Save result
        save_benchmark_result("multicore", score)
        
        return score
    
    except Exception as e:
        print(f"{ERROR}Multi-core benchmark failed: {e}{Style.RESET_ALL}")
        return 0

def run_full_benchmark():
    """Run all benchmarks and calculate a system score"""
    print(f"{HEADER}Starting SigmaOS Full System Benchmark{Style.RESET_ALL}")
    print(f"{INFO}This will take several minutes to complete.{Style.RESET_ALL}")
    print(f"{INFO}System: {platform.system()} {platform.release()}{Style.RESET_ALL}")
    print(f"{INFO}Processor: {platform.processor()}{Style.RESET_ALL}")
    print(f"{INFO}Python: {platform.python_version()}{Style.RESET_ALL}")
    print()
    
    # Run benchmarks
    cpu_score = cpu_benchmark()
    print()
    
    memory_score = memory_benchmark()
    print()
    
    disk_score = disk_benchmark()
    print()
    
    multicore_score = multicore_benchmark()
    print()
    
    # Calculate overall score
    # This is a weighted average that prioritizes CPU and memory performance
    overall_score = int(cpu_score * 0.35 + memory_score * 0.25 + disk_score * 0.15 + multicore_score * 0.25)
    
    print(f"{HEADER}Benchmark Results:{Style.RESET_ALL}")
    print(f"{BENCHMARK_INFO}CPU Score:        {cpu_score:,}{Style.RESET_ALL}")
    print(f"{BENCHMARK_INFO}Memory Score:     {memory_score:,}{Style.RESET_ALL}")
    print(f"{BENCHMARK_INFO}Disk Score:       {disk_score:,}{Style.RESET_ALL}")
    print(f"{BENCHMARK_INFO}Multi-Core Score: {multicore_score:,}{Style.RESET_ALL}")
    print(f"{BENCHMARK_TITLE}Overall Score:    {overall_score:,}{Style.RESET_ALL}")
    
    # Categorize the system performance based on the overall score
    # These thresholds are arbitrary and would need calibration
    if overall_score > 1000000:
        rating = f"{BENCHMARK_GOOD}Excellent{Style.RESET_ALL}"
    elif overall_score > 500000:
        rating = f"{BENCHMARK_GOOD}Very Good{Style.RESET_ALL}"
    elif overall_score > 200000:
        rating = f"{BENCHMARK_AVG}Good{Style.RESET_ALL}"
    elif overall_score > 100000:
        rating = f"{BENCHMARK_AVG}Average{Style.RESET_ALL}"
    elif overall_score > 50000:
        rating = f"{BENCHMARK_BAD}Below Average{Style.RESET_ALL}"
    else:
        rating = f"{BENCHMARK_BAD}Poor{Style.RESET_ALL}"
    
    print(f"{BENCHMARK_INFO}System Rating:    {rating}{Style.RESET_ALL}")
    
    # Save overall result
    save_benchmark_result("overall", overall_score)
    
    return overall_score

def show_benchmark_history():
    """Show history of benchmark results"""
    results_dir = os.path.join(get_sigmaos_root(), "benchmark_results")
    results_file = os.path.join(results_dir, "benchmark_history.json")
    
    if not os.path.exists(results_file):
        print(f"{WARNING}No benchmark history found.{Style.RESET_ALL}")
        return
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        benchmarks = results.get("benchmarks", [])
        
        if not benchmarks:
            print(f"{WARNING}No benchmark history found.{Style.RESET_ALL}")
            return
        
        print(f"{HEADER}Benchmark History:{Style.RESET_ALL}")
        print(f"{COMMAND}{'Timestamp':<20} {'Type':<10} {'Score':<12} {'System'}{Style.RESET_ALL}")
        print("-" * 80)
        
        for benchmark in reversed(benchmarks):
            timestamp = benchmark.get("timestamp", "Unknown")
            btype = benchmark.get("type", "Unknown")
            score = benchmark.get("score", 0)
            system = benchmark.get("system", "Unknown")
            
            print(f"{BENCHMARK_TIME}{timestamp:<20}{Style.RESET_ALL} "
                  f"{BENCHMARK_INFO}{btype:<10}{Style.RESET_ALL} "
                  f"{BENCHMARK_SCORE}{score:<12,}{Style.RESET_ALL} "
                  f"{DESCRIPTION}{system}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{ERROR}Error loading benchmark history: {e}{Style.RESET_ALL}")

def show_help():
    """Show help for benchmark commands"""
    print(f"\n{HEADER}System Benchmark Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.benchmark{DESCRIPTION} - Run full system benchmark")
    print(f"{COMMAND}  sigma.benchmark cpu{DESCRIPTION} - Run CPU benchmark")
    print(f"{COMMAND}  sigma.benchmark memory{DESCRIPTION} - Run memory benchmark")
    print(f"{COMMAND}  sigma.benchmark disk{DESCRIPTION} - Run disk benchmark")
    print(f"{COMMAND}  sigma.benchmark multicore{DESCRIPTION} - Run multi-core benchmark")
    print(f"{COMMAND}  sigma.benchmark history{DESCRIPTION} - Show benchmark history")
    print()

def main():
    """Main entry point for benchmark module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Default behavior: run full benchmark
        run_full_benchmark()
        return
    
    command = args[0].lower()
    
    if command == "help":
        show_help()
    elif command == "cpu":
        cpu_benchmark()
    elif command == "memory":
        memory_benchmark()
    elif command == "disk":
        disk_benchmark()
    elif command == "multicore":
        multicore_benchmark()
    elif command == "full":
        run_full_benchmark()
    elif command == "history":
        show_benchmark_history()
    else:
        print(f"{ERROR}Unknown command: {command}{Style.RESET_ALL}")
        show_help()

if __name__ == "__main__":
    main() 