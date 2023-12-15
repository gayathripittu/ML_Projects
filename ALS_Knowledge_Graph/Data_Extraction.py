
import csv
from Bio import Entrez

def search_pubmed(queries, start_year, end_year):
    Entrez.email = "gayathrip556@gmail.com"  # Replace with your email
    records = []
    
    for query in queries:
        search_term = f'({query}) AND ("{start_year}"[Date - Publication] : "{end_year}"[Date - Publication])'
        
        handle = Entrez.esearch(db="pubmed", term=search_term, retmax=200)
        record = Entrez.read(handle)
        id_list = record["IdList"]
        
        if not id_list:
            print(f"No results found for the given search term: {query}")
            continue  

        for pmid in id_list:
            try:
                handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="xml")
                record = Entrez.read(handle)
                pub_year = record['PubmedArticle'][0]['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
                abstract = record['PubmedArticle'][0]['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', ['No abstract available.'])[0]
                records.append({'PMID': pmid, 'Abstract': abstract, 'PublishedYear': pub_year})
            except IndexError as e:
                print(f"Error retrieving details for PMID: {pmid}", e)
    
    return records

def save_records_to_csv(records, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:  
        fieldnames = ['PMID', 'Abstract', 'PublishedYear']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Only write the header if the file is new/empty
        if csvfile.tell() == 0:
            writer.writeheader()
        
        for record in records:
            writer.writerow(record)

# Example usage:
queries = [
    '("ALS" OR "Amyotrophic Lateral Sclerosis") AND ("SOD1" OR "C9orf72" OR "genetic mutation" OR "familial ALS") AND ("muscle weakness" OR "spasticity")'
]
start_year = '2013'
end_year = '2023'
csv_filename = 'Pubmed_abstracts.csv' # Results will be stored in this file

# Check if the CSV already exists and get existing PMIDs
existing_pmids = set()
try:
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        existing_pmids = {row['PMID'] for row in reader}
except FileNotFoundError:
    pass  # If the file doesn't exist, we'll create it later
except UnicodeDecodeError as e:
    print(f"Error decoding the existing CSV file: {e}")


# Search PubMed with the provided queries
retrieved_records = search_pubmed(queries, start_year, end_year)

# Filter out records that are already in the CSV
new_records = [record for record in retrieved_records if record['PMID'] not in existing_pmids]

# Save new records to CSV
save_records_to_csv(new_records, csv_filename)
print("Completed")


