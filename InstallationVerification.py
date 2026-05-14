import spacy

nlp1 = spacy.load("en_ner_craft_md")
nlp2 = spacy.load("en_ner_jnlpba_md")
nlp3 = spacy.load("en_ner_bionlp13cg_md")

print("All models loaded successfully!")
