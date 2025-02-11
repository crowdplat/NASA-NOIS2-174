def generate_number_pairs(start, end, step, filename):
    with open(filename, 'w') as file:
        for i in range(start, end + 1, step):
            file.write(f"{i}, {i}\n")
            file.write(f"{i}, {i + 10}\n")

# Example usage
generate_number_pairs(10, 100000, 10, 'coordlist.txt')
