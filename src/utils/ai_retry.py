import time
import random

def call_with_retry(func, *args, max_retries=3, initial_delay=2, **kwargs):
    """
    Executes a function with exponential backoff for handling 429 errors.
    """
    retries = 0
    delay = initial_delay
    
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_msg = str(e)
            # Check for 429 Resource Exhausted
            if "429" in err_msg or "Resource exhausted" in err_msg:
                retries += 1
                if retries >= max_retries:
                    raise e
                
                # Jittered exponential backoff
                sleep_time = delay + random.uniform(0, 1)
                print(f"Rate limit hit (429). Retrying in {sleep_time:.2f}s... (Attempt {retries}/{max_retries})")
                time.sleep(sleep_time)
                delay *= 2 # Double the delay for next time
            else:
                # Other errors should not be retried by this logic
                raise e
