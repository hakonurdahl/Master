import csv

def filter_municipalities(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        low_beta_municipalities = [(row['Municipality'], float(row['Beta'])) for row in reader if float(row['Beta']) < 3.5]
    
    return low_beta_municipalities

# Example usage
file_path = 'municipalities.csv'  # Replace with your actual file path
municipalities = filter_municipalities(file_path)
print("Municipalities with Beta lower than 3.5:")
for municipality, beta in municipalities:
    print(f"{municipality}: {beta}")
