from runners.run import run_optimization

if __name__ == "__main__":
    input_file_name = "input.txt"
    output_file_name = "output.txt"
    days = 112
    max_iter = 10_000
    seed = 5

    run_optimization(input_file_name, output_file_name, days, max_iter, seed)
