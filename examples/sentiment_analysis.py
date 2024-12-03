import boto3

client = boto3.client('comprehend')

response = client.detect_sentiment(
    Text="""
To be fair, you have to have a very high IQ to understand Rick and Morty. 
The humour is extremely subtle, and without a solid grasp of theoretical 
physics most of the jokes will go over a typical viewer’s head. There’s 
also Rick’s nihilistic outlook, which is deftly woven into his 
characterisation- his personal philosophy draws heavily from Narodnaya 
Volya literature, for instance. The fans understand this stuff; they 
have the intellectual capacity to truly appreciate the depths of these 
jokes, to realise that they’re not just funny- they say something deep 
about LIFE. As a consequence people who dislike Rick & Morty truly ARE 
idiots- of course they wouldn’t appreciate, for instance, the humour in 
Rick’s existential catchphrase 'Wubba Lubba Dub Dub,' which itself is a 
cryptic reference to Turgenev’s Russian epic Fathers and Sons. I’m smirking 
right now just imagining one of those addlepated simpletons scratching
 their heads in confusion as Dan Harmon’s genius wit unfolds itself on 
 their television screens. What fools.. how I pity them 
""",
    LanguageCode='en'
)

print(response)