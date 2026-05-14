Intelligent Medical Data Integration, Standardization and Search System

MediFusion AI is an AI-powered platform for cleaning, standardizing, integrating, and searching large-scale clinical trial data from multiple CSV and JSON sources. The system combines data engineering, natural language processing (NLP), fuzzy matching, and database technologies to transform raw and inconsistent healthcare datasets into a structured and searchable knowledge base.
#Technologies Used
Python
Regular Expressions (Regex)
Pandas
spaCy
TheFuzz
MongoDB
MySQL
REST APIs
Streamlit / Flask
#Overview

Clinical trial and healthcare datasets often contain inconsistent formats, duplicate entries, missing fields, and unstructured text. MediFusion AI automates the entire preprocessing and integration pipeline by:

Cleaning and standardizing investigator, sponsor, hospital, and site information
Extracting phone numbers, fax numbers, and email addresses using Regular Expressions
Normalizing doctor names and institutional data
Identifying drugs and therapeutic areas from scientific study titles
Expanding disease synonyms using medical dictionary APIs
Performing fuzzy matching to merge duplicate entities
Integrating processed data into MongoDB and MySQL
Enabling intelligent search across investigators, hospitals, drugs, and diseases
#Key Features
Data Cleaning and Standardization
Standardizes doctor names by adding consistent prefixes such as "Dr."
Separates names, phone numbers, fax numbers, and email addresses
Removes duplicates and fixes inconsistent formatting
Cleans and normalizes addresses and site information
Biomedical Entity Extraction
Extracts drug names and diseases from scientific study titles
Maps diseases to therapeutic areas
Generates synonym expansions for improved search accuracy
Intelligent Data Matching
Uses fuzzy string matching to merge similar records
Matches investigators and hospitals across multiple data sources
Data Integration
Processes both CSV and JSON datasets
Combines data from multiple batch files and directories
Stores structured data in MongoDB and MySQL
Search and Analytics
Supports keyword-based and ranked search
Enables retrieval by investigator, hospital, sponsor, drug, and disease
Generates summary analytics such as trials per year and site distributions
