import csv
import os

IPC_DATA = [
    # Chapter XVI - Offences Affecting the Human Body
    {"Section": "299", "Description": "Culpable homicide. Whoever causes death by doing an act with the intention of causing death, or with the intention of causing such bodily injury as is likely to cause death, or with the knowledge that he is likely by such act to cause death, commits the offence of culpable homicide.", "Punishment": "Life Imprisonment or 10 years + Fine"},
    {"Section": "300", "Description": "Murder. Except in the cases hereinafter excepted, culpable homicide is murder, if the act by which the death is caused is done with the intention of causing death, or...", "Punishment": "Death or Life Imprisonment + Fine"},
    {"Section": "302", "Description": "Punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.", "Punishment": "Death or Life Imprisonment + Fine"},
    {"Section": "304", "Description": "Punishment for culpable homicide not amounting to murder.", "Punishment": "Life Imprisonment or 10 years + Fine"},
    {"Section": "304A", "Description": "Causing death by negligence. Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide.", "Punishment": "2 years + Fine"},
    {"Section": "304B", "Description": "Dowry death.", "Punishment": "Min 7 years to Life Imprisonment"},
    {"Section": "307", "Description": "Attempt to murder. Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder.", "Punishment": "10 years + Fine (Life if hurt caused)"},
    {"Section": "308", "Description": "Attempt to commit culpable homicide.", "Punishment": "3 years or Fine or Both (7 years if hurt caused)"},
    {"Section": "309", "Description": "Attempt to commit suicide.", "Punishment": "Simple Imprisonment up to 1 year or Fine or Both"},
    {"Section": "319", "Description": "Hurt. Whoever causes bodily pain, disease or infirmity to any person is said to cause hurt.", "Punishment": "N/A"},
    {"Section": "323", "Description": "Punishment for voluntarily causing hurt.", "Punishment": "1 year or 1000 INR or Both"},
    {"Section": "324", "Description": "Voluntarily causing hurt by dangerous weapons or means.", "Punishment": "3 years or Fine or Both"},
    {"Section": "325", "Description": "Punishment for voluntarily causing grievous hurt.", "Punishment": "7 years + Fine"},
    {"Section": "326", "Description": "Voluntarily causing grievous hurt by dangerous weapons or means.", "Punishment": "Life or 10 years + Fine"},
    {"Section": "351", "Description": "Assault. Whoever makes any gesture, or any preparation intending or knowing it to be likely that such gesture or preparation will cause any person present to apprehend that he who makes that gesture or preparation is about to use criminal force to that person, is said to commit an assault.", "Punishment": "3 months or 500 INR or Both"},
    {"Section": "354", "Description": "Assault or criminal force to woman with intent to outrage her modesty.", "Punishment": "Min 1 year to 5 years + Fine"},
    {"Section": "354A", "Description": "Sexual harassment and punishment for sexual harassment.", "Punishment": "3 years + Fine"},
    {"Section": "354B", "Description": "Assault or use of criminal force to woman with intent to disrobe.", "Punishment": "Min 3 years to 7 years + Fine"},
    {"Section": "354C", "Description": "Voyeurism.", "Punishment": "1-3 years + Fine (First conviction)"},
    {"Section": "354D", "Description": "Stalking.", "Punishment": "3 years + Fine (First conviction)"},
    {"Section": "363", "Description": "Punishment for kidnapping.", "Punishment": "7 years + Fine"},
    {"Section": "375", "Description": "Rape defined.", "Punishment": "N/A"},
    {"Section": "376", "Description": "Punishment for rape.", "Punishment": "Min 10 years to Life + Fine"},
    
    # Chapter XVII - Offences Against Property
    {"Section": "378", "Description": "Theft. Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.", "Punishment": "3 years or Fine or Both"},
    {"Section": "379", "Description": "Punishment for theft.", "Punishment": "3 years or Fine or Both"},
    {"Section": "383", "Description": "Extortion. Whoever intentionally puts any person in fear of any injury to that person, or to any other, and thereby dishonestly induces the person so put in fear to deliver to any person any property or valuable security...", "Punishment": "N/A"},
    {"Section": "384", "Description": "Punishment for extortion.", "Punishment": "3 years or Fine or Both"},
    {"Section": "390", "Description": "Robbery. In all robbery there is either theft or extortion.", "Punishment": "N/A"},
    {"Section": "392", "Description": "Punishment for robbery.", "Punishment": "10 years + Fine (14 years if on highway between sunset/sunrise)"},
    {"Section": "395", "Description": "Punishment for dacoity.", "Punishment": "Life or 10 years + Fine"},
    {"Section": "406", "Description": "Punishment for criminal breach of trust.", "Punishment": "3 years or Fine or Both"},
    {"Section": "415", "Description": "Cheating. Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person...", "Punishment": "N/A"},
    {"Section": "417", "Description": "Punishment for cheating.", "Punishment": "1 year or Fine or Both"},
    {"Section": "420", "Description": "Cheating and dishonestly inducing delivery of property.", "Punishment": "7 years + Fine"},
    {"Section": "425", "Description": "Mischief. Whoever with intent to cause, or knowing that he is likely to cause, wrongful loss or damage to the public or to any person, causes the destruction of any property...", "Punishment": "3 months or Fine or Both"},
    {"Section": "441", "Description": "Criminal trespass.", "Punishment": "N/A"},
    {"Section": "447", "Description": "Punishment for criminal trespass.", "Punishment": "3 months or 500 INR or Both"},
    {"Section": "448", "Description": "Punishment for house-trespass.", "Punishment": "1 year or 1000 INR or Both"},
    
    # Chapter XXA - Cruelty by Husband
    {"Section": "498A", "Description": "Husband or relative of husband of a woman subjecting her to cruelty.", "Punishment": "3 years + Fine"},
    
    # Chapter XXII - Criminal Intimidation, Insult/Annoyance
    {"Section": "503", "Description": "Criminal intimidation.", "Punishment": "2 years or Fine or Both"},
    {"Section": "506", "Description": "Punishment for criminal intimidation.", "Punishment": "2 years or Fine or Both (7 years if threat to cause death/grievous hurt)"},
    {"Section": "509", "Description": "Word, gesture or act intended to insult the modesty of a woman.", "Punishment": "3 years + Fine"},
]

OUTPUT_FILE = "backend/app/data/ipc/ipc.csv"

def seed_data():
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE))
        
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Section", "Description", "Punishment"])
        writer.writeheader()
        writer.writerows(IPC_DATA)
    
    print(f"✅ Seeding Complete: {len(IPC_DATA)} authentic IPC sections written to {OUTPUT_FILE}")

if __name__ == "__main__":
    seed_data()
