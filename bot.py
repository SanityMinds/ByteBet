import discord
from discord.ext import commands, tasks
from discord import ui, app_commands, Interaction, ButtonStyle  
import json
import os
import asyncio
from datetime import datetime, timedelta
import logging
from discord.ui import View, Button, Select  
from discord import InteractionResponded
import secrets
from secrets import choice
from decimal import Decimal
import matplotlib.pyplot as plt
import numpy as np
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

BALANCE_FILE = 'user_balances.json'
COOLDOWN_FILE = 'work_cooldowns.json'
SLAVE_FILE = 'slaves.json'
NICKNAME_FILE = 'slave_nicknames.json'
MUZZLE_FILE = 'muzzle_data.json'
muzzled_slaves = {} 

def check_expired_inventory(server_id, user_id):
    current_time = datetime.now()
    user_items = user_inventory.get(server_id, {}).get(user_id, {})

    
    expirable_items = {
        "stealth_mode": timedelta(days=1),
        "double_earnings": timedelta(hours=6),
        "lucky_clover": timedelta(days=1)
    }

    
    for item, duration in expirable_items.items():
        if item in user_items:
            expiration_time = datetime.fromisoformat(user_items[item])
            if current_time >= expiration_time + duration:
                del user_items[item]

    
    save_inventory()

def get_server_balances(server_id: str):
    if server_id not in user_balances:
        user_balances[server_id] = {}
    return user_balances[server_id]

def load_muzzle_data():
    if os.path.exists(MUZZLE_FILE):
        with open(MUZZLE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_muzzle_data():
    with open(MUZZLE_FILE, 'w') as file:
        json.dump(muzzle_data, file, indent=4)

def load_slave_nicknames():
    if os.path.exists(NICKNAME_FILE):
        with open(NICKNAME_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_slave_nicknames():
    with open(NICKNAME_FILE, 'w') as file:
        json.dump(slave_nicknames, file, indent=4)

def load_slaves():
    if os.path.exists(SLAVE_FILE):
        with open(SLAVE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_slaves():
    with open(SLAVE_FILE, 'w') as file:
        json.dump(slave_data, file, indent=4)

slave_data = load_slaves()
slave_nicknames = load_slave_nicknames()
muzzle_data = load_muzzle_data()

def load_balances():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_balances():
    with open(BALANCE_FILE, 'w') as file:
        json.dump(user_balances, file, indent=4)

def load_cooldowns():
    if os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cooldowns():
    with open(COOLDOWN_FILE, 'w') as file:
        json.dump(work_cooldowns, file, indent=4)

def get_server_cooldowns(server_id: str):
    if server_id not in work_cooldowns:
        work_cooldowns[server_id] = {}
    return work_cooldowns[server_id]

def get_server_slaves(server_id: str):
    if server_id not in slave_data:
        slave_data[server_id] = {}
    return slave_data[server_id]

user_balances = load_balances()
work_cooldowns = load_cooldowns()

sentences = [
    "She sells seashells by the seashore, but the shells she sells aren't from the shore.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
    "The sixth sick sheikh's sixth sheep's sick.",
    "Fuzzy Wuzzy was a bear, Fuzzy Wuzzy had no hair, Fuzzy Wuzzy wasn't very fuzzy, was he?",
    "Red lorry, yellow lorry, red lorry, yellow lorry, red lorry, yellow lorry.",
    "The thirty-three thieves thought that they thrilled the throne throughout Thursday.",
    "Six slippery snails slid slowly seaward.",
    "A box of mixed biscuits, a mixed biscuit box.",
    "Can you can a can as a canner can can a can?",
    "If two witches were watching two watches, which witch would watch which watch?",
    "I saw Susie sitting in a shoeshine shop.",
    "Shy Shelly says she shall sew sheets.",
    "Fred fed Ted bread and Ted fed Fred bread.",
    "I wish to wash my Irish wristwatch.",
    "The great Greek grape growers grow great Greek grapes.",
    "A proper copper coffee pot.",
    "He threw three free throws.",
    "How can a clam cram in a clean cream can?",
    "Silly Sally swiftly shooed seven silly sheep.",
    "Six sleek swans swam swiftly southwards.",
    "The big black bug bit the big black bear, but the big black bear bit the big black bug back.",
    "Lesser leather never weathered wetter weather better.",
    "Give Papa a cup of proper coffee in a copper coffee cup.",
    "A tutor who tooted the flute tried to tutor two tooters to toot.",
    "Amidst the mists and coldest frosts, with stoutest wrists and loudest boasts.",
    "The two-twenty-two train tore through the tunnel.",
    "Betty Botter bought some butter but she said the butter's bitter.",
    "Swan swam over the sea, swim swan swim!",
    "The big black-backed bumblebee buzzed busily by the blooming bluebells.",
    "Six short slow shepherds stood silently in the snow.",
    "Twelve twins twirled twelve twigs.",
    "The biggest bug bit the boldest bear.",
    "I saw Esau kissing Kate.",
    "Peter Piper picked a peck of pickled peppers.",
    "Crisp crusts crackle crunchily.",
    "I saw a kitten eating chicken in the kitchen.",
    "Toy boat, toy boat, toy boat.",
    "A tree toad loved a she-toad.",
    "Fred fed Ted bread and Ted fed Fred bread.",
    "I wish to wish the wish you wish to wish.",
    "He threw three free throws.",
    "Great gray geese graze green grassy groves.",
    "Fresh fried fish, fish fresh fried, fried fish fresh, fish fried fresh.",
    "Friendly fleas and fireflies fiercely fly.",
    "Chester Cheetah chews a chunk of cheap cheddar cheese.",
    "Which wristwatches are Swiss wristwatches?",
    "I scream, you scream, we all scream for ice cream.",
    "Black back bat, black back bat's back.",
    "Tom threw Tim three thumbtacks.",
    "The great Greek grape growers grow great Greek grapes.",
    "Sheena leads, Sheila needs.",
    "Can you can a can as a canner can can a can?",
    "A proper copper coffee pot.",
    "The cat crept into the crypt, crapped, and crept out.",
    "Thin sticks, thick bricks.",
    "Fred fed Ted bread and Ted fed Fred bread.",
    "Great gray goats graze green grassy groves.",
    "Six slippery snails slid slowly seaward.",
    "Red lorry, yellow lorry.",
    "Unique New York, New York's unique.",
    "He threw three free throws.",
    "Six sleek swans swam swiftly southwards.",
    "The quick brown fox jumps over the lazy dog.",
    "A journey of a thousand miles begins with a single step.",
    "To be or not to be, that is the question.",
    "All that glitters is not gold.",
    "A picture is worth a thousand words.",
    "Actions speak louder than words.",
    "Birds of a feather flock together.",
    "Fortune favors the bold.",
    "The pen is mightier than the sword.",
    "The early bird catches the worm.",
    "Absence makes the heart grow fonder.",
    "A watched pot never boils.",
    "Beauty is in the eye of the beholder.",
    "Beggars can't be choosers.",
    "Better late than never.",
    "Blood is thicker than water.",
    "Don't count your chickens before they hatch.",
    "Every cloud has a silver lining.",
    "Good things come to those who wait.",
    "Haste makes waste.",
    "Honesty is the best policy.",
    "Hope for the best, prepare for the worst.",
    "If it ain't broke, don't fix it.",
    "If you can't beat them, join them.",
    "In the land of the blind, the one-eyed man is king.",
    "It takes two to tango.",
    "Kill two birds with one stone.",
    "Laughter is the best medicine.",
    "Leave no stone unturned.",
    "Let sleeping dogs lie.",
    "Like father, like son.",
    "Look before you leap.",
    "Necessity is the mother of invention.",
    "No pain, no gain.",
    "One good turn deserves another.",
    "One man's trash is another man's treasure.",
    "Out of sight, out of mind.",
    "People who live in glass houses shouldn't throw stones.",
    "Practice makes perfect.",
    "Rome wasn't built in a day.",
    "Seeing is believing.",
    "Slow and steady wins the race.",
    "The grass is always greener on the other side.",
    "The more things change, the more they stay the same.",
    "The squeaky wheel gets the grease.",
    "There's no place like home.",
    "Time heals all wounds.",
    "Too many cooks spoil the broth.",
    "Two heads are better than one.",
    "What goes around comes around.",
    "When in Rome, do as the Romans do.",
    "You can't judge a book by its cover.",
    "You can't make an omelet without breaking a few eggs.",
    "A bird in the hand is worth two in the bush.",
    "A chain is only as strong as its weakest link.",
    "A fool and his money are soon parted.",
    "A friend in need is a friend indeed.",
    "A penny for your thoughts.",
    "A rolling stone gathers no moss.",
    "A stitch in time saves nine.",
    "All is fair in love and war.",
    "All's well that ends well.",
    "An apple a day keeps the doctor away.",
    "As you sow, so shall you reap.",
    "Barking up the wrong tree.",
    "Bite the bullet.",
    "Burn the midnight oil.",
    "Caught between a rock and a hard place.",
    "Cross that bridge when you come to it.",
    "Curiosity killed the cat.",
    "Cut to the chase.",
    "Don't bite the hand that feeds you.",
    "Don't cry over spilled milk.",
    "Don't put all your eggs in one basket.",
    "Every dog has its day.",
    "Every rose has its thorn.",
    "Faint heart never won fair lady.",
    "Go the extra mile.",
    "Hindsight is 20/20.",
    "Ignorance is bliss.",
    "It's not rocket science.",
    "Jack of all trades, master of none.",
    "Keep your friends close, and your enemies closer.",
    "Knowledge is power.",
    "Lend an ear.",
    "Let the cat out of the bag.",
    "Money doesn't grow on trees.",
    "Necessity is the mother of invention.",
    "No use crying over spilt milk.",
    "Off the beaten path.",
    "On cloud nine.",
    "Once in a blue moon.",
    "Out of the frying pan, into the fire.",
    "Patience is a virtue.",
    "Piece of cake.",
    "Pulling your leg.",
    "Put your best foot forward.",
    "Read between the lines.",
    "Rising tide lifts all boats.",
    "Rome wasn't built in a day.",
    "Short end of the stick.",
    "Spill the beans.",
    "Take with a grain of salt.",
    "The ball is in your court.",
    "The best of both worlds.",
    "The devil is in the details.",
    "The elephant in the room.",
    "The early bird catches the worm.",
    "The whole nine yards.",
    "There's a method to my madness.",
    "Through thick and thin.",
    "Throw in the towel.",
    "Time flies when you're having fun.",
    "To each his own.",
    "Under the weather.",
    "Water under the bridge.",
    "What goes around comes around.",
    "You can't have your cake and eat it too.",
    "A leopard can't change its spots.",
    "A penny saved is a penny earned.",
    "A picture is worth a thousand words.",
    "Actions speak louder than words.",
    "All bark and no bite.",
    "At the drop of a hat.",
    "Back to the drawing board.",
    "Barking up the wrong tree.",
    "Beat around the bush.",
    "Between a rock and a hard place.",
    "Bite off more than you can chew.",
    "Break the ice.",
    "Burn the midnight oil.",
    "Burst your bubble.",
    "By the skin of your teeth.",
    "Caught between a rock and a hard place.",
    "Climbing up the walls.",
    "Close but no cigar.",
    "Cold feet.",
    "Come rain or shine.",
    "Crack the code.",
    "Cross that bridge when you come to it.",
    "Cry over spilt milk.",
    "Curiosity killed the cat.",
    "Cut to the chase.",
    "Don't count your chickens before they hatch.",
    "Don't give up your day job.",
    "Don't judge a book by its cover.",
    "Don't put all your eggs in one basket.",
    "Don't throw the baby out with the bathwater.",
    "Double-edged sword.",
    "Drawing a blank.",
    "Drive me up the wall.",
    "Dropping like flies.",
    "Eat your heart out.",
    "Every cloud has a silver lining.",
    "Every dog has its day.",
    "Face the music.",
    "Fair and square.",
    "Few and far between.",
    "Fish out of water.",
    "Flat as a pancake.",
    "Fly off the handle.",
    "Follow suit.",
    "Food for thought.",
    "Fools rush in where angels fear to tread.",
    "From rags to riches.",
    "Get a taste of your own medicine.",
    "Get out of hand.",
    "Get your act together.",
    "Give the benefit of the doubt.",
    "Go back to the drawing board.",
    "Go for broke.",
    "Go the extra mile.",
    "Good things come to those who wait.",
    "Green thumb.",
    "Hang in there.",
    "Haste makes waste.",
    "Have a change of heart.",
    "Hit the hay.",
    "Hit the nail on the head.",
    "Hit the sack.",
    "Hold your horses.",
    "Ignorance is bliss.",
    "In a nutshell.",
    "In the heat of the moment.",
    "It's a piece of cake.",
    "It's not rocket science.",
    "It takes two to tango.",
    "Jump on the bandwagon.",
    "Keep your chin up.",
    "Kill two birds with one stone.",
    "Knock on wood.",
    "Know the ropes.",
    "Leave no stone unturned.",
    "Let sleeping dogs lie.",
    "Let the cat out of the bag."
]

hard_sentences = [
    "Wheen i went to the store to by some bread iI saw a catt wearing a hat but then I realized it was just my imaginashun playng tricks on me, or waz it.?",
    "It seams like everytiime I try to explane my point, somone else jus comes along and twist my words into somethin I didn't even sayy, its so anoing.",
    "My neigghbor's dog barks at everythng, even the windd and now I can't tell if I'm hearing the windd or the dog anymoar its driving me craazy!",
    "She said she'd call me back in five minnutess but its been five ours now im not sure if i should call herr or just keep waiting or just givv up completly.",
    "The rain was pourngg down so hard I couldnnt see the road but i kept driveing hopingg the storm would pass befor i run out of gas.",
    "Everytimee I walkk past that old house i hear strange noizess but whenn i turn aroundd theres nothing there exept a creepy fealing I can't shakee.",
    "I tried to fix the leaky fossett myself but now the whhole sink is spraying water everywere and I thinkk I made it even worstt.",
    "The tv remotee has dissapeared agan and ivee looked everywher but I cant findd it and now im starting to thinkk it has a mind of its ownn or its just messingg with me.",
    "Whenn ever i go to the grocery store i alwais forget to buyy the one thing I actully needed and it's starting to drive me craazy i dont even know what to do anymoree.",
    "I foundd a spider in myy shoe this mornng and now i'm to afraid to wear shoes at all cuz what if there r moree spiders hiding in them ughh.",
    "I told my freindd i would help him move but now i'm regretng it becaus he has wayy more stuff then i expected and i think i might have injured my bakk.",
    "The traffic was soo bad this morning that i was latee for work and now myy boss is mad at me but I swear it wasn't my falt!",
    "I accidentlyy sent a text to the wrong person and now i'm desperatly trying to explainn the situtation before they get the wrong idea about me.",
    "I went to the park to relaxx but a group of loudd teenagrs showed up and ruined the peacefull atmospher and now i'm just annoyed and wishing i stayed homee.",
    "I tryed to bake a cake for the first timee but it came out burnt on the outsidee and raw on the insde and now I don't no what wentt rong.",
    "The cat nocked over the plant again and now there's dirt all over the floorr and i'm starting to wonder if this catt is out to get me.",
    "I forgot my umbrela at homee and now i'm stuck in the rainn getting soaked and wondering why i didnt checkk the weather befor i left.",
    "I keep loseingg my keys and every time i findd them i sweare i'll put them in the same place next timee but then I forget and lose them again its soo frustrateing.",
    "I thought i was being helpful by organzingg the pantry but now no one can find anything and i'm starting to think i made a big mistakee.",
    "The printer jammed agan and now there's paper stuck insde and I'm nott sure how to fix it without making the problem even worserr.",
    "I tried to fix the WiFi but now it's compleatly down and everyonne in the house is mad at me because they can't gett online, i feel like i ruined everything.",
    "The icecream truck drove by my house and now I can't stop thinkng about icecream but I don't have anyy at homee and the truckk is long gone.",
    "I triped over my own feet while walkng and now i'm trying to play it off like it didn't happen but i thinkk everyone saw me and now i'm embarasedd.",
    "The moviee I've been waiting to see for monthss is finaly out but now i can't find any one to go with me and I don't wantt to go alone but i might hav to.",
    "I was trying to write an importent email but then myy cat walked across the keybord and now I have to start all over againn ughh soo frustrateing.",
    "I went to the store to buy milk but I ended upp buying everything exept milk and now i have to go back to the store again, i can't beleive i forgot.",
    "I tryed to take a napp but then the construction outside got really loud and now I can't sleep and i'm just laying here tired and anoyed.",
    "I thought I lost my phonee but it was in my handd the whole time and now i feel so silly but at leastt i found it rite?",
    "I planned to go jogging this morning but then I realyzed i had no clean clothes and now I'm just sitting here eating brekfast insted.",
    "I was going to water the plants but then I forgot and now they look really droopy and i feel bad because they relyy on me to stayy alive.",
    "I tryed to assemble the new furniture by myself but now there's screws left over and I'm nott sure where they go and the wholle thingg seems wobbly.",
    "I spilled coffe on my shirrtt this morning and now i have to go through the wholle day withh a big stain and everyone keepss pointing it out.",
    "I made a to-do list to stay organized but now i can't findd the list and i can't rememberr whatt was on it so now i'm just lost.",
    "I got a new haircut but now i'm nott sure if i like it or if it was a mistake and i'm stuckk with it untill it grows back.",
    "I was trying to be healthy by making a salad but then i added too much dressingg and now it's all soggy and unappetizingg.",
    "I leftt myy car keys in the house but I didn't realize untill i locked the door behind me and now i'm stuckk outside waiting for someone to help.",
    "I was going to cook dinner but then I realyzed I forgot to defrost the meat and now i have to wait and dinner is going to be really latee.",
    "I tried to fix the squeeky door hinge but now it's even louderr and I thinkk I just made the problem worse, now everyonne's annoyed.",
    "I was trying to be on time for oncee but then i got stuck behind a slow driver and now i'm late agan, i guess i'll never be on time.",
    "I wanted to save some money so i skipped my morning coffeee but now i'm really tired and cranky and I'm not sure it was worthh it.",
    "I tryed to surprise my friend with a gift but then i realyzed I got the wrong thing and now i'm nott sure if i should give it to them or justt keep it.",
    "I was cleaningg the house but then I got distracted by an old photo album and now hourss have passed and i haven't cleaned anything.",
    "I thought I would be productive todayy but then I spent the wholle dayy watching TV and now I feel guilty for wasting so much time.",
    "I tried to fix the leaky roof but now there's water everywhere and I thinkk I made it worse and i'm nott sure what to do next.",
    "I was going to read a bookk but then I got stuck scrolling on my phone and now it's late and i'm too tired to read anythingg.",
    "I boughtt a plant to brighten up the room but now i'm worried I won't be able to keep it alivee because I alwais forget to water it.",
    "I thought I was being smart by waking up earlyy but now i'm just tired and grumpy and i still didn't get everythingg done that I needed to.",
    "I was going to go to the gym but then I couldn't find my shoes and by the time I did, I didn't feel like going anymoree.",
    "I tried to take a shortcut but then I got lostt and now it's taking even longer than if I had just gone the normal way.",
    "I was going to call my friend but then I realyzed I don't rememberr their number and now I'm just staringg at my phone feeling silly.",
    "I thought I was doing a good job at workk but then my boss pointed outt a mistake I made and now I'm worried they thinkk I'm not good enough.",
    "I was excited to wear my new outfit but then I spilled somethingg on it and now I have to change and I'm really bummed outt.",
    "I was going to make a healthy dinner but then I saw the pizza menu and now I'm waiting for delivery because I couldn't resist.",
    "I tried to organize my closett but now there's clothess everywhere and it's even more of a mess than it was before and i'm nott sure where to start.",
    "I went to the library to get some workk done but then I forgot my laptop at home and now i'm just sitting here with nothingg to do.",
    "I was trying to fix my bike but then I lostt one of the screws and now I can't finish the job and i'm stuck walkingg everywhere.",
    "I was going to the movies but thenn my car wouldn't start and now I'm stuckk at homee missing the movie I reallyy wanted to see.",
    "I tried to make a smoothie but then the blender broke and now there's fruit all over the kitchen and i have no smoothie to show for it.",
    "I wanted to make breakfast but then I realized I had no eggs and now I'm just staring at the empty fridge wondering whatt to eat.",
    "I planned a nice picnic but then it started to rain and now I'm stuckk insidee with a basket of food and no where to go.",
    "I was going to the gym but then I leftt my water bottle at homee and now I'm too thirsty to workout so i'm just sitting here doing nothingg.",
    "I was going to wash my car but then I realized I had no soap and now I'm just staring at the dirty car thinking maybe i'll do it another day.",
    "I tried to make a phone call but then I lostt signal and now I can't reach the person I needed to talk to and it's really importantt.",
    "I was planning to go shopping but then I realized I left my wallet at homee and now I'm just standing here feelingg foolish.",
    "I wanted to watch a movie but then the power went outt and now I'm just sitting in the dark wondering what to do with my timee.",
    "I was trying to write in my journal but thenn my pen ran out of ink and now I have half a page written and no way to finish my thoughts.",
    "I was going to cook a nice dinner but then I burned the rice and now I'm just staring at the pot wonderingg what went wrong.",
    "I planned to go to the park but then I got a flat tire on my bike and now I'm just sitting at homee staringg out the window.",
    "I tried to play a video game but then the controller died and now I'm just sitting here staring at the screen waitingg for it to charge.",
    "I wanted to go for a run but thenn it started rainingg and now I'm just sitting here in my workout clothes feelingg lazy.",
    "I was going to bake cookies but then I realized I had no sugar and now I'm just standing in the kitchen wonderingg what to do.",
    "I was going to the store but then I realized I leftt my grocery list at homee and now I'm just wanderingg the aisles not sure what to buy.",
    "I tried to fix the squeaky door but thenn I made it worse and now it's even louder and everyone in the house is annoyed.",
    "I was going to make a sandwich but thenn I realized I had no bread and now I'm just staring at the empty fridge feelingg disappointed.",
    "I planned to go hiking but thenn I couldn't find my boots and now I'm just sitting here wishingg I had been more organized.",
    "I wanted to read a book but then I got distractedd by my phone and now I'm just sitting here scrolling through social media wastingg time.",
    "I was going to call my mom but then I realized it was too late and now I'm just sitting here feelingg guilty for not calling earlier.",
    "I tried to fix the TV but then I lostt the remote and now I can't even turn it on and i'm just sitting here staringg at a blank screen.",
    "I was planning to go for a walk but thenn it started snowingg and now I'm just sitting here staringg out the window feeling lazy."
]

death_sentences = [
    "FuCk mY WiFe... AnD Fjhck HoW BaD mY LIfe hS beCuME!.!21!",
    "WhY DoEs EVeryTHING AlwaYs hAvE To GO wRONg!?!? i CAn't tAkE it AnYmOrE!!",
    "ThE WOrlD Is A dArK PlAcE, AnD I'm StUcK In IT!!! ThErE'S No WAy OUt...",
    "I hAtE EvErYTHinG ANd EvERyOne, wHy is My lIfe liKE ThIs???!!!",
    "SOMeonE PlEaSE EnD tHiS PaiN, I cAn'T Do ThIS AnYmOrE!!1!1",
    "LoVe Is A LIE, eVEryOnE BEtRaYs yOu EvEntUaLly, WhY Do i eVen TrY?!?!",
    "i'M SO SICk of ThiS SHit!!! WHeN WiLl It eND??!?!!",
    "WhaT's THe PoINt of EvEn TryING If It'S ALl GoINg TO faIL?!?!?",
    "No oNe CarEs ABouT ME, ThEy NEver DID... I HaTe ThIs LiFe!!!",
    "EvErYONE Is FAKE, I CaN't TRUSt aNYoNe!!! WhAt A JoKE My LIfe iS!!!",
    "I hAve hAD iT WiTh All tHIS BS!!! WhEn WIll iT StOP!?!?",
    "PlEasE JusT LeT Me Go... I'vE HaD EnOUgh!!! i CaN'T TaKE It AnYmORE!!!",
    "WhY Do I KeEp GeTtInG Hurt By ThE PEOplE I TrUSt?!?!!!",
    "ThErE'S nO HopE lEFT FoR Me... EvErYThINg IS FaLLIng aPart!!!",
    "i'M SO TIreD oF BeiNG ALoNe, No OnE UNdErSTaNds ME!!!",
    "GoD DamN It, I hAtE WhO I've BECOMe!!! ThIs IsN't wHaT i WAntED!!!",
    "NothINg MATTErs AnYmoRE, EvErYtHiNg Is USELEsS!!! WhY EvEn TrY?!",
    "WhEn WiLL ThE PaiN EnD?! I CAn't tAkE AnYMoRE Of ThiS!!!",
    "I'M DonE TrYinG, EvEryThiNg JuSt KeEPs gOInG WROng!!!",
    "My LiFe Is A JOKe, I'M A JoKE, WhY EveN BOtHEr!!!",
    "i cAN'T sTaND ThIs AnYMoRE, EvErY DaY Is THe SaME PaIN!!",
    "ThEY sAY ThInGS gET BETTeR, bUT THEy nEveR dO!! WhY LIE??!?!",
    "ThE DaRkNeSS iS CoNSumInG Me, I CaN't ESCApE!! HElP ME!!",
    "I'm So TIrED oF TrYinG tO MaKE THInGS BeTTEr, IT'S HoPElEsS!!!",
    "EvEry Day iS A StrUGgLe, WhY Do I BoThEr!?!!?!",
    "ThiS iS All My fAuLt, I DeSerVe ThIS, I ReAlLY Do!!!",
    "I'M So SiCk Of PreTENdinG EvErYthINg Is FInE, It's NoT!!!",
    "I'm DOnE... No oNe CArES AbOuT ME, NoT AnYMoRE!!!",
    "ThE VoICes In mY hEad WOn't sTop, MaKe ThEM StoP!! PleAse!!",
    "WhY CaN't i EvEr Be HaPpY?! It'S LIke ThE WoRld Is aGaInST Me!!!",
    "My LiFe Is A NEvER-EnDiNG NiGhtMarE, I JuSt wAnT To WAke Up!!!",
    "I HaTE MySELf, I'M SuCH a fAIluRe, nOtHIng EVEr GoEs RigHT!!!",
    "I JuST wAnt To DiSAppEaR, No oNe WoUlD EVen nOtIce!!!",
    "ThIS WoRLd Is ToO CrUel, I CaN't HaNdlE It AnYmORE!!!",
    "I'M TrAppED In A CaGe Of My OWn MiNd, WhErE Is ThE KEy!?!",
    "EvERyTHinG I ToUCH TuRns To ShIt, WhY BoThEr AnYmOrE?!?",
    "I FeEl LIke I'M sLoWly LoSIng My MiNd, I CaN't CoNtROl It!!!",
    "No OnE UnDerStAnDs Me, I feEl So ALonE In ThiS WoRld!!!",
    "i'M So TIreD oF LiVinG In CoNsTanT FeAR And DoUbT!!!",
    "I wIsH I CoULd JUst END It All, It WoUlD bE SO EaSy!!!",
    "ThE MoRE I tRy, ThE MoRE I FaIL, I cAn'T KEEp GoinG!!!",
    "I dOn'T KnoW HoW MuCh MoRE oF ThIS I cAn TaKe, I'm At My LimIt!!!",
    "EvERyOnE LeAvEs Me, Why Is It ALwaYs Me?!! WhAt dID I dO!?!!",
    "I'M so SICk oF ThIs EmPty FeELinG, It'S eAtInG ME ALiVe!!!",
    "ThE WoRLD Is A DaRk PlaCE, And I'M SuFfocAtInG In It!!!",
    "WhY Do I EvEr GeT My HoPeS Up? It AlWaYs LeADs To DiSaPpOintMenT!!!",
    "I'm JusT So TiReD oF AlL ThE PaIn, It NeVer EndS!!!",
    "No ONe cAres AbOuT My PaIn, ThEy OnLy CaRe AbOuT ThEirS!!!",
    "I'm SCrEamiNG InsIDe, BuT No OnE Can HeAr Me, It'S So LoNely!!!",
    "ThE MoRE I tRY To ESCApe, ThE DeEpEr I SiNk InTo ThE DarKnESs!!!",
    "I'M So TIreD Of LiFE's CruEL JoKes, WhEN WiLl It StOp!?!?",
    "ThErE's NoWHeRe LeFt To Go, NoWHeRe To HIdE, I'm StUck HeRe!!!",
    "I'm WaITinG FoR ThE PaIn To StOP, BuT It NeVEr DoEs, It NeVEr EnDs!!!",
    "WhY Am I SuCH A MeSs? WhY cAn'T I GeT It ToGeThEr!?!?",
    "I DoN't KnoW HoW MuCh MoRE I CaN TaKE, I'm ABouT To BrEaK!!!",
    "ThE DaRKNeSs IS ALWaYS ThErE, No MATter WhAT I Do, It NeVEr LEaVes!!!",
    "I'M SLoWLy DrOWnINg In My OWn MiSery, AnD ThEre'S No OnE To SaVE Me!!!",
    "EvERyTHing Is FaLLInG APArt, I cAn'T HoLD It TogEThEr AnYmORE!!!",
    "ThE WoRld Is CoLLaPSIng ARounD Me, AnD I'M TrAPpeD UnDer ThE RubBLe!!!",
    "I CaN'T KeeP DoInG ThiS, ThE PaIN Is ToO MuCH, I NeeD It To END!!!",
    "EvEryONE Is LeAvIng Me, I'M So ALone, So CoLD, So BrOKEn!!!",
    "ThErE'S No HopE LeFT FoR Me, EvEryTHInG Is LOST!!!",
    "I'm WaITinG FoR ThE EnD, BuT It NeVEr ComEs, I'm TRappED!!!",
    "ThE MoRE I TrY To FInd PEace, ThE MoRE ChAOS I FiNd!!!",
    "I JuSt Want TO Be HaPPy, BuT It SEemS LiKE THaT'S iMPosSiBLE FoR Me!!!",
    "WhY DoES EvERYtHinG Go WroNG? I'm So SICk OF ThiS!!!",
    "I'M So TIreD Of ThE LiES, ThE DeCEit, ThE PAIN!!! WhY DoEs It NEVer EnD?!?",
    "ThErE'S No REasON To KeEp GoINg, It'S All HoPElesS AnYWays!!!",
    "I'm StaNdING On ThE EdgE, LooKing DoWn, And I JuSt WanT To LET GO!!!",
    "ThE PaIN Is EATIng Me ALive, I CaN't StAND It AnYmore!!!",
    "WhY Am I AlWayS ThE One LefT SuFfErIng? WhAt Did I Do To DeSErvE ThiS!?!?",
    "I'm So TIrED Of BeiNG So TIRed, I JuSt WaNt To ReST FoReVEr!!!",
    "ThErE'S No HopE LeFT, EvEryThINg Is FaLLIng AParT, And I CaN't StOP It!!!",
    "ThE DaRKNeSs Is CoNSuMinG Me, ThE LiGHt Is GoNE, I aM LOsT!!!",
    "I JuST WaNT To EnD It AlL, To BrING ThiS PaiN To A CoLD, HaRD StOP!!!",
    "ThE MoRE I TrY To FIGht, ThE MoRE I FALl, I CaN't WiN!!!",
    "I'm So TIreD Of ThIS SHiT, WhEn Will It Be OvER?!? WhEN?!?",
    "WhY DoES EvERyONe ALwaYS LeaVE? I'm SO SiCK Of BeiNG ALone!!!",
    "I CaN't FiND ThE ENErgy To CarE AnYmOrE, I'm JusT So DonE!!!",
    "ThE MoRe I TrY To FiX ThInGs, ThE MoRE I FucK TheM Up!!!",
    "WhY Am I StIll HerE? WhAt'S ThE PoINt? I'm So TiReD!!!",
    "EvEry DAy Is ThE SaME, JuSt MoRE PAIN, MoRE DisAPpoinTmEnt!!!",
    "ThE LonGer I StAY, ThE MoRE I BrEAk, I CaN't HanDLe ThIS AnYmOrE!!!",
    "I JuSt WaNt To FAdE AwAy, To DiSapPEaR AnD NevER BE FouNd!!!",
    "ThE MoRE I LoVe, ThE MoRE I GeT HuRT, I JuST CaN't TaKE IT!!!",
    "I'M TrIEd Of WAitINg FoR ThInGs To GeT BeTTer, ThEY NevER DO!!!",
    "EvEryTHinG I Do TuRns To SHiT, WhAt'S ThE PoINt Of EvEN TrYiNg?!?",
    "ThE MoRE I TrY To LiVE, ThE MoRE I DiE, I CaN'T Do ThIS AnYMoRE!!!",
    "I HaTe WhO I'Ve BECOMe, I HaTE WHAt My LIfe IS, I HaTe EvERyTHinG!!!",
    "WhY Do I FeEl LiKE ThIS? WhY CaN'T I Be NoRmAl!?!? WhY Me?!?",
    "I'M So TIreD Of ThE StrUgGLE, ThE NeVEr-ENdIng PaiN, ThE DeSpAIr!!!",
    "ThErE'S No FuTuRE For Me, It'S All JUSt DaRkNeSS, NoThINg ElsE!!!",
    "I WaNt To SCREAM, To BrEaK FreE, But I'M TrAppEd, ThErE'S No EsCaPE!!!",
    "EvEryTHinG I ToUCH TuRns To SHiT, WhAt Did I Do To DeSErvE ThIS!?!?",
    "ThE MoRE I WaNT To Be HaPpY, ThE MoRE MisErY I FinD!!!",
    "I CaN'T TaKE AnYmORE, I'M At My BReAKIng PoinT, SoMEonE HeLP Me!!!",
    "I'M So SiCk Of ThIS PaIN, WhY WoN't It Go AwAY? I JuSt WaNT It To EnD!!!",
    "EvERyONE LiEs, EvERyONE BeTRayS, I CaN'T TruST AnYoNe, I HaTE ThIS!!!",
    "ThE MoRe I LoVe, ThE MoRe I GeT HuRT, I JuST CaN't TaKE It AnYMoRE!!!",
    "I'M TrIEd Of WAitINg FoR ThInGs To GeT BeTTer, ThEY NevER DO!!!",
    "EvEryTHinG I Do TuRns To SHiT, WhAt'S ThE PoINt Of EvEN TrYiNg?!?",
    "ThE MoRE I TrY To LiVE, ThE MoRE I DiE, I CaN'T Do ThIS AnYMoRE!!!",
    "I HaTe WhO I'Ve BECOMe, I HaTE WHAt My LIfe IS, I HaTe EvERyTHinG!!!",
    "WhY Do I FeEl LiKE ThIS? WhY CaN'T I Be NoRmAl!?!? WhY Me?!?",
    "I'M So TIreD Of ThE StrUgGLE, ThE NeVEr-ENdIng PaiN, ThE DeSpAIr!!!",
    "ThErE'S No FuTuRE For Me, It'S All JUSt DaRkNeSS, NoThINg ElsE!!!",
    "I WaNt To SCREAM, To BrEaK FreE, But I'M TrAppEd, ThErE'S No EsCaPE!!!",
    "EvEryTHinG I ToUCH TuRns To SHiT, WhAt Did I Do To DeSErvE ThIS!?!?",
    "ThE MoRE I WaNT To Be HaPpY, ThE MoRE MisErY I FinD!!!",
    "I CaN'T TaKE AnYmORE, I'M At My BReAKIng PoinT, SoMEonE HeLP Me!!!",
    "I'M So SiCk Of ThIS PaIN, WhY WoN't It Go AwAY? I JuSt WaNT It To EnD!!!",
    "EvERyONE LiEs, EvERyONE BeTRayS, I CaN'T TruST AnYoNe, I HaTE ThIS!!!",
    "ThE MoRe I TrY To Be StRoNg, ThE WeaKer I FeEl!!! WhY Is ThiS HaPPeniNG?!?",
    "I CaN'T KeeP GoINg, I'M So ExHAusTeD, So DoNe, I JuST WaNT To QUit!!!",
    "EvEryOnE sAYs It'S GoInG To GeT BeTTer, BuT It NeVEr DoES!!!",
    "I'M TrAppEd In My OWn HeAD, I CaN'T GeT OuT, I CaN'T EsCApE!!!",
    "ThE MoRE I ThInK AbOuT My LifE, ThE MoRE HoPlEsS I FeEl!!!",
    "I'M LoSt, I'M BrOkEn, AnD ThErE'S No OnE WhO CaReS!!!",
    "WhY DoEs ThE PaIn NeVeR End? WhAt DiD I Do To DeSErvE ThIS!?!?",
    "I'M So SiCk Of ThIS WoRLD, So TiReD Of ThE PeOpLe In It!!!",
    "EvERyTHinG I OnCE LoVed Is GoNe, All ThAt'S LeFt Is MisEry!!!",
    "ThE MoRE I TrY To LiVE, ThE MoRE I ReAlize I DoN'T BelOng HeRE!!!",
    "I'M TiReD Of CrYiNG, TiReD Of HuRtiNg, TiReD Of EvErYThINg!!!",
    "ThErE'S No PlAcE For Me In ThIs WoRLD, I'm AlOnE!!!",
    "ThE MoRE I ReACH Out, ThE MoRE I GeT ReJeCTEd!!!",
    "I'M So SiCk Of BeIng A BuRDeN To EvErYOnE ArOuNd Me!!!",
    "ThE PaIn Is OvERwHeLmIng, I CaN't CoPe, I CaN't BrEAtHe!!!",
    "WhY Is EvErYOnE So MeAn? So CruEl? I HaTE ThiS WoRLD!!!",
    "ThE MoRE I TrY To HoLD On, ThE MoRE I WaNT To LeT Go!!!",
    "I'M TrAppED In A NeVer-EnDiNg CyCLE Of PAin AnD MiSeRy!!!",
    "EvEryThiNg Is MeSSed Up, AnD I CaN't Do AnYThIng AbOuT It!!!"
]


WORK_COOLDOWN = 2

ongoing_work_sessions = {}

@bot.event
async def on_ready():
    logger.info(f'🎉 Logged in as {bot.user.name}')
    pay_slaves.start()
    load_cooldowns()
    announce_lottery_winner.start()
    update_stock_prices_task.start()
    try:
        logger.info(f"⚙️ Attempting to sync commands...")
        synced = await bot.tree.sync()
        logger.info(f"✅ Successfully synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name='balance', description='💰 Check your current balance')
async def balance(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)

    formatted_balance = f"{balance:,}"

    embed = discord.Embed(
        title="Your Balance",
        description=f"💸 You currently have **{formatted_balance} coins**.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='coin_flip', description='🎲 Flip a coin to double your bet')
@app_commands.describe(amount='The amount you want to bet')
async def coin_flip(interaction: discord.Interaction, amount: int):
    server_id = str(interaction.guild.id)  # Get the server ID
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)  # Default balance of 500

    if balance < -100:
        await interaction.response.send_message("🚫 You cannot bet because you are in debt.", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("⚠️ You must bet a positive amount.", ephemeral=True)
        return

    max_bet = int(balance * 1.5)

    if max_bet <= 0:
        await interaction.response.send_message("🚫 You cannot bet because your current balance is too low.", ephemeral=True)
        return

    if amount > max_bet:
        await interaction.response.send_message(f"🚫 You cannot bet more than 50% above your current balance. The maximum you can bet is **{max_bet} coins**.", ephemeral=True)
        return

    await ask_for_choice(interaction, amount)


async def ask_for_choice(interaction: discord.Interaction, amount: int):
    user_id = str(interaction.user.id)
    logger.info(f"Asking user {user_id} to choose heads or tails.")

    view = View()

    select = Select(
        placeholder="Choose heads or tails...",
        options=[
            discord.SelectOption(label="Heads", value="heads", emoji="🪙"),
            discord.SelectOption(label="Tails", value="tails", emoji="🪙")
        ]
    )

    async def select_callback(select_interaction: discord.Interaction):
        user_choice = select.values[0]
        logger.info(f"User {user_id} selected {user_choice}.")
        await proceed_with_bet(select_interaction, amount, user_choice)

    select.callback = select_callback
    view.add_item(select)

    await interaction.response.send_message(content="Please choose heads or tails:", view=view)


async def proceed_with_bet(interaction: discord.Interaction, amount: int, user_choice: str):
    server_id = str(interaction.guild.id)  
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)  

    result = secrets.choice(["heads", "tails"])

    if result == user_choice:
        balance += amount
        response = f"🎉 Congratulations! You won **{amount} coins** by choosing **{user_choice}**. Your new balance is **{balance} coins**."
    else:
        balance -= amount
        response = f"💔 Sorry, you lost **{amount} coins**. The coin landed on **{result}**. Your new balance is **{balance} coins**."

    server_balances[user_id] = balance
    save_balances()  

    embed = discord.Embed(
        title="Coin Flip Result",
        description=response,
        color=discord.Color.blue() if result == user_choice else discord.Color.red()
    )

    try:
        await interaction.response.edit_message(content=None, embed=embed, view=None)
    except Exception as e:
        logger.error(f"Failed to send message to user {user_id}: {e}")

def generate_text_image(text, width=1024, height=256):
    # Create a blank figure
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.set_facecolor((54/255, 57/255, 63/255))  

    
    ax.axis('off')

    ax.text(0.5, 0.5, text, color="white", fontsize=60, ha='center', va='center', wrap=True)

    plt.tight_layout(pad=0)

    image_bytes = io.BytesIO()
    plt.savefig(image_bytes, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    image_bytes.seek(0)

    plt.close(fig)

    return image_bytes

@bot.tree.command(name='work', description='💼 Work to earn coins. Can be used every 2 hours.')
@app_commands.describe(difficulty='Choose the difficulty: easy (default), hard, death sentence')
@app_commands.choices(difficulty=[
    app_commands.Choice(name="Easy", value="easy"),
    app_commands.Choice(name="Hard", value="hard"),
    app_commands.Choice(name="Death Sentence", value="death sentence")
])
async def work(interaction: discord.Interaction, difficulty: str = "easy"):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    logger.info(f"User {user_id} initiated work command with difficulty '{difficulty}'.")

    if user_id in ongoing_work_sessions:
        await interaction.response.send_message(
            "⚠️ You are already in a work session. Please complete your current session before starting a new one.",
            ephemeral=True
        )
        return

    last_work_time = work_cooldowns.get(server_id, {}).get(user_id)
    if last_work_time:
        last_work_time = datetime.fromisoformat(last_work_time)
        if datetime.now() < last_work_time + timedelta(hours=WORK_COOLDOWN):
            remaining_time = (last_work_time + timedelta(hours=WORK_COOLDOWN)) - datetime.now()
            await interaction.response.send_message(
                f"⏳ You need to wait **{remaining_time.seconds // 3600} hours and {(remaining_time.seconds % 3600) // 60} minutes** before working again."
            )
            logger.info(f"User {user_id} is on cooldown.")
            return

    if difficulty == "hard":
        selected_sentences = hard_sentences
        reward_per_sentence = 100
    elif difficulty == "death sentence":
        selected_sentences = death_sentences
        reward_per_sentence = 200
    else:
        selected_sentences = sentences
        reward_per_sentence = 50

    embed = discord.Embed(
        title="Work",
        description="You are about to start your shift. 🕒 The more messages you type within 1 minute, the more money you make.",
        color=discord.Color.blue()
    )
    start_button = discord.ui.Button(label="Start Work", style=discord.ButtonStyle.green, emoji="✅")
    cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")

    async def start_work_callback(interaction: discord.Interaction):
        if user_id in ongoing_work_sessions:
            await interaction.response.send_message(
                "⚠️ You are already in a work session. Please complete your current session before starting a new one.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        session = {
            'total_earned': 0,
            'reward_per_sentence': reward_per_sentence,
            'end_time': datetime.now() + timedelta(minutes=1),
            'current_sentence': random.choice(selected_sentences),
            'selected_sentences': selected_sentences  
        }
        ongoing_work_sessions[user_id] = session

        image_bytes = generate_text_image(session['current_sentence'])

        file = discord.File(image_bytes, filename="sentence.png")
        await interaction.followup.send(
            f"✍️ {interaction.user.mention}, type the sentence shown in the image below:",
            file=file
        )
        logger.info(f"Work session started for user {user_id} with difficulty '{difficulty}'. First sentence: {session['current_sentence']}")

        if server_id not in work_cooldowns:
            work_cooldowns[server_id] = {}

        work_cooldowns[server_id][user_id] = datetime.now().isoformat()
        save_cooldowns()  

    async def cancel_callback(interaction: discord.Interaction):
        if user_id in ongoing_work_sessions:
            del ongoing_work_sessions[user_id]
        await interaction.response.send_message("❌ Work session cancelled.", ephemeral=True)
        logger.info(f"User {user_id} cancelled their work session.")

    start_button.callback = start_work_callback
    cancel_button.callback = cancel_callback

    view = discord.ui.View()
    view.add_item(start_button)
    view.add_item(cancel_button)

    await interaction.response.send_message(embed=embed, view=view)
    logger.info(f"Work embed sent to user {user_id}.")


@bot.event
async def on_message(message):
    if not message.author.bot:
        user_id = str(message.author.id)
        server_id = str(message.guild.id)

        if server_id not in work_cooldowns:
            work_cooldowns[server_id] = {}

        if user_id in ongoing_work_sessions:
            session = ongoing_work_sessions[user_id]

            if datetime.now() > session['end_time']:
                earned = session['total_earned']

                if "double_earnings" in user_inventory[server_id].get(user_id, {}):
                    earned *= 2 

                server_balances = get_server_balances(server_id)
                balance = server_balances.get(user_id, 500) + earned
                server_balances[user_id] = balance
                save_balances()

                del ongoing_work_sessions[user_id]
                await message.channel.send(f"⏰ {message.author.mention} Your work session is over! You earned **{earned} coins**. Your new balance is **{balance:,} coins**.")

                work_cooldowns[server_id][user_id] = datetime.now().isoformat()
                save_cooldowns()  
                return

            def normalize(text):
                return ' '.join(text.lower().strip().split())

            normalized_message = normalize(message.content)
            normalized_sentence = normalize(session['current_sentence'])

            if normalized_message == normalized_sentence:
                session['total_earned'] += session['reward_per_sentence']
                session['current_sentence'] = random.choice(session['selected_sentences'])  

                image_bytes = generate_text_image(session['current_sentence'])

                file = discord.File(image_bytes, filename="sentence.png")
                await message.channel.send(
                    f"✅ {message.author.mention} Correct! You earned **{session['reward_per_sentence']} coins**. Type the following:",
                    file=file
                )
            else:
                image_bytes = generate_text_image(session['current_sentence'])
                file = discord.File(image_bytes, filename="sentence.png")
                await message.channel.send(
                    f"❌ {message.author.mention} Message incorrect. Try again:",
                    file=file
                )

        if user_id in muzzle_data:
            keyword = muzzle_data[user_id]
            if keyword.lower() in message.content.lower():
                try:
                    await message.delete()
                    await message.author.send(f"🔇 Your message was deleted because it contained the forbidden keyword '{keyword}'.")
                except discord.Forbidden:
                    logger.warning(f"Failed to delete message from {message.author} due to lack of permissions.")
                except discord.HTTPException as e:
                    logger.error(f"Failed to delete message from {message.author}: {e}")

    await bot.process_commands(message) 

@bot.tree.command(name='blackjack', description='🎰 Play a game of blackjack!')
@app_commands.describe(amount='The amount you want to bet')
async def blackjack(interaction: discord.Interaction, amount: int):
    server_id = str(interaction.guild.id)  
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)  #

    if balance < -100:
        await interaction.response.send_message("🚫 You cannot bet because you are in debt.", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("⚠️ You must bet a positive amount.", ephemeral=True)
        return

    max_bet = int(balance * 1.5)

    if max_bet <= 0:
        await interaction.response.send_message("🚫 You cannot bet because your current balance is too low.", ephemeral=True)
        return

    if amount > max_bet:
        await interaction.response.send_message(f"🚫 You cannot bet more than 50% above your current balance. The maximum you can bet is **{max_bet} coins**.", ephemeral=True)
        return

    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    if hand_value(player_hand) == 21:
        if hand_value(dealer_hand) == 21:
            await end_game(interaction, user_id, amount, player_hand, dealer_hand, "push_blackjack")
        else:
            await end_game(interaction, user_id, amount, player_hand, dealer_hand, "blackjack")
        return

    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.green())
    embed.add_field(name="Your Hand", value=f"{hand_display(player_hand)} (Total: **{hand_value(player_hand)}**)", inline=False)
    embed.add_field(name="Dealer's Hand", value=f"{hand_display([dealer_hand[0]])}, 🂠\n(Value of visible card: **{card_value_description(dealer_hand[0])}**)", inline=False)
    embed.set_footer(text=f"💰 Your current bet: {amount} coins")

    view = View()

    hit_button = Button(label="Hit", style=discord.ButtonStyle.primary, emoji="✋")
    async def hit_callback(interaction: discord.Interaction):
        player_hand.append(draw_card())

        if hand_value(player_hand) > 21:
            await end_game(interaction, user_id, amount, player_hand, dealer_hand, "bust")
        else:
            await update_embed(interaction, player_hand, dealer_hand, amount, view)

    hit_button.callback = hit_callback

    stand_button = Button(label="Stand", style=discord.ButtonStyle.success, emoji="🛑")
    async def stand_callback(interaction: discord.Interaction):
        await dealer_play(interaction, user_id, amount, player_hand, dealer_hand)

    stand_button.callback = stand_callback

    double_down_button = Button(label="Double Down", style=discord.ButtonStyle.danger, emoji="🔄")
    async def double_down_callback(interaction: discord.Interaction):
        nonlocal amount
        if len(player_hand) == 2:
            amount *= 2
            player_hand.append(draw_card())
            if hand_value(player_hand) > 21:
                await end_game(interaction, user_id, amount, player_hand, dealer_hand, "bust")
            else:
                await dealer_play(interaction, user_id, amount, player_hand, dealer_hand)
        else:
            await interaction.response.send_message("⚠️ You can only double down at the start of the game.", ephemeral=True)

    double_down_button.callback = double_down_callback

    view.add_item(hit_button)
    view.add_item(stand_button)
    view.add_item(double_down_button)

    await interaction.response.send_message(embed=embed, view=view)

async def update_embed(interaction, player_hand, dealer_hand, amount, view):
    embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.green())
    embed.add_field(name="Your Hand", value=f"{hand_display(player_hand)} (Total: **{hand_value(player_hand)}**)", inline=False)
    embed.add_field(name="Dealer's Hand", value=f"{hand_display([dealer_hand[0]])}, 🂠\n(Value of visible card: **{card_value_description(dealer_hand[0])}**)", inline=False)
    embed.set_footer(text=f"💰 Your current bet: {amount} coins")
    await interaction.response.edit_message(embed=embed, view=view)

async def dealer_play(interaction, user_id, amount, player_hand, dealer_hand):
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(draw_card())

    if hand_value(dealer_hand) > 21:
        await end_game(interaction, user_id, amount, player_hand, dealer_hand, "dealer_bust")
    else:
        await compare_hands(interaction, user_id, amount, player_hand, dealer_hand)

async def compare_hands(interaction, user_id, amount, player_hand, dealer_hand):
    player_total = hand_value(player_hand)
    dealer_total = hand_value(dealer_hand)
    if player_total > dealer_total:
        await end_game(interaction, user_id, amount, player_hand, dealer_hand, "win")
    elif player_total < dealer_total:
        await end_game(interaction, user_id, amount, player_hand, dealer_hand, "lose")
    else:
        await end_game(interaction, user_id, amount, player_hand, dealer_hand, "push")

async def end_game(interaction, user_id, amount, player_hand, dealer_hand, result):
    server_id = str(interaction.guild.id) 
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)

    if result == "bust":
        response = f"💔 You busted with {hand_display(player_hand)}! You lose {amount} coins."
        balance -= amount
    elif result == "dealer_bust":
        response = f"🎉 Dealer busted with {hand_display(dealer_hand)}! You win {amount} coins."
        balance += amount
    elif result == "win":
        response = f"🎉 You won with {hand_display(player_hand)}! You win {amount} coins."
        balance += amount
    elif result == "lose":
        response = f"💔 Dealer wins with {hand_display(dealer_hand)}! You lose {amount} coins."
        balance -= amount
    elif result == "push":
        response = f"🤝 It's a push! You both have {hand_display(player_hand)}. Your bet is returned."
    elif result == "blackjack":
        response = f"🃏 **Blackjack!** You won with {hand_display(player_hand)}! You win {amount * 1.5} coins."
        balance += amount * 1.5
    elif result == "push_blackjack":
        response = f"🤝 Both you and the dealer have Blackjack! It's a push. Your bet is returned."

    server_balances[user_id] = balance
    save_balances()

    embed = discord.Embed(title="🃏 Blackjack - Final Result", description=response, color=discord.Color.blue())
    embed.add_field(name="Your Hand", value=f"{hand_display(player_hand)} (Total: **{hand_value(player_hand)}**)", inline=False)
    embed.add_field(name="Dealer's Hand", value=f"{hand_display(dealer_hand)} (Total: **{hand_value(dealer_hand)}**)", inline=False)
    embed.set_footer(text=f"💰 Your current balance: {balance} coins")

    await interaction.response.edit_message(embed=embed, view=None)

def draw_card():
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return secrets.choice(cards)

def hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']:
            value += 10
        elif card == 'A':
            value += 11
            aces += 1
        else:
            value += int(card)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def hand_display(hand):
    return ', '.join([card_name(card) for card in hand])

def card_name(card):
    card_names = {
        'A': 'Ace',
        'K': 'King',
        'Q': 'Queen',
        'J': 'Jack',
        '10': '10',
        '9': '9',
        '8': '8',
        '7': '7',
        '6': '6',
        '5': '5',
        '4': '4',
        '3': '3',
        '2': '2'
    }
    return card_names[card]

def card_value_description(card):
    descriptions = {
        'A': 'Ace (1 or 11)',
        'K': 'King (10)',
        'Q': 'Queen (10)',
        'J': 'Jack (10)',
        '10': 'Ten (10)',
        '9': 'Nine (9)',
        '8': 'Eight (8)',
        '7': 'Seven (7)',
        '6': 'Six (6)',
        '5': 'Five (5)',
        '4': 'Four (4)',
        '3': 'Three (3)',
        '2': 'Two (2)',
    }
    return descriptions[card]



@bot.tree.command(name='enslave', description='🔗 Enslave a user to pay off their debt or for any reason')
@app_commands.describe(user='The user you want to enslave', amount='The amount of coins to pay daily (minimum 50 coins)')
async def enslave(interaction: discord.Interaction, user: discord.User, amount: int):
    await interaction.response.defer(thinking=True)  # Defer to allow time for processing

    server_id = str(interaction.guild.id)  # Get the server ID
    master_id = str(interaction.user.id)
    slave_id = str(user.id)
    server_slaves = get_server_slaves(server_id)

    if amount < 50:
        await interaction.followup.send("🚫 The minimum daily payment you can set is 50 coins.", ephemeral=True)
        return

    if slave_id in server_slaves:
        await interaction.followup.send("🚫 This user is already enslaved by someone else.", ephemeral=True)
        return

    user_ping = f"{user.mention}"

    slave_embed = discord.Embed(
        title="🔗 Enslavement Request",
        description=f"You are requested to be a slave to {interaction.user.mention} for **{amount} coins** per 24 hours.\n\n"
                    "Once you press 'Yes' on this embed, you won't be able to reverse this decision. Only the master can.",
        color=discord.Color.orange()
    )
    slave_embed.set_footer(text="Choose wisely!")

    slave_view = View()

    async def accept_callback(interaction: discord.Interaction):
        if interaction.user.id != user.id:
            await interaction.response.send_message("🚫 You are not authorized to respond to this request.", ephemeral=True)
            return

        try:
            server_slaves[slave_id] = {
                "master_id": master_id,
                "daily_payment": amount,
                "last_payment": datetime.now().isoformat(),
                "missed_payment": False 
            }
            save_slaves()

            server_balances = get_server_balances(server_id)

            server_balances[master_id] -= amount
            server_balances[slave_id] += amount
            save_balances()

            master = await bot.fetch_user(int(master_id))
            slave = await bot.fetch_user(int(slave_id))

            await master.send(f"💸 You have enslaved {slave.mention} and the first payment of {amount} coins has been deducted.")
            await slave.send(f"🔗 You have been enslaved by {master.mention} and have received your first payment of {amount} coins.")

            await interaction.response.edit_message(content="✔️ Enslavement accepted. The first payment has been made.", view=None)
        except discord.errors.NotFound:
            await interaction.followup.send(content="❌ Failed to process the enslavement. Interaction not found.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(content=f"❌ An error occurred: {str(e)}", ephemeral=True)

    async def deny_callback(interaction: discord.Interaction):
        if interaction.user.id != user.id:
            await interaction.response.send_message("🚫 You are not authorized to respond to this request.", ephemeral=True)
            return

        try:
            await interaction.followup.edit_message(content="❌ Enslavement request denied.", view=None)
        except discord.errors.NotFound:
            await interaction.followup.send(content="❌ Failed to process the denial. Interaction not found.", ephemeral=True)

    accept_button = Button(label="Yes", style=discord.ButtonStyle.green)
    accept_button.callback = accept_callback
    deny_button = Button(label="No", style=discord.ButtonStyle.red)
    deny_button.callback = deny_callback

    slave_view.add_item(accept_button)
    slave_view.add_item(deny_button)

    await interaction.followup.send(content=user_ping, embed=slave_embed, view=slave_view)

@tasks.loop(hours=1)
async def pay_slaves():
    for server_id, server_data in slave_data.items():
        server_balances = get_server_balances(server_id)

        for slave_id, data in server_data.items():
            if "master_id" not in data or "daily_payment" not in data or "last_payment" not in data:
                logger.error(f"Missing data in slave entry: {slave_id}. Skipping payment.")
                continue

            master_id = data["master_id"]
            daily_payment = data["daily_payment"]
            last_payment = datetime.fromisoformat(data["last_payment"])

            master = await bot.fetch_user(int(master_id))
            slave = await bot.fetch_user(int(slave_id))

            if not any(guild in slave.mutual_guilds for guild in master.mutual_guilds):
                await free_slave_payments(server_id, slave_id, master_id)
                try:
                    await master.send(f"⚠️ You and your slave {slave.mention} no longer share a server. The slave has been freed.")
                except discord.Forbidden:
                    logger.warning(f"Failed to send DM to {master.display_name} (ID: {master.id}) about freeing the slave.")

                try:
                    await slave.send(f"🎉 You and your master {master.mention} no longer share a server. You have been freed from slavery.")
                except discord.Forbidden:
                    logger.warning(f"Failed to send DM to {slave.display_name} (ID: {slave.id}) about being freed.")

                continue

            if datetime.now() >= last_payment + timedelta(days=1):
                if master_id not in server_balances:
                    server_balances[master_id] = 0
                if slave_id not in server_balances:
                    server_balances[slave_id] = 0

                if server_balances.get(master_id, 0) >= daily_payment:
                    if data.get("missed_payment", False):
                        amount_due = daily_payment * 2  
                        if server_balances[master_id] >= amount_due:
                            server_balances[master_id] -= amount_due
                            server_balances[slave_id] += amount_due
                            slave_data[server_id][slave_id]["missed_payment"] = False  
                            slave_data[server_id][slave_id]["last_payment"] = datetime.now().isoformat()
                            save_balances()
                            save_slaves()

                            try:
                                await master.send(f"💸 {amount_due} coins have been deducted from your balance for your slave {slave.mention} due to a missed payment.")
                                await slave.send(f"🔗 You have received a double payment of {amount_due} coins from your master {master.mention} due to a missed payment.")
                            except discord.Forbidden:
                                logger.warning(f"Failed to send DM to {master.display_name} (ID: {master.id}) or {slave.display_name} (ID: {slave.id}).")

                        else:
                            await free_slave_payments(server_id, slave_id, master_id)
                    else:
                        server_balances[master_id] -= daily_payment
                        server_balances[slave_id] += daily_payment
                        slave_data[server_id][slave_id]["last_payment"] = datetime.now().isoformat()
                        save_balances()
                        save_slaves()

                        try:
                            await master.send(f"💸 {daily_payment} coins have been deducted from your balance for your slave {slave.mention}.")
                            await slave.send(f"🔗 You have received your daily payment of {daily_payment} coins from your master {master.mention}.")
                        except discord.Forbidden:
                            logger.warning(f"Failed to send DM to {master.display_name} (ID: {master.id}) or {slave.display_name} (ID: {slave.id}).")

                else:
                    slave_data[server_id][slave_id]["missed_payment"] = True
                    save_slaves()

                    try:
                        await master.send(f"⚠️ You missed a payment for your slave {slave.mention}. If you don't pay double the amount tomorrow, you will lose ownership.")
                        await slave.send(f"⚠️ Your master {master.mention} missed a payment. If they don't pay double the amount tomorrow, you will be freed.")
                    except discord.Forbidden:
                        logger.warning(f"Failed to send DM to {master.display_name} (ID: {master.id}) or {slave.display_name} (ID: {slave.id}).")

async def free_slave_payments(server_id, slave_id, master_id):
    try:
        slave_data[server_id].pop(slave_id, None)
        save_slaves()

        master = await bot.fetch_user(int(master_id))
        slave = await bot.fetch_user(int(slave_id))

        try:
            await master.send(f"⚠️ You failed to make the required payment. You have lost ownership of {slave.mention}.")
        except discord.errors.Forbidden:
            logging.warning(f"Failed to send message to master {master_id} (Forbidden).")
        
        try:
            await slave.send(f"🎉 You are no longer enslaved by {master.mention} due to missed payments.")
        except discord.errors.Forbidden:
            logging.warning(f"Failed to send message to slave {slave_id} (Forbidden).")

    except KeyError:
        logging.error(f"Attempted to free a slave that did not exist in the database: Server ID: {server_id}, Slave ID: {slave_id}, Master ID: {master_id}")



@bot.event
async def on_member_update(before, after):
    logger.info(f"Member update detected: {after.id} ({after.display_name})")
    
    if before.nick != after.nick:
        logger.info(f"Nickname change detected for {after.display_name} (ID: {after.id}). Old: '{before.nick}', New: '{after.nick}'")

        slave_id = str(after.id)
        if slave_id in slave_nicknames:
            expected_nickname = slave_nicknames[slave_id]
            if after.nick != expected_nickname:
                logger.info(f"Attempting to revert nickname for {after.display_name} (ID: {after.id}) to '{expected_nickname}'")
                
                try:
                    await after.edit(nick=expected_nickname)
                    logger.info(f"Successfully reverted nickname for {after.display_name} (ID: {after.id}) to '{expected_nickname}'")

                    master_id = slave_data[slave_id]["master_id"]
                    master = await bot.fetch_user(int(master_id))
                    await master.send(f"⚠️ Your slave {after.mention} tried to change their nickname to **{after.nick}**, but it was reverted to **{expected_nickname}**.")
                    
                    await after.send(f"⚠️ You tried to change your nickname to **{after.nick}**, but your master demands you keep the nickname **{expected_nickname}**. Behave yourself!")

                except discord.Forbidden:
                    logger.warning(f"Failed to revert nickname for {after.display_name} (ID: {after.id}) due to lack of permissions.")
                except discord.HTTPException as e:
                    logger.error(f"Failed to revert nickname for {after.display_name} (ID: {after.id}): {e}")

@bot.tree.command(name="tame", description="Tame your slave by setting their nickname.")
@app_commands.describe(slave="The user you want to tame", nickname="The nickname you want to set for the slave")
async def tame(interaction: discord.Interaction, slave: discord.Member, nickname: str):
    master_id = interaction.user.id

    if not interaction.guild.me.guild_permissions.manage_nicknames:
        await interaction.response.send_message("🚫 I don't have permission to manage nicknames in this server.", ephemeral=True)
        return

    try:
        await slave.edit(nick=nickname)
        
        slave_nicknames[str(slave.id)] = nickname
        slave_data[str(slave.id)] = {"master_id": str(master_id)}
        save_slave_nicknames()  # Save to file

        await interaction.response.send_message(f"✔️ Successfully tamed {slave.mention}. Their nickname is now '{nickname}'.", ephemeral=True)
        
        await slave.send(f"🔗 Your master {interaction.user.mention} has set your nickname to '{nickname}'. Do not try to change it.")

    except discord.Forbidden:
        await interaction.response.send_message("🚫 I don't have permission to change this user's nickname.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"❌ Failed to change the nickname due to an unexpected error: {str(e)}", ephemeral=True)



PAYOUTS = {
    "number": 35,  # 35:1 for straight-up bets on a specific number
    "color": 1,    # 1:1 for red or black
    "evenodd": 1,  # 1:1 for odd or even
    "lowhigh": 1   # 1:1 for low (1-18) or high (19-36)
}

ROULETTE_NUMBERS = [
    {"number": 0, "color": "green"},
    {"number": 1, "color": "red"},
    {"number": 2, "color": "black"},
    {"number": 3, "color": "red"},
    {"number": 4, "color": "black"},
    {"number": 5, "color": "red"},
    {"number": 6, "color": "black"},
    {"number": 7, "color": "red"},
    {"number": 8, "color": "black"},
    {"number": 9, "color": "red"},
    {"number": 10, "color": "black"},
    {"number": 11, "color": "black"},
    {"number": 12, "color": "red"},
    {"number": 13, "color": "black"},
    {"number": 14, "color": "red"},
    {"number": 15, "color": "black"},
    {"number": 16, "color": "red"},
    {"number": 17, "color": "black"},
    {"number": 18, "color": "red"},
    {"number": 19, "color": "red"},
    {"number": 20, "color": "black"},
    {"number": 21, "color": "red"},
    {"number": 22, "color": "black"},
    {"number": 23, "color": "red"},
    {"number": 24, "color": "black"},
    {"number": 25, "color": "red"},
    {"number": 26, "color": "black"},
    {"number": 27, "color": "red"},
    {"number": 28, "color": "black"},
    {"number": 29, "color": "black"},
    {"number": 30, "color": "red"},
    {"number": 31, "color": "black"},
    {"number": 32, "color": "red"},
    {"number": 33, "color": "black"},
    {"number": 34, "color": "red"},
    {"number": 35, "color": "black"},
    {"number": 36, "color": "red"}
]


@bot.tree.command(name="roulette", description="🎲 Play a game of roulette with realistic odds!")
@app_commands.describe(bet_value="Enter your bet value")
@app_commands.choices(bet_type=[
    app_commands.Choice(name="Number", value="number"),
    app_commands.Choice(name="Color", value="color"),
    app_commands.Choice(name="Odd/Even", value="evenodd"),
    app_commands.Choice(name="Low/High", value="lowhigh")
])
async def roulette(interaction: discord.Interaction, bet_type: app_commands.Choice[str], bet_value: str, amount: int):
    server_id = str(interaction.guild.id) 
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500) 

    if bet_type.value == "number":
        if not bet_value.isdigit() or not (0 <= int(bet_value) <= 36):
            await interaction.response.send_message("🚫 Invalid bet value for 'Number'. Please enter a number between 0 and 36.", ephemeral=True)
            return
    elif bet_type.value == "color":
        if bet_value.lower() not in ["red", "black"]:
            await interaction.response.send_message("🚫 Invalid bet value for 'Color'. Please enter 'red' or 'black'.", ephemeral=True)
            return
    elif bet_type.value == "evenodd":
        if bet_value.lower() not in ["odd", "even"]:
            await interaction.response.send_message("🚫 Invalid bet value for 'Odd/Even'. Please enter 'odd' or 'even'.", ephemeral=True)
            return
    elif bet_type.value == "lowhigh":
        if bet_value.lower() not in ["low", "high"]:
            await interaction.response.send_message("🚫 Invalid bet value for 'Low/High'. Please enter 'low' or 'high'.", ephemeral=True)
            return

    if amount <= 0:
        await interaction.response.send_message("⚠️ You must bet a positive amount.", ephemeral=True)
        return

    if amount > balance:
        await interaction.response.send_message("🚫 You don't have enough coins to make that bet.", ephemeral=True)
        return

    outcome = secrets.choice(ROULETTE_NUMBERS)
    outcome_number = outcome["number"]
    outcome_color = outcome["color"]

    winnings = 0
    if bet_type.value == "number":
        if int(bet_value) == outcome_number:
            winnings = amount * PAYOUTS["number"]
            result_message = f"🎉 The ball landed on {outcome_number} ({outcome_color})! You won {winnings} coins!"
        else:
            winnings = -amount
            result_message = f"💔 The ball landed on {outcome_number} ({outcome_color}). You lost {amount} coins."
    elif bet_type.value == "color":
        if bet_value.lower() == outcome_color:
            winnings = amount * PAYOUTS["color"]
            result_message = f"🎉 The ball landed on {outcome_number} ({outcome_color})! You won {winnings} coins!"
        else:
            winnings = -amount
            result_message = f"💔 The ball landed on {outcome_number} ({outcome_color}). You lost {amount} coins."
    elif bet_type.value == "evenodd":
        if (bet_value.lower() == "even" and outcome_number != 0 and outcome_number % 2 == 0) or (bet_value.lower() == "odd" and outcome_number % 2 != 0):
            winnings = amount * PAYOUTS["evenodd"]
            result_message = f"🎉 The ball landed on {outcome_number} ({outcome_color})! You won {winnings} coins!"
        else:
            winnings = -amount
            result_message = f"💔 The ball landed on {outcome_number} ({outcome_color}). You lost {amount} coins."
    elif bet_type.value == "lowhigh":
        if (bet_value.lower() == "low" and 1 <= outcome_number <= 18) or (bet_value.lower() == "high" and 19 <= outcome_number <= 36):
            winnings = amount * PAYOUTS["lowhigh"]
            result_message = f"🎉 The ball landed on {outcome_number} ({outcome_color})! You won {winnings} coins!"
        else:
            winnings = -amount
            result_message = f"💔 The ball landed on {outcome_number} ({outcome_color}). You lost {amount} coins."

    balance += winnings
    server_balances[user_id] = balance
    save_balances()

    await interaction.response.send_message(result_message)


@bot.tree.command(name="muzzle", description="🔇 Muzzle your slave to delete messages containing specific keywords.")
@app_commands.describe(slave="The slave you want to muzzle", keywords="The keywords to trigger message deletion (separate by commas)")
async def muzzle(interaction: discord.Interaction, slave: discord.Member, keywords: str):
    master_id = interaction.user.id
    slave_id = str(slave.id)

    if slave_id in slave_data and slave_data[slave_id]["master_id"] == str(master_id):
        new_keywords = [keyword.strip().lower() for keyword in keywords.split(",")]

        if slave_id in muzzled_slaves:
            muzzled_slaves[slave_id].extend(new_keywords)
            muzzled_slaves[slave_id] = list(set(muzzled_slaves[slave_id]))  
        else:
            muzzled_slaves[slave_id] = new_keywords

        save_muzzle_data()

        await interaction.response.send_message(
            f"🔇 {slave.mention} has been muzzled. Messages containing the keywords '{', '.join(new_keywords)}' will be deleted.",
            ephemeral=False
        )
    else:
        await interaction.response.send_message("🚫 You do not own this slave, so you cannot muzzle them.", ephemeral=True)

@bot.tree.command(name="unmuzzle", description="🔊 Unmuzzle your slave to allow them to speak freely.")
@app_commands.describe(slave="The slave you want to unmuzzle", keywords="The keywords to remove from the muzzle (optional, separate by commas)")
async def unmuzzle(interaction: discord.Interaction, slave: discord.Member, keywords: str = None):
    master_id = interaction.user.id
    slave_id = str(slave.id)

    if slave_id in slave_data and slave_data[slave_id]["master_id"] == str(master_id):
        if slave_id in muzzled_slaves:
            if keywords:
                remove_keywords = [keyword.strip().lower() for keyword in keywords.split(",")]
                muzzled_slaves[slave_id] = [kw for kw in muzzled_slaves[slave_id] if kw not in remove_keywords]
                
                if not muzzled_slaves[slave_id]:
                    del muzzled_slaves[slave_id]  
                    await interaction.response.send_message(f"🔊 {slave.mention} has been fully unmuzzled and can speak freely.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"🔊 The keywords '{', '.join(remove_keywords)}' have been removed from {slave.mention}'s muzzle.", ephemeral=True)
            else:
                del muzzled_slaves[slave_id]
                await interaction.response.send_message(f"🔊 {slave.mention} has been fully unmuzzled and can speak freely.", ephemeral=True)
            
            save_muzzle_data()
        else:
            await interaction.response.send_message(f"🔊 {slave.mention} is not muzzled.", ephemeral=True)
    else:
        await interaction.response.send_message("🚫 You do not own this slave, so you cannot unmuzzle them.", ephemeral=True)


@bot.tree.command(name="unslave", description="⚠️ Free your slave and stop daily payments.")
@app_commands.describe(slave="The slave you want to free")
async def unslave(interaction: discord.Interaction, slave: discord.User):
    master_id = str(interaction.user.id)
    slave_id = str(slave.id)

    if slave_id in slave_data and slave_data[slave_id]["master_id"] == master_id:
        slave_data.pop(slave_id, None)
        save_slaves()

        if slave_id in muzzled_slaves:
            muzzled_slaves.pop(slave_id, None)
            save_muzzled_slaves()

        if slave_id in slave_nicknames:
            slave_nicknames.pop(slave_id, None)
            save_slave_nicknames()

        await interaction.response.send_message(f"⚠️ {slave.mention} has been freed and is no longer your slave.", ephemeral=True)

        master = await bot.fetch_user(int(master_id))
        slave = await bot.fetch_user(int(slave_id))

        await master.send(f"⚠️ You have freed {slave.mention} from slavery.")
        await slave.send(f"🎉 You are no longer enslaved by {master.mention}. Any restrictions or nicknames imposed on you have been lifted.")
    else:
        await interaction.response.send_message(f"🚫 You do not own {slave.mention}, or they are not currently a slave.", ephemeral=True)

@bot.tree.command(name="slots", description="🎰 Try your luck with the slot machine!")
@app_commands.describe(amount="The amount of coins you want to bet")
async def slots(interaction: discord.Interaction, amount: int):
    server_id = str(interaction.guild.id) 
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)

    if amount <= 0:
        await interaction.response.send_message("🚫 You must bet a positive amount.", ephemeral=True)
        return

    if amount > balance:
        await interaction.response.send_message("🚫 You don't have enough coins to make that bet.", ephemeral=True)
        return

    symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]
    payout_multipliers = {
        "🍒🍒🍒": 5,  # 5x payout
        "🍋🍋🍋": 3,  # 3x payout
        "🔔🔔🔔": 10,  # 10x payout
        "⭐⭐⭐": 15,  # 15x payout
        "💎💎💎": 50  # 50x payout
    }

    spin_result = [secrets.choice(symbols) for _ in range(3)]
    spin_str = ''.join(spin_result)

    if spin_str in payout_multipliers:
        payout = amount * payout_multipliers[spin_str]
        balance += payout
        result_message = f"🎉 **Jackpot!** You got {spin_str} and won **{payout} coins**!"
        result_color = discord.Color.green()
    else:
        balance -= amount
        result_message = f"😢 You got {spin_str}. Better luck next time!"
        result_color = discord.Color.red()

    server_balances[user_id] = balance
    save_balances()

    embed = discord.Embed(
        title="🎰 Slot Machine",
        description=f"**Your Bet:** {amount} coins",
        color=result_color
    )

    # Format the slot machine look
    embed.add_field(
        name="----------------------",
        value="**│   │   │   │**\n"
              f"**│  {spin_result[0]}  │  {spin_result[1]}  │  {spin_result[2]}  │**\n"
              "**│   │   │   │**",
        inline=False
    )
    embed.add_field(name="----------------------", value=" ", inline=False)
    embed.add_field(name="**Result**", value=result_message, inline=False)
    embed.add_field(name="**Your Balance**", value=f"**{balance} coins**", inline=False)

    embed.set_footer(text="Good luck on your next spin! 🎰")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slaves", description="📜 Show information about the slaves you currently own.")
async def slaves(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)  
    master_id = str(interaction.user.id)
    server_slaves = get_server_slaves(server_id)

    owned_slaves = {slave_id: data for slave_id, data in server_slaves.items() if data.get("master_id") == master_id}

    if not owned_slaves:
        await interaction.response.send_message("😶 You don't currently own any slaves.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📜 Your Slaves",
        description="Here is a list of all the slaves you currently own:",
        color=discord.Color.purple()
    )
    
    for slave_id, data in owned_slaves.items():
        slave_user = await bot.fetch_user(int(slave_id))
        slave_name = slave_user.display_name if slave_user else "Unknown User"

        muzzle_status = "🔇 Not Muzzled" if slave_id not in muzzled_slaves else f"🔇 Muzzled: {', '.join(muzzled_slaves[slave_id])}"
        tamed_name = slave_nicknames.get(slave_id, "🐾 Not Tamed")

        embed.add_field(
            name=f"🔹 Slave: {slave_name}",
            value=(
                f"**🔒 Muzzled:** {muzzle_status}\n"
                f"**🐾 Tamed Name:** {tamed_name}"
            ),
            inline=False
        )

    embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed, ephemeral=False)

LUCKY_FILE = 'lucky_wheel_cooldowns.json'

def load_cooldowns_lucky():
    if os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cooldowns_lucky():
    with open(COOLDOWN_FILE, 'w') as file:
        json.dump(work_cooldowns, file, indent=4)

lucky_wheel_cooldowns = load_cooldowns_lucky()

wheel_possibilities = [
    ("100 coins", 30),
    ("500 coins", 10),
    ("freed from slavery", 0.5),
    ("10000 coins", 0.01),
    ("50 coins", 50),
    ("350 coins", 10)
]

def spin_wheel(possibilities):
    choices = []
    for prize, weight in possibilities:
        choices.extend([prize] * int(weight * 100))  
    return secrets.choice(choices)

@bot.tree.command(name="lucky_wheel", description="🎡 Spin the lucky wheel and see what you win!")
async def lucky_wheel(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    current_time = datetime.now()

    check_expired_inventory(server_id, user_id)

    global user_inventory
    if user_inventory is None:
        user_inventory = {}

    if server_id not in user_inventory:
        user_inventory[server_id] = {}
    if user_id not in user_inventory[server_id]:
        user_inventory[server_id][user_id] = {}

    if server_id not in lucky_wheel_cooldowns:
        lucky_wheel_cooldowns[server_id] = {}

    if "extra_spin" in user_inventory[server_id][user_id]:
        del user_inventory[server_id][user_id]["extra_spin"]
        save_inventory()
    elif user_id in lucky_wheel_cooldowns[server_id]:
        last_used_time = datetime.fromisoformat(lucky_wheel_cooldowns[server_id][user_id])
        if current_time < last_used_time + timedelta(hours=24):
            remaining_time = (last_used_time + timedelta(hours=24)) - current_time
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(
                f"⏳ You need to wait **{hours} hours and {minutes} minutes** before spinning the wheel again.",
                ephemeral=True
            )
            return

    has_lucky_clover = "lucky_clover" in user_inventory[server_id][user_id]

    wheel_possibilities = [
        ("100 coins", 30 if not has_lucky_clover else 25),
        ("500 coins", 10 if not has_lucky_clover else 12),
        ("freed from slavery", 0.5 if not has_lucky_clover else 1),
        ("10000 coins", 0.01 if not has_lucky_clover else 0.1),
        ("50 coins", 50 if not has_lucky_clover else 45),
        ("350 coins", 10 if not has_lucky_clover else 12)
    ]

    possibilities_description = "\n".join([f"**{prize}**: {weight}%" for prize, weight in wheel_possibilities])
    embed = discord.Embed(
        title="🎡 Lucky Wheel",
        description="Here are the possible outcomes of the lucky wheel spin:\n\n" + possibilities_description,
        color=discord.Color.blue()
    )
    embed.set_footer(text="Press the button below to spin the wheel!")

    view = View()

    spin_button = Button(label="Spin the Wheel", style=discord.ButtonStyle.green, emoji="🎰")

    async def spin_callback(interaction_button: discord.Interaction):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        result = spin_wheel(wheel_possibilities)

        server_balances = get_server_balances(server_id)
        reward = None
        if result == "100 coins":
            reward = 100
        elif result == "500 coins":
            reward = 500
        elif result == "freed from slavery":
            if server_id in slave_data and user_id in slave_data[server_id]:
                await free_slave_wheel(server_id, user_id, slave_data[server_id][user_id]["master_id"])
            else:
                reward = 5000 
        elif result == "10000 coins":
            reward = 10000
        elif result == "50 coins":
            reward = 50
        elif result == "350 coins":
            reward = 350

        if reward is not None:
            if "double_earnings" in user_inventory[server_id][user_id]:
                reward *= 2  

            server_balances[user_id] = server_balances.get(user_id, 0) + reward
            save_balances()

        lucky_wheel_cooldowns[server_id][user_id] = current_time.isoformat()
        save_cooldowns_lucky()

        result_embed = discord.Embed(
            title="🎡 Lucky Wheel Result",
            description=f"You spun the wheel and won **{result}**!",
            color=discord.Color.gold()
        )
        result_embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        spin_button.disabled = True
        await interaction_button.response.edit_message(embed=result_embed, view=view)

    spin_button.callback = spin_callback
    view.add_item(spin_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

async def free_slave_wheel(server_id, slave_id, master_id):
    slave_data[server_id].pop(slave_id, None)
    save_slaves()

    master = await bot.fetch_user(int(master_id))
    slave = await bot.fetch_user(int(slave_id))

    await master.send(f"⚠️ Your slave {slave.mention} was freed by the Lucky Wheel.")
    await slave.send(f"🎉 You are no longer enslaved by {master.mention} thanks to the Lucky Wheel.")


def get_random_percentage(min_percent, max_percent):
    return secrets.randbelow(max_percent - min_percent + 1) + min_percent

@bot.tree.command(name="blackmarket", description="🖤 Welcome to the Black Market")
async def blackmarket(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)

    embed = discord.Embed(
        title="🖤 Black Market",
        description="Welcome to the Black Market. Here are the available options:",
        color=discord.Color.dark_grey()
    )

    embed.add_field(name="💰 Rob Money", value="Cost: 500 coins. Attempt to rob someone's money. Success rate: Varies.", inline=False)
    embed.add_field(name="🔄 Overthrow Master", value="Cost: 25,000 coins. Attempt to overthrow your master. Success rate: 25%.", inline=False)
    embed.add_field(name="⏳ Reduce Cooldowns", value="Cost: 800 coins. 25% chance to reduce or remove cooldowns on 'work' and 'lucky wheel'.", inline=False)

    view = View()

    rob_button = Button(label="Rob Money", style=discord.ButtonStyle.primary, emoji="💰")
    overthrow_button = Button(label="Overthrow Master", style=discord.ButtonStyle.danger, emoji="🔄")
    reduce_cooldowns_button = Button(label="Reduce Cooldowns", style=discord.ButtonStyle.success, emoji="⏳")

    async def reduce_cooldowns_callback(interaction_button: discord.Interaction):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        if balance < 800:
            await interaction_button.response.send_message("You don't have enough money to attempt reducing cooldowns.", ephemeral=True)
            return

        server_balances[user_id] -= 800
        save_balances()

        success_chance = secrets.randbelow(100) + 1
        if success_chance <= 25:  # 25% chance of success
            if secrets.randbelow(100) < 50:  # 50% chance to remove cooldowns
                removed_work = False
                removed_lucky_wheel = False

                if user_id in work_cooldowns.get(server_id, {}):
                    del work_cooldowns[server_id][user_id]
                    removed_work = True

                if user_id in lucky_wheel_cooldowns.get(server_id, {}):
                    del lucky_wheel_cooldowns[server_id][user_id]
                    removed_lucky_wheel = True

                save_cooldowns()  # Save the updated cooldowns

                if removed_work and removed_lucky_wheel:
                    await interaction_button.response.send_message("Success! Both 'work' and 'lucky wheel' cooldowns have been removed!", ephemeral=False)
                elif removed_work:
                    await interaction_button.response.send_message("Success! 'Work' cooldown has been removed!", ephemeral=False)
                elif removed_lucky_wheel:
                    await interaction_button.response.send_message("Success! 'Lucky Wheel' cooldown has been removed!", ephemeral=False)
                else:
                    await interaction_button.response.send_message("There were no active cooldowns to remove.", ephemeral=True)
            else:  
                halved_work = False
                halved_lucky_wheel = False

                if user_id in work_cooldowns.get(server_id, {}):
                    current_cooldown_time = datetime.fromisoformat(work_cooldowns[server_id][user_id])
                    remaining_time = current_cooldown_time - datetime.now()
                    new_cooldown_time = datetime.now() + (remaining_time * 0.5)  
                    work_cooldowns[server_id][user_id] = new_cooldown_time.isoformat()
                    halved_work = True

                if user_id in lucky_wheel_cooldowns.get(server_id, {}):
                    current_cooldown_time = datetime.fromisoformat(lucky_wheel_cooldowns[server_id][user_id])
                    remaining_time = current_cooldown_time - datetime.now()
                    new_cooldown_time = datetime.now() + (remaining_time * 0.5)  
                    lucky_wheel_cooldowns[server_id][user_id] = new_cooldown_time.isoformat()
                    halved_lucky_wheel = True

                save_cooldowns()  # Save the updated cooldowns

                if halved_work and halved_lucky_wheel:
                    await interaction_button.response.send_message("Success! Both 'work' and 'lucky wheel' cooldowns have been halved!", ephemeral=False)
                elif halved_work:
                    await interaction_button.response.send_message("Success! 'Work' cooldown has been halved!", ephemeral=False)
                elif halved_lucky_wheel:
                    await interaction_button.response.send_message("Success! 'Lucky Wheel' cooldown has been halved!", ephemeral=False)
                else:
                    await interaction_button.response.send_message("There were no active cooldowns to halve.", ephemeral=True)
        else:  
            fine_percentage = get_random_percentage(1, 20)
            fine_amount = int(balance * fine_percentage / 100)
            server_balances[user_id] -= fine_amount
            save_balances()
            await interaction_button.response.send_message(f"Failed to reduce cooldowns. You have been fined **{fine_amount} coins**.", ephemeral=False)

    async def rob_callback(interaction_button: discord.Interaction):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        if balance < 500: 
            await interaction_button.response.send_message("You don't have enough money to rob someone.", ephemeral=True)
            return

        target_view = View()

        select_menu = Select(
            placeholder="Choose a target to rob...",
            options=[discord.SelectOption(label=member.display_name, value=str(member.id)) for member in interaction.guild.members if member.id != interaction.user.id]
        )

        async def select_callback(interaction_select: discord.Interaction):
            target_id = str(select_menu.values[0])
            target_name = interaction.guild.get_member(int(target_id)).display_name

            server_balances[user_id] -= 500
            save_balances()

            if "stealth_mode" in user_inventory[server_id].get(target_id, {}):
                await interaction_select.response.send_message(f"{target_name} is in stealth mode and cannot be robbed.", ephemeral=False)
                return

            success_chance = secrets.randbelow(100) + 1
            if success_chance <= 50:  
                victim_balance = server_balances.get(target_id, 0)
                robbed_percentage = get_random_percentage(5, 30)
                robbed_amount = int(victim_balance * robbed_percentage / 100)

                server_balances[user_id] += robbed_amount
                server_balances[target_id] -= robbed_amount
                save_balances()

                await interaction_select.response.send_message(f"Success! You robbed **{robbed_amount} coins** from {target_name}!", ephemeral=False)
                victim = await bot.fetch_user(int(target_id))
                await victim.send(f"⚠️ {interaction.user.mention} has robbed you for **{robbed_amount} coins**.")
            else:
                fine = int(balance * 0.25)
                server_balances[user_id] -= fine
                
                save_balances()

                await interaction_select.response.send_message(f"You failed the robbery attempt and were fined **{fine} coins**.", ephemeral=False)

        select_menu.callback = select_callback
        target_view.add_item(select_menu)

        await interaction_button.response.send_message("Select a target to rob:", view=target_view, ephemeral=True)

    async def overthrow_callback(interaction_button: discord.Interaction):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        if balance < 25000:
            await interaction_button.response.send_message("You don't have enough money to overthrow your master.", ephemeral=True)
            return

        server_balances[user_id] -= 25000
        save_balances()

        if server_id in slave_data and user_id in slave_data[server_id]:
            master_id = slave_data[server_id][user_id]["master_id"]

            success_chance = secrets.randbelow(100) + 1
            if success_chance <= 25:  
                await free_slave(server_id, user_id, master_id)
                if secrets.randbelow(100) < 5:
                    robbed_percentage = get_random_percentage(5, 30)
                    master_balance = server_balances.get(master_id, 0)
                    robbed_amount = int(master_balance * robbed_percentage / 100)
                    server_balances[user_id] += robbed_amount
                    server_balances[master_id] -= robbed_amount
                    save_balances()
                    await interaction_button.response.send_message(f"Success! You overthrew your master and robbed **{robbed_amount} coins** from them!", ephemeral=False)
                else:
                    await interaction_button.response.send_message("Success! You overthrew your master!", ephemeral=False)
            else:
                fine = int(balance * 0.65)
                server_balances[user_id] -= fine
                save_balances()

                await interaction_button.response.send_message(f"You failed to overthrow your master and were fined **{fine} coins**.", ephemeral=False)
        else:
            await interaction_button.response.send_message("You are not enslaved, so you can't overthrow your master.", ephemeral=True)

    rob_button.callback = rob_callback
    overthrow_button.callback = overthrow_callback
    reduce_cooldowns_button.callback = reduce_cooldowns_callback

    view.add_item(rob_button)
    view.add_item(overthrow_button)
    view.add_item(reduce_cooldowns_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

async def free_slave(server_id, slave_id, master_id):
    slave_data[server_id].pop(slave_id, None)
    save_slaves()

    master = await bot.fetch_user(int(master_id))
    slave = await bot.fetch_user(int(slave_id))

    await master.send(f"⚠️ Your slave {slave.mention} was freed by the Black Market.")
    await slave.send(f"🎉 You are no longer enslaved by {master.mention} thanks to the Black Market.")



@bot.tree.command(name="shop", description="🛒 Visit the shop and purchase items!")
async def shop(interaction: discord.Interaction):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    ensure_inventory(server_id, user_id)

    server_balances = get_server_balances(server_id)
    balance = server_balances.get(user_id, 500)

    embed = discord.Embed(
        title="🛒 Shop",
        description="Welcome to the shop! Here are the items available for purchase:",
        color=discord.Color.blue()
    )

    embed.add_field(name="🍀 Lucky Clover", value="Price: 1,150 coins. Increases chances of winning big rewards on 'lucky wheel' by 10%.", inline=False)
    embed.add_field(name="🛠️ Robbery Kit", value="Price: 1,500 coins. Increases the success rate of your next robbery attempt by 20%.", inline=False)
    embed.add_field(name="🕶️ Stealth Mode", value="Price: 2,000 coins. Prevents you from being targeted for robbery for 24 hours.", inline=False)
    embed.add_field(name="⏳ Cooldown Reduction", value="Price: 2,000 coins. Reduces all active cooldowns by 50%.", inline=False)
    embed.add_field(name="🎰 Extra Spin", value="Price: 2,500 coins. Allows you to spin the 'lucky wheel' one additional time without waiting for the cooldown.", inline=False)
    embed.add_field(name="💰 Double Earnings Boost", value="Price: 3,000 coins. Doubles the money earned from 'work' and 'lucky wheel' commands for 24 hours.", inline=False)

    view = View()

    lucky_clover_button = Button(label="Buy Lucky Clover", style=discord.ButtonStyle.success, emoji="🍀")
    robbery_kit_button = Button(label="Buy Robbery Kit", style=discord.ButtonStyle.success, emoji="🛠️")
    stealth_mode_button = Button(label="Buy Stealth Mode", style=discord.ButtonStyle.success, emoji="🕶️")
    cooldown_reduction_button = Button(label="Buy Cooldown Reduction", style=discord.ButtonStyle.success, emoji="⏳")
    extra_spin_button = Button(label="Buy Extra Spin", style=discord.ButtonStyle.success, emoji="🎰")
    double_earnings_button = Button(label="Buy Double Earnings Boost", style=discord.ButtonStyle.success, emoji="💰")

    async def buy_item(interaction_button: discord.Interaction, item_name: str, price: int, effect_function):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        if balance < price:
            await interaction_button.response.send_message(f"You don't have enough coins to buy {item_name}.", ephemeral=True)
            return

        server_balances[user_id] -= price
        save_balances()

        await effect_function(interaction_button, server_id, user_id)

    async def lucky_clover_effect(interaction_button, server_id, user_id):
        user_inventory[server_id][user_id]["lucky_clover"] = True
        await interaction_button.response.send_message("You purchased a 🍀 Lucky Clover! Your chances of winning big on the 'lucky wheel' have increased by 10%.", ephemeral=True)

    async def robbery_kit_effect(interaction_button, server_id, user_id):
        user_inventory[server_id][user_id]["robbery_kit"] = True
        await interaction_button.response.send_message("You purchased a 🛠️ Robbery Kit! Your success rate for the next robbery attempt has increased by 20%.", ephemeral=True)

    async def stealth_mode_effect(interaction_button, server_id, user_id):
        user_inventory[server_id][user_id]["stealth_mode"] = datetime.now().isoformat()
        save_inventory()
        await interaction_button.response.send_message("You purchased 🕶️ Stealth Mode! You won't be targeted for robbery for 24 hours.", ephemeral=True)
        await asyncio.sleep(86400)  # Wait for 24 hours
        if user_inventory[server_id][user_id].get("stealth_mode"):
            del user_inventory[server_id][user_id]["stealth_mode"]
            save_inventory()
            user = await bot.fetch_user(int(user_id))
            await user.send("🕶️ Your Stealth Mode has expired. You can now be targeted for robbery again.")

    async def cooldown_reduction_effect(interaction_button, server_id, user_id):
        if user_id in work_cooldowns.get(server_id, {}):
            current_cooldown_time = datetime.fromisoformat(work_cooldowns[server_id][user_id])
            remaining_time = current_cooldown_time - datetime.now()
            new_cooldown_time = datetime.now() + (remaining_time * 0.5) 
            work_cooldowns[server_id][user_id] = new_cooldown_time.isoformat()

        if user_id in lucky_wheel_cooldowns.get(server_id, {}):
            current_cooldown_time = datetime.fromisoformat(lucky_wheel_cooldowns[server_id][user_id])
            remaining_time = current_cooldown_time - datetime.now()
            new_cooldown_time = datetime.now() + (remaining_time * 0.5) 
            lucky_wheel_cooldowns[server_id][user_id] = new_cooldown_time.isoformat()

        save_cooldowns()
        await interaction_button.response.send_message("You purchased ⏳ Cooldown Reduction! All active cooldowns have been reduced by 50%.", ephemeral=True)

    async def extra_spin_effect(interaction_button, server_id, user_id):
        user_inventory[server_id][user_id]["extra_spin"] = True
        await interaction_button.response.send_message("You purchased 🎰 Extra Spin! You can spin the 'lucky wheel' one additional time without waiting for the cooldown.", ephemeral=True)

    async def double_earnings_effect(interaction_button, server_id, user_id):
        user_inventory[server_id][user_id]["double_earnings"] = datetime.now().isoformat()
        save_inventory()
        await interaction_button.response.send_message("You purchased 💰 Double Earnings Boost! You'll earn double money from 'work' and 'lucky wheel' commands for the next 24 hours.", ephemeral=True)

    lucky_clover_button.callback = lambda interaction_button: buy_item(interaction_button, "Lucky Clover", 1150, lucky_clover_effect)
    robbery_kit_button.callback = lambda interaction_button: buy_item(interaction_button, "Robbery Kit", 1500, robbery_kit_effect)
    stealth_mode_button.callback = lambda interaction_button: buy_item(interaction_button, "Stealth Mode", 2000, stealth_mode_effect)
    cooldown_reduction_button.callback = lambda interaction_button: buy_item(interaction_button, "Cooldown Reduction", 2000, cooldown_reduction_effect)
    extra_spin_button.callback = lambda interaction_button: buy_item(interaction_button, "Extra Spin", 2500, extra_spin_effect)
    double_earnings_button.callback = lambda interaction_button: buy_item(interaction_button, "Double Earnings Boost", 3000, double_earnings_effect)

    view.add_item(lucky_clover_button)
    view.add_item(robbery_kit_button)
    view.add_item(stealth_mode_button)
    view.add_item(cooldown_reduction_button)
    view.add_item(extra_spin_button)
    view.add_item(double_earnings_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

def save_inventory():
    with open('user_inventory.json', 'w') as file:
        json.dump(user_inventory, file, indent=4)

def load_inventory():
    if os.path.exists('user_inventory.json'):
        with open('user_inventory.json', 'r') as file:
            return json.load(file)
    return {}

user_inventory = load_inventory()

def ensure_inventory(server_id, user_id):
    if server_id not in user_inventory:
        user_inventory[server_id] = {}
    if user_id not in user_inventory[server_id]:
        user_inventory[server_id][user_id] = {}





lottery_data = {
    "prize_pool": 100,
    "players": {},
    "end_time": (datetime.now() + timedelta(hours=12)).isoformat()
}

def load_lottery_data():
    try:
        with open('lottery_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return lottery_data

def save_lottery_data():
    with open('lottery_data.json', 'w') as file:
        json.dump(lottery_data, file, indent=4)

lottery_data = load_lottery_data()

@tasks.loop(minutes=1)
async def announce_lottery_winner():
    current_time = datetime.now()
    end_time = datetime.fromisoformat(lottery_data['end_time'])

    if current_time >= end_time:
        if lottery_data['players']:
            winner_id = secrets.choice(list(lottery_data['players'].keys()))
            winner_tickets = lottery_data['players'][winner_id]['tickets']
            total_tickets = sum(player_data['tickets'] for player_data in lottery_data['players'].values())
            winning_chance = winner_tickets / total_tickets

            server_id = lottery_data['players'][winner_id]['server_id']

            server_balances = get_server_balances(server_id)
            winner_balance = server_balances.get(winner_id, 500)
            winner_balance += lottery_data['prize_pool']
            server_balances[winner_id] = winner_balance
            save_balances()

            for player_id in lottery_data['players']:
                player = await bot.fetch_user(int(player_id))
                embed = discord.Embed(
                    title="🎉 Lottery Winner Announced!",
                    description=f"The lottery has ended, and {player.mention} won **{lottery_data['prize_pool']} coins** with a {winning_chance:.2%} chance!",
                    color=discord.Color.gold()
                )
                await player.send(embed=embed)

            lottery_data['prize_pool'] = 100
            lottery_data['players'] = {}
            lottery_data['end_time'] = (current_time + timedelta(hours=12)).isoformat()
            save_lottery_data()

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@bot.tree.command(name="lottery", description="🎟️ Check the current lottery and buy tickets!")
async def lottery(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    server_id = str(interaction.guild.id)

    current_time = datetime.now()
    end_time = datetime.fromisoformat(lottery_data['end_time'])
    remaining_time = end_time - current_time
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    embed = discord.Embed(
        title="🎟️ Lottery",
        description=(
            f"**Current Prize Pool:** {lottery_data['prize_pool']} coins\n"
            f"**Number of Players:** {len(lottery_data['players'])}\n"
            f"**Time Remaining:** {hours} hours and {minutes} minutes\n"
        ),
        color=discord.Color.blue()
    )

    buy_ticket_button = Button(label="Buy Lottery Ticket", style=discord.ButtonStyle.success, emoji="🎟️")

    async def buy_ticket_callback(interaction_button: discord.Interaction):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        server_balances = get_server_balances(server_id)
        balance = server_balances.get(user_id, 500)

        if balance < 50:
            await interaction_button.response.send_message("You don't have enough coins to buy a lottery ticket.", ephemeral=True)
            return

        balance -= 50
        server_balances[user_id] = balance
        save_balances()

        if user_id in lottery_data['players']:
            lottery_data['players'][user_id]['tickets'] += 1
        else:
            lottery_data['players'][user_id] = {"tickets": 1, "server_id": server_id}
        lottery_data['prize_pool'] += 25
        save_lottery_data()

        await interaction_button.response.send_message(
            f"🎟️ You bought a lottery ticket! You now have {lottery_data['players'][user_id]['tickets']} ticket(s).",
            ephemeral=True
        )

    buy_ticket_button.callback = buy_ticket_callback

    view = View()
    view.add_item(buy_ticket_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)



stock_market_data = None

initial_stock_market_data = {
    "LLS": {"name": "Larry's Lottery Services LTD", "price": 100.0},
    "BYTE": {"name": "Bytelabs LTD", "price": 200.0},
    "CASINO": {"name": "Bytebet Casino", "price": 150.0},
    "JCS": {"name": "Jason's Corner Store", "price": 75.0},
    "BYTECOIN": {"name": "Bytecoin", "price": 50.0},
    "HYPRK": {"name": "Hyperkoin", "price": 25.0},
}

def load_global_stock_market_data():
    global stock_market_data
    if stock_market_data is None:
        file_path = 'stock_market_data.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                stock_market_data = json.load(file)
        else:
            stock_market_data = initial_stock_market_data.copy()
            with open(file_path, 'w') as file:
                json.dump(stock_market_data, file, indent=4)

def save_global_stock_market_data():
    global stock_market_data  
    file_path = 'global_stock_market_data.json'
    with open(file_path, 'w') as file:
        json.dump(stock_market_data, file, indent=4)

user_portfolios = {}

def load_user_portfolios(server_id):
    global user_portfolios
    file_path = f'user_portfolios_{server_id}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            user_portfolios[server_id] = json.load(file)
    else:
        user_portfolios[server_id] = {}  
    return user_portfolios[server_id]  

def save_user_portfolios(server_id):
    file_path = f'user_portfolios_{server_id}.json'
    with open(file_path, 'w') as file:
        json.dump(user_portfolios[server_id], file, indent=4)

def update_stock_prices():
    global stock_market_data  

    if stock_market_data is None:
        load_global_stock_market_data()

    for symbol, data in stock_market_data.items():
        if symbol == "BYTECOIN":
            volatility = 0.5  # Bytecoin is volatile
        elif symbol == "HYPRK":
            volatility = 5.5  # Hyperkoin is even more volatile
        else:
            volatility = 0.1  # Other stocks are less volatile

        change = random.uniform(-volatility, volatility)
        data["price"] = max(0.1, data["price"] * (1 + change))  # Ensure price doesn't go below 0.1

    save_global_stock_market_data()

# Task to update stock prices every 10 minutes
@tasks.loop(minutes=10)
async def update_stock_prices_task():
    update_stock_prices()

@bot.tree.command(name="stock_market", description="View and buy stocks in the global stock market.")
async def stock_market(interaction: discord.Interaction):
    global stock_market_data

    embed = discord.Embed(
        title="📈 Stock Market",
        description="Here are the current stock prices:",
        color=discord.Color.green()
    )

    if stock_market_data:
        for symbol, data in stock_market_data.items():
            embed.add_field(
                name=f"{data['name']} ({symbol})",
                value=f"Current Price: {data['price']:.2f} coins",
                inline=False
            )
    else:
        embed.description = "No stocks available at the moment."

    buy_button = ui.Button(label="Buy Stock", style=discord.ButtonStyle.primary)

    async def buy_stock_callback(interaction_button: discord.Interaction):
        if interaction_button.user.id != interaction.user.id:
            await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
            return

        await interaction_button.response.send_modal(BuyStockModal())

    buy_button.callback = buy_stock_callback

    view = ui.View()
    view.add_item(buy_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

class BuyStockModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Buy Stock")
        self.stock_symbol = ui.TextInput(label="Stock Symbol", placeholder="Enter the stock symbol (e.g., LLS)")
        self.stock_amount = ui.TextInput(label="Amount", placeholder="Enter the number of shares", style=discord.TextStyle.short)
        self.add_item(self.stock_symbol)
        self.add_item(self.stock_amount)

    async def on_submit(self, interaction: discord.Interaction):
        global stock_market_data 

        symbol = self.stock_symbol.value.upper()
        try:
            amount = int(self.stock_amount.value)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number for the amount.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        server_id = str(interaction.guild.id)

        if stock_market_data is None:
            load_global_stock_market_data()

        if symbol not in stock_market_data:
            await interaction.response.send_message("Invalid stock symbol.", ephemeral=True)
            return

        price = stock_market_data[symbol]["price"]
        total_cost = round(price * amount)

        server_balances = get_server_balances(server_id)
        balance = server_balances.get(user_id, 500)

        if balance < total_cost:
            await interaction.response.send_message("You don't have enough coins to buy this stock.", ephemeral=True)
            return

        server_balances[user_id] = round(balance - total_cost)
        save_balances()

        if server_id not in user_portfolios:
            user_portfolios[server_id] = load_user_portfolios(server_id)

        if user_id not in user_portfolios[server_id]:
            user_portfolios[server_id][user_id] = {}

        if symbol in user_portfolios[server_id][user_id]:
            user_portfolios[server_id][user_id][symbol]["amount"] += amount
            user_portfolios[server_id][user_id][symbol]["total_invested"] += total_cost
        else:
            user_portfolios[server_id][user_id][symbol] = {"amount": amount, "total_invested": total_cost}

        save_user_portfolios(server_id)

        await interaction.response.send_message(
            f"You successfully bought {amount} shares of {symbol} for {total_cost} coins.", ephemeral=True
        )

TAX_RATE = 0.20
FINE_RATE_LOW = 0.05
FINE_RATE_HIGH = 0.10

def calculate_tax(amount):
    return amount * TAX_RATE

@bot.tree.command(name="portfolio", description="View your stock portfolio.")
async def portfolio(interaction: discord.Interaction):
    global user_portfolios
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    if server_id not in user_portfolios:
        load_user_portfolios(server_id)
    
    if user_id not in user_portfolios[server_id] or not user_portfolios[server_id][user_id]:
        await interaction.response.send_message("You don't have any stocks in your portfolio.", ephemeral=True)
        return

    embed = discord.Embed(title="💼 Your Portfolio", color=discord.Color.blue())
    total_return = 0
    view = ui.View()

    for symbol, stock_data in user_portfolios[server_id][user_id].items():
        if symbol not in stock_market_data:
            await interaction.response.send_message(f"Error: Stock symbol {symbol} not found in the market data.", ephemeral=True)
            return

        current_price = stock_market_data[symbol]["price"]
        invested = stock_data["total_invested"]
        current_value = stock_data["amount"] * current_price
        profit_loss = current_value - invested
        total_return += profit_loss

        income_after_tax = profit_loss - calculate_tax(profit_loss)
        
        embed.add_field(
            name=f"{symbol} ({stock_data['amount']} shares)",
            value=(
                f"Total Invested: {invested:.2f} coins\n"
                f"Current Value: {current_value:.2f} coins\n"
                f"Profit/Loss: {profit_loss:.2f} coins\n"
                f"Income After 20% Tax: {income_after_tax:.2f} coins"
            ),
            inline=False
        )

        sell_button = ui.Button(label=f"Sell {symbol}", style=discord.ButtonStyle.danger)

        async def sell_shares_callback(interaction_button: discord.Interaction, symbol=symbol):
            if interaction_button.user.id != interaction.user.id:
                await interaction_button.response.send_message("This button isn't for you!", ephemeral=True)
                return

            await interaction_button.response.send_modal(SellStockModal(symbol, stock_data["amount"], server_id))

        sell_button.callback = sell_shares_callback
        view.add_item(sell_button)

    embed.set_footer(text=f"Total Profit/Loss: {total_return:.2f} coins")
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

sale_info_cache = {}

class SellStockModal(ui.Modal):
    def __init__(self, symbol, max_shares, server_id):
        super().__init__(title=f"Sell {symbol}")
        self.symbol = symbol
        self.max_shares = max_shares
        self.server_id = server_id
        self.shares_to_sell = ui.TextInput(
            label="Shares to Sell",
            placeholder=f"Enter the number of shares to sell (Max: {self.max_shares})",
            style=discord.TextStyle.short
        )
        self.add_item(self.shares_to_sell)

    async def on_submit(self, interaction: discord.Interaction):
        global stock_market_data  
        global sale_info_cache  
        try:
            amount = int(self.shares_to_sell.value)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number of shares.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        server_id = self.server_id

        if amount <= 0 or amount > self.max_shares:
            await interaction.response.send_message(f"Invalid number of shares. You can sell up to {self.max_shares} shares.", ephemeral=True)
            return

        if stock_market_data is None:
            load_global_stock_market_data()

        current_price = stock_market_data[self.symbol]["price"]
        proceeds = current_price * amount

        sale_info_cache[user_id] = {
            "symbol": self.symbol,
            "amount": amount,
            "proceeds": proceeds,
            "server_id": server_id,
            "user_id": user_id
        }

        view = TaxOptionsView(proceeds, server_id, user_id)
        await view.send_earnings_summary(interaction) 

class TaxOptionsView(ui.View):
    def __init__(self, proceeds, server_id, user_id):
        super().__init__()
        self.proceeds = proceeds
        self.server_id = server_id
        self.user_id = user_id
        self.tax_rate = TAX_RATE
        self.avoid_tax_success_rate = 25  # Success rate of avoiding tax

        self.tax_amount = round(proceeds * self.tax_rate)
        self.after_tax_income = round(proceeds - self.tax_amount)
        self.avoid_tax_income = round(proceeds)

        report_income_button = ui.Button(label="Report Income", style=discord.ButtonStyle.primary)
        dont_report_tax_button = ui.Button(label="Don't Report Tax", style=discord.ButtonStyle.danger)

        report_income_button.callback = self.report_income
        dont_report_tax_button.callback = self.avoid_tax

        self.add_item(report_income_button)
        self.add_item(dont_report_tax_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("This button isn't for you!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.user_id in sale_info_cache:
            del sale_info_cache[self.user_id]

    async def report_income(self, interaction: discord.Interaction):
        server_balances = get_server_balances(self.server_id)
        server_balances[self.user_id] += self.after_tax_income  
        save_balances()

        embed = discord.Embed(
            title="💸 Tax Reported",
            description=f"Your income has been taxed at 20%. You received **{self.after_tax_income} coins**.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Thank you for being a responsible citizen!")

        await self.clear_sold_stock_from_portfolio()

        await interaction.response.send_message(embed=embed, ephemeral=False)

    async def avoid_tax(self, interaction: discord.Interaction):
        if secrets.randbelow(100) < self.avoid_tax_success_rate:
            server_balances = get_server_balances(self.server_id)
            server_balances[self.user_id] += self.avoid_tax_income  
            save_balances()

            embed = discord.Embed(
                title="💰 Successfully Avoided Tax!",
                description=f"You successfully avoided taxes and received **{self.avoid_tax_income} coins**.",
                color=discord.Color.green()
            )
            embed.set_footer(text="Luck was on your side this time...")

            await interaction.response.send_message(embed=embed, ephemeral=False)

        else:
            server_balances = get_server_balances(self.server_id)
            fine_rate = random.uniform(FINE_RATE_LOW, FINE_RATE_HIGH)
            fine_amount = round(server_balances[self.user_id] * fine_rate)
            server_balances[self.user_id] -= fine_amount
            save_balances()

            embed = discord.Embed(
                title="🚨 Caught Avoiding Taxes!",
                description=f"You were caught trying to avoid taxes! You paid a fine of **{fine_amount} coins** in addition to the tax.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Better luck next time...")

            await interaction.response.send_message(embed=embed, ephemeral=False)

        await self.clear_sold_stock_from_portfolio()

    async def clear_sold_stock_from_portfolio(self):
        sale_info = sale_info_cache.get(self.user_id)
        if not sale_info:
            return

        symbol = sale_info['symbol']
        server_id = sale_info['server_id']
        user_id = sale_info['user_id']

        user_portfolio = load_user_portfolios(server_id).get(user_id, {})
        if symbol in user_portfolio:
            stock_data = user_portfolio[symbol]
            stock_data['amount'] -= sale_info['amount']
            if stock_data['amount'] <= 0:
                del user_portfolio[symbol]  
            save_user_portfolios(server_id)
  
    async def send_earnings_summary(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💰 Earnings Summary",
            description=(
                f"**If you report your income:**\n"
                f"🪙 You will earn {self.after_tax_income} coins after taxes.\n\n"
                f"**If you successfully avoid taxes:**\n"
                f"💰 You will earn {self.avoid_tax_income} coins.\n\n"
                f"**Chance of success:**\n"
                f"🔮 {self.avoid_tax_success_rate}% chance of avoiding tax successfully."
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, view=self, ephemeral=False)




class PayView(View):
    def __init__(self, interaction: discord.Interaction, user_id: int, target_id: int, amount: int):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.user_id = str(user_id)
        self.target_id = str(target_id)
        self.amount = amount
        self.server_id = str(interaction.guild.id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("You cannot interact with these buttons.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        server_balances = get_server_balances(self.server_id)

        server_balances[self.user_id] = server_balances.get(self.user_id, 500) - self.amount
        server_balances[self.target_id] = server_balances.get(self.target_id, 500) + self.amount

        save_balances()

        payer_balance = server_balances[self.user_id]
        recipient_balance = server_balances[self.target_id]

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Payment Successful",
                description=f"You have successfully paid <@{self.target_id}> **{self.amount} coins**.\n"
                            f"💰 Your new balance: **{payer_balance} coins**.\n"
                            f"💰 <@{self.target_id}>'s new balance: **{recipient_balance} coins**.",
                color=discord.Color.green()
            )
        )
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Payment canceled.", ephemeral=True)
        self.stop()

@bot.tree.command(name="pay", description="💸 Pay another user")
async def pay(interaction: discord.Interaction, user: discord.User, amount: int):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    target_id = str(user.id)
    
    server_balances = get_server_balances(server_id)
    user_balance = server_balances.get(user_id, 0)

    if user_balance < amount and user_balance + 500 < 0:
        await interaction.response.send_message("You don't have enough coins to make this payment.", ephemeral=True)
        return

    view = PayView(interaction, int(user_id), int(target_id), amount, server_balances, save_balances)
    await interaction.response.send_message(
        f"Are you sure you want to pay {user.mention} **{amount} coins**?",
        view=view,
        ephemeral=True
    )



class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.tree.command(name="leaderboard", description="📊 Display the server's leaderboard of balances")
    async def leaderboard(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        server_balances = get_server_balances(server_id)

        sorted_balances = sorted(server_balances.items(), key=lambda item: item[1], reverse=True)
        
        embed = discord.Embed(
            title=f"💰 Leaderboard for {interaction.guild.name}",
            description="Here are the current rankings based on coin balances:",
            color=discord.Color.gold()
        )

        for index, (user_id, balance) in enumerate(sorted_balances, start=1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{index}. {user.display_name}",
                value=f"**{balance:,} coins**",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

bot.add_cog(Leaderboard(bot))


bot.run('BOT_TOKEN')
