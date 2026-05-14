import spacy

nlp_bc5 = spacy.load("en_ner_bc5cdr_md")
nlp_jnlpba = spacy.load("en_ner_jnlpba_md")

print("Models loaded successfully")