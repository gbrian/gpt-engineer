from gpt_engineer.core.scheduler import add_work

def print_on_schedule():
    print("on schedule")

add_work(print_on_schedule)