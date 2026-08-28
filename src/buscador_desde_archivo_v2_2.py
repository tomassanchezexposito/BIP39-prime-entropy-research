#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BIP-39 / Bitcoin — Buscador desde archivo V2.2

Funciones:
1. Frase BIP-39 de 12 palabras -> dirección Bitcoin Native SegWit.
2. Dirección Bitcoin -> busca una coincidencia EXCLUSIVAMENTE entre las frases
   cargadas desde un archivo TXT, CSV o XLSX seleccionado por el usuario.
3. Valida BIP-39 antes de derivar.
4. No genera candidatas nuevas ni intenta invertir criptografía fuera del archivo.

Ruta Bitcoin por defecto:
    m/84'/0'/0'/0/0
Passphrase BIP-39 por defecto:
    vacía
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import os
import queue
import re
import threading
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

EMBEDDED_WORDLIST = """abandon
ability
able
about
above
absent
absorb
abstract
absurd
abuse
access
accident
account
accuse
achieve
acid
acoustic
acquire
across
act
action
actor
actress
actual
adapt
add
addict
address
adjust
admit
adult
advance
advice
aerobic
affair
afford
afraid
again
age
agent
agree
ahead
aim
air
airport
aisle
alarm
album
alcohol
alert
alien
all
alley
allow
almost
alone
alpha
already
also
alter
always
amateur
amazing
among
amount
amused
analyst
anchor
ancient
anger
angle
angry
animal
ankle
announce
annual
another
answer
antenna
antique
anxiety
any
apart
apology
appear
apple
approve
april
arch
arctic
area
arena
argue
arm
armed
armor
army
around
arrange
arrest
arrive
arrow
art
artefact
artist
artwork
ask
aspect
assault
asset
assist
assume
asthma
athlete
atom
attack
attend
attitude
attract
auction
audit
august
aunt
author
auto
autumn
average
avocado
avoid
awake
aware
away
awesome
awful
awkward
axis
baby
bachelor
bacon
badge
bag
balance
balcony
ball
bamboo
banana
banner
bar
barely
bargain
barrel
base
basic
basket
battle
beach
bean
beauty
because
become
beef
before
begin
behave
behind
believe
below
belt
bench
benefit
best
betray
better
between
beyond
bicycle
bid
bike
bind
biology
bird
birth
bitter
black
blade
blame
blanket
blast
bleak
bless
blind
blood
blossom
blouse
blue
blur
blush
board
boat
body
boil
bomb
bone
bonus
book
boost
border
boring
borrow
boss
bottom
bounce
box
boy
bracket
brain
brand
brass
brave
bread
breeze
brick
bridge
brief
bright
bring
brisk
broccoli
broken
bronze
broom
brother
brown
brush
bubble
buddy
budget
buffalo
build
bulb
bulk
bullet
bundle
bunker
burden
burger
burst
bus
business
busy
butter
buyer
buzz
cabbage
cabin
cable
cactus
cage
cake
call
calm
camera
camp
can
canal
cancel
candy
cannon
canoe
canvas
canyon
capable
capital
captain
car
carbon
card
cargo
carpet
carry
cart
case
cash
casino
castle
casual
cat
catalog
catch
category
cattle
caught
cause
caution
cave
ceiling
celery
cement
census
century
cereal
certain
chair
chalk
champion
change
chaos
chapter
charge
chase
chat
cheap
check
cheese
chef
cherry
chest
chicken
chief
child
chimney
choice
choose
chronic
chuckle
chunk
churn
cigar
cinnamon
circle
citizen
city
civil
claim
clap
clarify
claw
clay
clean
clerk
clever
click
client
cliff
climb
clinic
clip
clock
clog
close
cloth
cloud
clown
club
clump
cluster
clutch
coach
coast
coconut
code
coffee
coil
coin
collect
color
column
combine
come
comfort
comic
common
company
concert
conduct
confirm
congress
connect
consider
control
convince
cook
cool
copper
copy
coral
core
corn
correct
cost
cotton
couch
country
couple
course
cousin
cover
coyote
crack
cradle
craft
cram
crane
crash
crater
crawl
crazy
cream
credit
creek
crew
cricket
crime
crisp
critic
crop
cross
crouch
crowd
crucial
cruel
cruise
crumble
crunch
crush
cry
crystal
cube
culture
cup
cupboard
curious
current
curtain
curve
cushion
custom
cute
cycle
dad
damage
damp
dance
danger
daring
dash
daughter
dawn
day
deal
debate
debris
decade
december
decide
decline
decorate
decrease
deer
defense
define
defy
degree
delay
deliver
demand
demise
denial
dentist
deny
depart
depend
deposit
depth
deputy
derive
describe
desert
design
desk
despair
destroy
detail
detect
develop
device
devote
diagram
dial
diamond
diary
dice
diesel
diet
differ
digital
dignity
dilemma
dinner
dinosaur
direct
dirt
disagree
discover
disease
dish
dismiss
disorder
display
distance
divert
divide
divorce
dizzy
doctor
document
dog
doll
dolphin
domain
donate
donkey
donor
door
dose
double
dove
draft
dragon
drama
drastic
draw
dream
dress
drift
drill
drink
drip
drive
drop
drum
dry
duck
dumb
dune
during
dust
dutch
duty
dwarf
dynamic
eager
eagle
early
earn
earth
easily
east
easy
echo
ecology
economy
edge
edit
educate
effort
egg
eight
either
elbow
elder
electric
elegant
element
elephant
elevator
elite
else
embark
embody
embrace
emerge
emotion
employ
empower
empty
enable
enact
end
endless
endorse
enemy
energy
enforce
engage
engine
enhance
enjoy
enlist
enough
enrich
enroll
ensure
enter
entire
entry
envelope
episode
equal
equip
era
erase
erode
erosion
error
erupt
escape
essay
essence
estate
eternal
ethics
evidence
evil
evoke
evolve
exact
example
excess
exchange
excite
exclude
excuse
execute
exercise
exhaust
exhibit
exile
exist
exit
exotic
expand
expect
expire
explain
expose
express
extend
extra
eye
eyebrow
fabric
face
faculty
fade
faint
faith
fall
false
fame
family
famous
fan
fancy
fantasy
farm
fashion
fat
fatal
father
fatigue
fault
favorite
feature
february
federal
fee
feed
feel
female
fence
festival
fetch
fever
few
fiber
fiction
field
figure
file
film
filter
final
find
fine
finger
finish
fire
firm
first
fiscal
fish
fit
fitness
fix
flag
flame
flash
flat
flavor
flee
flight
flip
float
flock
floor
flower
fluid
flush
fly
foam
focus
fog
foil
fold
follow
food
foot
force
forest
forget
fork
fortune
forum
forward
fossil
foster
found
fox
fragile
frame
frequent
fresh
friend
fringe
frog
front
frost
frown
frozen
fruit
fuel
fun
funny
furnace
fury
future
gadget
gain
galaxy
gallery
game
gap
garage
garbage
garden
garlic
garment
gas
gasp
gate
gather
gauge
gaze
general
genius
genre
gentle
genuine
gesture
ghost
giant
gift
giggle
ginger
giraffe
girl
give
glad
glance
glare
glass
glide
glimpse
globe
gloom
glory
glove
glow
glue
goat
goddess
gold
good
goose
gorilla
gospel
gossip
govern
gown
grab
grace
grain
grant
grape
grass
gravity
great
green
grid
grief
grit
grocery
group
grow
grunt
guard
guess
guide
guilt
guitar
gun
gym
habit
hair
half
hammer
hamster
hand
happy
harbor
hard
harsh
harvest
hat
have
hawk
hazard
head
health
heart
heavy
hedgehog
height
hello
helmet
help
hen
hero
hidden
high
hill
hint
hip
hire
history
hobby
hockey
hold
hole
holiday
hollow
home
honey
hood
hope
horn
horror
horse
hospital
host
hotel
hour
hover
hub
huge
human
humble
humor
hundred
hungry
hunt
hurdle
hurry
hurt
husband
hybrid
ice
icon
idea
identify
idle
ignore
ill
illegal
illness
image
imitate
immense
immune
impact
impose
improve
impulse
inch
include
income
increase
index
indicate
indoor
industry
infant
inflict
inform
inhale
inherit
initial
inject
injury
inmate
inner
innocent
input
inquiry
insane
insect
inside
inspire
install
intact
interest
into
invest
invite
involve
iron
island
isolate
issue
item
ivory
jacket
jaguar
jar
jazz
jealous
jeans
jelly
jewel
job
join
joke
journey
joy
judge
juice
jump
jungle
junior
junk
just
kangaroo
keen
keep
ketchup
key
kick
kid
kidney
kind
kingdom
kiss
kit
kitchen
kite
kitten
kiwi
knee
knife
knock
know
lab
label
labor
ladder
lady
lake
lamp
language
laptop
large
later
latin
laugh
laundry
lava
law
lawn
lawsuit
layer
lazy
leader
leaf
learn
leave
lecture
left
leg
legal
legend
leisure
lemon
lend
length
lens
leopard
lesson
letter
level
liar
liberty
library
license
life
lift
light
like
limb
limit
link
lion
liquid
list
little
live
lizard
load
loan
lobster
local
lock
logic
lonely
long
loop
lottery
loud
lounge
love
loyal
lucky
luggage
lumber
lunar
lunch
luxury
lyrics
machine
mad
magic
magnet
maid
mail
main
major
make
mammal
man
manage
mandate
mango
mansion
manual
maple
marble
march
margin
marine
market
marriage
mask
mass
master
match
material
math
matrix
matter
maximum
maze
meadow
mean
measure
meat
mechanic
medal
media
melody
melt
member
memory
mention
menu
mercy
merge
merit
merry
mesh
message
metal
method
middle
midnight
milk
million
mimic
mind
minimum
minor
minute
miracle
mirror
misery
miss
mistake
mix
mixed
mixture
mobile
model
modify
mom
moment
monitor
monkey
monster
month
moon
moral
more
morning
mosquito
mother
motion
motor
mountain
mouse
move
movie
much
muffin
mule
multiply
muscle
museum
mushroom
music
must
mutual
myself
mystery
myth
naive
name
napkin
narrow
nasty
nation
nature
near
neck
need
negative
neglect
neither
nephew
nerve
nest
net
network
neutral
never
news
next
nice
night
noble
noise
nominee
noodle
normal
north
nose
notable
note
nothing
notice
novel
now
nuclear
number
nurse
nut
oak
obey
object
oblige
obscure
observe
obtain
obvious
occur
ocean
october
odor
off
offer
office
often
oil
okay
old
olive
olympic
omit
once
one
onion
online
only
open
opera
opinion
oppose
option
orange
orbit
orchard
order
ordinary
organ
orient
original
orphan
ostrich
other
outdoor
outer
output
outside
oval
oven
over
own
owner
oxygen
oyster
ozone
pact
paddle
page
pair
palace
palm
panda
panel
panic
panther
paper
parade
parent
park
parrot
party
pass
patch
path
patient
patrol
pattern
pause
pave
payment
peace
peanut
pear
peasant
pelican
pen
penalty
pencil
people
pepper
perfect
permit
person
pet
phone
photo
phrase
physical
piano
picnic
picture
piece
pig
pigeon
pill
pilot
pink
pioneer
pipe
pistol
pitch
pizza
place
planet
plastic
plate
play
please
pledge
pluck
plug
plunge
poem
poet
point
polar
pole
police
pond
pony
pool
popular
portion
position
possible
post
potato
pottery
poverty
powder
power
practice
praise
predict
prefer
prepare
present
pretty
prevent
price
pride
primary
print
priority
prison
private
prize
problem
process
produce
profit
program
project
promote
proof
property
prosper
protect
proud
provide
public
pudding
pull
pulp
pulse
pumpkin
punch
pupil
puppy
purchase
purity
purpose
purse
push
put
puzzle
pyramid
quality
quantum
quarter
question
quick
quit
quiz
quote
rabbit
raccoon
race
rack
radar
radio
rail
rain
raise
rally
ramp
ranch
random
range
rapid
rare
rate
rather
raven
raw
razor
ready
real
reason
rebel
rebuild
recall
receive
recipe
record
recycle
reduce
reflect
reform
refuse
region
regret
regular
reject
relax
release
relief
rely
remain
remember
remind
remove
render
renew
rent
reopen
repair
repeat
replace
report
require
rescue
resemble
resist
resource
response
result
retire
retreat
return
reunion
reveal
review
reward
rhythm
rib
ribbon
rice
rich
ride
ridge
rifle
right
rigid
ring
riot
ripple
risk
ritual
rival
river
road
roast
robot
robust
rocket
romance
roof
rookie
room
rose
rotate
rough
round
route
royal
rubber
rude
rug
rule
run
runway
rural
sad
saddle
sadness
safe
sail
salad
salmon
salon
salt
salute
same
sample
sand
satisfy
satoshi
sauce
sausage
save
say
scale
scan
scare
scatter
scene
scheme
school
science
scissors
scorpion
scout
scrap
screen
script
scrub
sea
search
season
seat
second
secret
section
security
seed
seek
segment
select
sell
seminar
senior
sense
sentence
series
service
session
settle
setup
seven
shadow
shaft
shallow
share
shed
shell
sheriff
shield
shift
shine
ship
shiver
shock
shoe
shoot
shop
short
shoulder
shove
shrimp
shrug
shuffle
shy
sibling
sick
side
siege
sight
sign
silent
silk
silly
silver
similar
simple
since
sing
siren
sister
situate
six
size
skate
sketch
ski
skill
skin
skirt
skull
slab
slam
sleep
slender
slice
slide
slight
slim
slogan
slot
slow
slush
small
smart
smile
smoke
smooth
snack
snake
snap
sniff
snow
soap
soccer
social
sock
soda
soft
solar
soldier
solid
solution
solve
someone
song
soon
sorry
sort
soul
sound
soup
source
south
space
spare
spatial
spawn
speak
special
speed
spell
spend
sphere
spice
spider
spike
spin
spirit
split
spoil
sponsor
spoon
sport
spot
spray
spread
spring
spy
square
squeeze
squirrel
stable
stadium
staff
stage
stairs
stamp
stand
start
state
stay
steak
steel
stem
step
stereo
stick
still
sting
stock
stomach
stone
stool
story
stove
strategy
street
strike
strong
struggle
student
stuff
stumble
style
subject
submit
subway
success
such
sudden
suffer
sugar
suggest
suit
summer
sun
sunny
sunset
super
supply
supreme
sure
surface
surge
surprise
surround
survey
suspect
sustain
swallow
swamp
swap
swarm
swear
sweet
swift
swim
swing
switch
sword
symbol
symptom
syrup
system
table
tackle
tag
tail
talent
talk
tank
tape
target
task
taste
tattoo
taxi
teach
team
tell
ten
tenant
tennis
tent
term
test
text
thank
that
theme
then
theory
there
they
thing
this
thought
three
thrive
throw
thumb
thunder
ticket
tide
tiger
tilt
timber
time
tiny
tip
tired
tissue
title
toast
tobacco
today
toddler
toe
together
toilet
token
tomato
tomorrow
tone
tongue
tonight
tool
tooth
top
topic
topple
torch
tornado
tortoise
toss
total
tourist
toward
tower
town
toy
track
trade
traffic
tragic
train
transfer
trap
trash
travel
tray
treat
tree
trend
trial
tribe
trick
trigger
trim
trip
trophy
trouble
truck
true
truly
trumpet
trust
truth
try
tube
tuition
tumble
tuna
tunnel
turkey
turn
turtle
twelve
twenty
twice
twin
twist
two
type
typical
ugly
umbrella
unable
unaware
uncle
uncover
under
undo
unfair
unfold
unhappy
uniform
unique
unit
universe
unknown
unlock
until
unusual
unveil
update
upgrade
uphold
upon
upper
upset
urban
urge
usage
use
used
useful
useless
usual
utility
vacant
vacuum
vague
valid
valley
valve
van
vanish
vapor
various
vast
vault
vehicle
velvet
vendor
venture
venue
verb
verify
version
very
vessel
veteran
viable
vibrant
vicious
victory
video
view
village
vintage
violin
virtual
virus
visa
visit
visual
vital
vivid
vocal
voice
void
volcano
volume
vote
voyage
wage
wagon
wait
walk
wall
walnut
want
warfare
warm
warrior
wash
wasp
waste
water
wave
way
wealth
weapon
wear
weasel
weather
web
wedding
weekend
weird
welcome
west
wet
whale
what
wheat
wheel
when
where
whip
whisper
wide
width
wife
wild
will
win
window
wine
wing
wink
winner
winter
wire
wisdom
wise
wish
witness
wolf
woman
wonder
wood
wool
word
work
world
worry
worth
wrap
wreck
wrestle
wrist
write
wrong
yard
year
yellow
you
young
youth
zebra
zero
zone
zoo"""

BTC_PATH_DEFAULT = "m/84'/0'/0'/0/0"

FIELD_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
CURVE_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)
BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def load_words():
    words = [x.strip() for x in EMBEDDED_WORDLIST.splitlines() if x.strip()]
    if len(words) != 2048 or len(set(words)) != 2048:
        raise ValueError("La lista BIP-39 interna no contiene exactamente 2048 palabras únicas.")
    return words


def normalize_mnemonic(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", str(text).strip()).split())


def mnemonic_details(mnemonic: str, words: list[str]) -> dict:
    mnemonic = normalize_mnemonic(mnemonic)
    parts = mnemonic.split()
    if len(parts) != 12:
        raise ValueError("Se requieren exactamente 12 palabras BIP-39.")

    lookup = {w: i for i, w in enumerate(words)}
    if any(w not in lookup for w in parts):
        raise ValueError("La frase contiene palabras fuera de la lista BIP-39 inglesa.")

    indexes = [lookup[w] for w in parts]
    combined = 0
    for idx in indexes:
        combined = (combined << 11) | idx

    checksum = combined & 0xF
    entropy_int = combined >> 4
    entropy_bytes = entropy_int.to_bytes(16, "big")
    expected_checksum = hashlib.sha256(entropy_bytes).digest()[0] >> 4

    return {
        "mnemonic": mnemonic,
        "words": parts,
        "indexes": indexes,
        "positions": [i + 1 for i in indexes],
        "entropy_hex": entropy_bytes.hex(),
        "checksum_bits": f"{checksum:04b}",
        "expected_checksum_bits": f"{expected_checksum:04b}",
        "valid": checksum == expected_checksum,
    }


# -------------------------- secp256k1 / BIP32 -------------------------------

def inv_mod(a: int, p: int = FIELD_P) -> int:
    return pow(a, p - 2, p)


def point_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    x1, y1 = a
    x2, y2 = b

    if x1 == x2 and (y1 + y2) % FIELD_P == 0:
        return None

    if a == b:
        slope = (3 * x1 * x1) * inv_mod(2 * y1) % FIELD_P
    else:
        slope = (y2 - y1) * inv_mod((x2 - x1) % FIELD_P) % FIELD_P

    x3 = (slope * slope - x1 - x2) % FIELD_P
    y3 = (slope * (x1 - x3) - y1) % FIELD_P
    return x3, y3


def point_mul(k: int, point=G):
    if not (0 < k < CURVE_N):
        raise ValueError("Escalar secp256k1 fuera de rango.")
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


def compressed_pubkey(point) -> bytes:
    x, y = point
    return bytes([2 + (y & 1)]) + x.to_bytes(32, "big")


def bip39_seed(mnemonic: str, passphrase: str = "") -> bytes:
    m = unicodedata.normalize("NFKD", normalize_mnemonic(mnemonic))
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac(
        "sha512",
        m.encode("utf-8"),
        salt.encode("utf-8"),
        2048,
        dklen=64,
    )


def parse_path(path: str) -> list[int]:
    path = path.strip()
    if not path.startswith("m/"):
        raise ValueError("La ruta debe comenzar por m/.")

    out = []
    for component in path[2:].split("/"):
        hardened = component.endswith(("'", "h", "H"))
        if hardened:
            component = component[:-1]
        if not component.isdigit():
            raise ValueError(f"Componente inválido en la ruta: {component!r}")
        n = int(component)
        if n >= 0x80000000:
            raise ValueError("Índice de derivación demasiado grande.")
        if hardened:
            n += 0x80000000
        out.append(n)
    return out


def master_key_from_seed(seed: bytes) -> tuple[int, bytes]:
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key = int.from_bytes(I[:32], "big")
    chain = I[32:]
    if key == 0 or key >= CURVE_N:
        raise ValueError("Clave maestra inválida.")
    return key, chain


def ckd_priv(key: int, chain: bytes, index: int) -> tuple[int, bytes]:
    if index >= 0x80000000:
        data = b"\x00" + key.to_bytes(32, "big") + index.to_bytes(4, "big")
    else:
        data = compressed_pubkey(point_mul(key)) + index.to_bytes(4, "big")

    I = hmac.new(chain, data, hashlib.sha512).digest()
    left = int.from_bytes(I[:32], "big")
    child = (left + key) % CURVE_N

    if left >= CURVE_N or child == 0:
        raise ValueError("Derivación BIP-32 inválida para este índice.")
    return child, I[32:]


def derive_private_key(seed: bytes, path: str) -> int:
    key, chain = master_key_from_seed(seed)
    for index in parse_path(path):
        key, chain = ckd_priv(key, chain, index)
    return key


# ----------------------------- Bitcoin Bech32 -------------------------------

def hash160(data: bytes) -> bytes:
    return hashlib.new("ripemd160", hashlib.sha256(data).digest()).digest()


def bech32_polymod(values):
    generators = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ v
        for i, generator in enumerate(generators):
            if (top >> i) & 1:
                chk ^= generator
    return chk


def bech32_hrp_expand(hrp: str):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def convertbits(data: bytes, frombits=8, tobits=5, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1

    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)

    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)

    return ret


def bech32_encode(hrp: str, data: list[int]) -> str:
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0] * 6) ^ 1
    checksum = [(polymod >> (5 * (5 - i))) & 31 for i in range(6)]
    return hrp + "1" + "".join(BECH32_CHARSET[d] for d in data + checksum)


def p2wpkh_address(pubkey: bytes) -> str:
    witness_program = hash160(pubkey)
    data = [0] + convertbits(witness_program, 8, 5, True)
    return bech32_encode("bc", data)


def derive_btc_address(
    mnemonic: str,
    words: list[str],
    passphrase: str = "",
    path: str = BTC_PATH_DEFAULT,
) -> dict:
    details = mnemonic_details(mnemonic, words)
    if not details["valid"]:
        raise ValueError(
            "Checksum BIP-39 inválido "
            f"(incluido {details['checksum_bits']}, esperado {details['expected_checksum_bits']})."
        )

    seed = bip39_seed(details["mnemonic"], passphrase)
    private_key = derive_private_key(seed, path)
    pubkey = compressed_pubkey(point_mul(private_key))
    address = p2wpkh_address(pubkey)

    return {**details, "address": address}


# ----------------------- Lectura de archivo de candidatas -------------------

def candidate_from_tokens(tokens, valid_words):
    tokens = [normalize_mnemonic(x) for x in tokens if str(x).strip()]

    # Caso 1: una celda/campo contiene toda la mnemonic.
    for value in tokens:
        parts = value.split()
        if len(parts) == 12 and all(w in valid_words for w in parts):
            yield " ".join(parts)

    # Caso 2: una fila tiene 12 palabras separadas en columnas.
    flat = []
    for value in tokens:
        flat.extend(value.split())

    if len(flat) == 12 and all(w in valid_words for w in flat):
        yield " ".join(flat)


def load_txt(path: Path, valid_words: set[str]):
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = normalize_mnemonic(line)
        if not line:
            continue

        # Línea completa.
        parts = line.split()
        if len(parts) == 12 and all(w in valid_words for w in parts):
            yield line
            continue

        # Por si hay prefijo/ID antes de la frase: buscar una ventana exacta de 12
        # palabras BIP39 consecutivas dentro de la línea.
        raw = re.findall(r"[a-z]+", line.lower())
        for i in range(0, max(0, len(raw) - 11)):
            block = raw[i:i+12]
            if len(block) == 12 and all(w in valid_words for w in block):
                yield " ".join(block)


def load_csv_file(path: Path, valid_words: set[str]):
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except Exception:
            dialect = csv.excel

        for row in csv.reader(f, dialect):
            yield from candidate_from_tokens(row, valid_words)


def _xlsx_col_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref or "")
    if not letters:
        return 0
    n = 0
    for ch in letters.group(0):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def load_xlsx_file(path: Path, valid_words: set[str]):
    NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

    with zipfile.ZipFile(path, "r") as z:
        shared = []

        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(NS + "si"):
                texts = [t.text or "" for t in si.iter(NS + "t")]
                shared.append("".join(texts))

        sheet_names = sorted(
            name for name in z.namelist()
            if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name)
        )

        for sheet_name in sheet_names:
            root = ET.fromstring(z.read(sheet_name))

            for row in root.iter(NS + "row"):
                values = []
                for cell in row.findall(NS + "c"):
                    ctype = cell.get("t")
                    value = ""

                    if ctype == "inlineStr":
                        texts = [t.text or "" for t in cell.iter(NS + "t")]
                        value = "".join(texts)
                    else:
                        v = cell.find(NS + "v")
                        if v is not None and v.text is not None:
                            if ctype == "s":
                                try:
                                    value = shared[int(v.text)]
                                except Exception:
                                    value = ""
                            else:
                                value = v.text

                    values.append(value)

                yield from candidate_from_tokens(values, valid_words)


def load_candidate_file(path: Path, words: list[str]) -> tuple[list[str], dict]:
    valid_words = set(words)
    suffix = path.suffix.lower()

    if suffix in (".txt", ".log", ".md"):
        iterator = load_txt(path, valid_words)
    elif suffix in (".csv", ".tsv"):
        iterator = load_csv_file(path, valid_words)
    elif suffix == ".xlsx":
        iterator = load_xlsx_file(path, valid_words)
    else:
        raise ValueError("Formato no admitido. Utiliza TXT, CSV, TSV o XLSX.")

    seen = set()
    valid = []
    raw_candidates = 0
    invalid_checksum = 0

    for phrase in iterator:
        raw_candidates += 1
        phrase = normalize_mnemonic(phrase)
        if phrase in seen:
            continue
        seen.add(phrase)

        try:
            details = mnemonic_details(phrase, words)
        except Exception:
            continue

        if details["valid"]:
            valid.append(phrase)
        else:
            invalid_checksum += 1

    return valid, {
        "raw_candidates": raw_candidates,
        "unique_seen": len(seen),
        "valid_bip39": len(valid),
        "invalid_checksum": invalid_checksum,
    }


# ----------------------------------- GUI ------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BIP-39 / Bitcoin — buscador de frase desde archivo V2.2")
        self.geometry("1180x880")
        self.minsize(1000, 740)

        self.words = load_words()
        self.candidates = []
        self.candidate_file = None
        self.searching = False
        self.stop_event = threading.Event()
        self.progress_queue = queue.Queue()

        self._build()
        self.after(100, self._poll_progress)

    def _build(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="BIP-39 / Bitcoin — buscar una frase dentro de un archivo de candidatas",
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            text=(
                "La aplicación no invierte una dirección Bitcoin. Carga un archivo finito de "
                "frases candidatas y calcula la dirección de cada frase BIP-39 válida hasta "
                "encontrar una coincidencia."
            ),
            wraplength=1140,
            justify="left",
        ).pack(anchor="w", pady=(5, 12))

        file_frame = ttk.LabelFrame(main, text="1. Archivo de frases candidatas", padding=10)
        file_frame.pack(fill="x")

        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(file_frame, text="Seleccionar archivo…", command=self.select_file).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(file_frame, text="Recargar", command=self.reload_file).pack(
            side="left", padx=(8, 0)
        )

        self.file_info_var = tk.StringVar(value="No se ha cargado ningún archivo.")
        ttk.Label(file_frame, textvariable=self.file_info_var).pack(
            anchor="w", side="bottom", fill="x", pady=(8, 0)
        )

        params = ttk.LabelFrame(main, text="2. Parámetros de derivación", padding=10)
        params.pack(fill="x", pady=(12, 0))

        ttk.Label(params, text="Ruta Bitcoin:").grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar(value=BTC_PATH_DEFAULT)
        ttk.Entry(params, textvariable=self.path_var, width=28).grid(
            row=0, column=1, padx=(8, 20), sticky="w"
        )

        ttk.Label(params, text="Passphrase BIP-39:").grid(row=0, column=2, sticky="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(params, textvariable=self.pass_var, width=35, show="•").grid(
            row=0, column=3, padx=(8, 0), sticky="ew"
        )
        params.columnconfigure(3, weight=1)

        search = ttk.LabelFrame(main, text="3. Dirección Bitcoin a buscar", padding=10)
        search.pack(fill="x", pady=(12, 0))

        self.addr_var = tk.StringVar()
        ttk.Entry(search, textvariable=self.addr_var).pack(side="left", fill="x", expand=True)

        self.search_btn = ttk.Button(search, text="Buscar frase en el archivo", command=self.start_search)
        self.search_btn.pack(side="left", padx=(8, 0))

        self.stop_btn = ttk.Button(search, text="Detener", command=self.stop_search, state="disabled")
        self.stop_btn.pack(side="left", padx=(8, 0))

        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill="x", pady=(10, 0))

        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(main, textvariable=self.status_var).pack(anchor="w", pady=(5, 0))

        phrase_frame = ttk.LabelFrame(
            main,
            text="4. Derivar una dirección desde una frase individual",
            padding=10,
        )
        phrase_frame.pack(fill="x", pady=(12, 0))

        self.mnemonic_text = tk.Text(phrase_frame, height=3, wrap="word")
        self.mnemonic_text.pack(fill="x")
        ttk.Button(
            phrase_frame,
            text="Calcular dirección Bitcoin",
            command=self.derive_single,
        ).pack(anchor="w", pady=(8, 0))

        result = ttk.LabelFrame(main, text="Resultado", padding=10)
        result.pack(fill="both", expand=True, pady=(12, 0))

        self.output = tk.Text(result, wrap="word", state="disabled")
        self.output.pack(fill="both", expand=True)

    def set_output(self, text: str):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Selecciona el archivo con las frases semilla",
            filetypes=[
                ("Archivos admitidos", "*.txt *.csv *.tsv *.xlsx"),
                ("Texto", "*.txt"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not path:
            return

        self.candidate_file = Path(path)
        self.file_var.set(str(self.candidate_file))
        self.reload_file()

    def reload_file(self):
        if not self.candidate_file:
            messagebox.showwarning("Sin archivo", "Selecciona primero un archivo.")
            return

        try:
            self.status_var.set("Cargando y validando frases…")
            self.update_idletasks()

            candidates, stats = load_candidate_file(self.candidate_file, self.words)
            self.candidates = candidates

            self.file_info_var.set(
                f"Frases detectadas: {stats['raw_candidates']} · "
                f"únicas: {stats['unique_seen']} · "
                f"BIP-39 válidas: {stats['valid_bip39']} · "
                f"checksum inválido: {stats['invalid_checksum']}"
            )
            self.status_var.set(f"Archivo cargado: {len(candidates)} frases BIP-39 válidas.")
            self.progress["value"] = 0

            self.set_output(
                f"Archivo:\n{self.candidate_file}\n\n"
                f"Frases BIP-39 válidas disponibles para la búsqueda: {len(candidates)}\n\n"
                "Introduce una dirección Bitcoin y pulsa «Buscar frase en el archivo»."
            )

        except Exception as exc:
            self.candidates = []
            self.status_var.set("Error al cargar el archivo")
            messagebox.showerror("Error", str(exc))

    def start_search(self):
        if self.searching:
            return

        address = self.addr_var.get().strip().lower()
        if not address.startswith("bc1"):
            messagebox.showwarning(
                "Dirección inválida",
                "Introduce una dirección Bitcoin Native SegWit que empiece por bc1.",
            )
            return

        if not self.candidates:
            messagebox.showwarning(
                "Sin candidatas",
                "Selecciona primero un archivo que contenga frases BIP-39 válidas.",
            )
            return

        try:
            parse_path(self.path_var.get())
        except Exception as exc:
            messagebox.showerror("Ruta inválida", str(exc))
            return

        self.searching = True
        self.stop_event.clear()
        self.search_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        self.progress["maximum"] = len(self.candidates)
        self.progress["value"] = 0
        self.status_var.set(f"Buscando entre {len(self.candidates)} frases…")
        self.set_output("Búsqueda en curso…")

        passphrase = self.pass_var.get()
        path = self.path_var.get()

        def worker():
            found = None
            error = None

            try:
                for i, mnemonic in enumerate(self.candidates, start=1):
                    if self.stop_event.is_set():
                        self.progress_queue.put(("stopped", i - 1, None))
                        return

                    try:
                        result = derive_btc_address(
                            mnemonic,
                            self.words,
                            passphrase=passphrase,
                            path=path,
                        )
                    except Exception:
                        continue

                    if i == 1 or i % 10 == 0 or i == len(self.candidates):
                        self.progress_queue.put(("progress", i, None))

                    if result["address"].lower() == address:
                        found = result
                        self.progress_queue.put(("found", i, found))
                        return

                self.progress_queue.put(("not_found", len(self.candidates), None))

            except Exception as exc:
                error = exc
                self.progress_queue.put(("error", 0, error))

        threading.Thread(target=worker, daemon=True).start()

    def stop_search(self):
        if self.searching:
            self.stop_event.set()
            self.status_var.set("Deteniendo búsqueda…")

    def _poll_progress(self):
        try:
            while True:
                kind, value, payload = self.progress_queue.get_nowait()

                if kind == "progress":
                    self.progress["value"] = value
                    self.status_var.set(
                        f"Probadas {value} / {len(self.candidates)} frases…"
                    )

                elif kind == "found":
                    self.progress["value"] = value
                    self.searching = False
                    self.search_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")

                    result = payload
                    self.mnemonic_text.delete("1.0", "end")
                    self.mnemonic_text.insert("1.0", result["mnemonic"])

                    self.status_var.set(
                        f"COINCIDENCIA ENCONTRADA — candidata {value} de {len(self.candidates)}"
                    )
                    self.set_output(
                        f"Dirección buscada:\n{result['address']}\n\n"
                        f"Frase encontrada en el archivo:\n{result['mnemonic']}\n\n"
                        f"Entropía BIP-39:\n{result['entropy_hex']}\n"
                        f"Checksum: {result['checksum_bits']}\n"
                        f"Ruta: {self.path_var.get()}\n\n"
                        "La frase se encontró porque estaba incluida en el archivo cargado."
                    )

                elif kind == "not_found":
                    self.progress["value"] = value
                    self.searching = False
                    self.search_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")

                    self.status_var.set("Sin coincidencia")
                    self.set_output(
                        f"Se han probado {value} frases BIP-39 válidas y ninguna genera "
                        f"la dirección:\n{self.addr_var.get().strip()}\n\n"
                        "Comprueba que la frase buscada esté realmente en el archivo y que "
                        "la passphrase, ruta de derivación y tipo de dirección sean correctos."
                    )

                elif kind == "stopped":
                    self.progress["value"] = value
                    self.searching = False
                    self.search_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.status_var.set(f"Búsqueda detenida tras {value} candidatas.")

                elif kind == "error":
                    self.searching = False
                    self.search_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.status_var.set("Error durante la búsqueda")
                    messagebox.showerror("Error", str(payload))

        except queue.Empty:
            pass

        self.after(100, self._poll_progress)

    def derive_single(self):
        mnemonic = normalize_mnemonic(self.mnemonic_text.get("1.0", "end"))
        try:
            result = derive_btc_address(
                mnemonic,
                self.words,
                passphrase=self.pass_var.get(),
                path=self.path_var.get(),
            )

            self.status_var.set("Dirección calculada correctamente")
            self.set_output(
                f"Frase:\n{result['mnemonic']}\n\n"
                f"Dirección Bitcoin:\n{result['address']}\n\n"
                f"Entropía BIP-39:\n{result['entropy_hex']}\n"
                f"Checksum: {result['checksum_bits']}\n"
                f"Ruta: {self.path_var.get()}"
            )

        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def main():
    App().mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error al iniciar la aplicación",
                f"{type(exc).__name__}: {exc}",
            )
            root.destroy()
        except Exception:
            print(f"ERROR: {type(exc).__name__}: {exc}")
            try:
                input("Pulsa ENTER para cerrar…")
            except Exception:
                pass
