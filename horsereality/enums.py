from enum import Enum


__all__ = (
    'Breed',
    'BreedOrders',
    'LayerType',
)


class Breed(Enum):
    akhal_teke = 'Akhal-Teke'
    arabian_horse = 'Arabian Horse'
    brabant_horse = 'Brabant Horse'
    brumby_horse = 'Brumby Horse'
    camargue_horse = 'Camargue Horse'
    cleveland_bay = 'Cleveland Bay'
    exmoor_pony = 'Exmoor Pony'
    finnhorse = 'Finnhorse'
    fjord_horse = 'Fjord Horse'
    friesian_horse = 'Friesian Horse'
    haflinger_horse = 'Haflinger Horse'
    icelandic_horse = 'Icelandic Horse'
    irish_cob_horse = 'Irish Cob Horse'
    kladruber_horse = 'Kladruber Horse'
    knabstrupper = 'Knabstrupper'
    lusitano = 'Lusitano'
    mustang_horse = 'Mustang Horse'
    namib_desert_horse = 'Namib Desert Horse'
    noriker_horse = 'Noriker Horse'
    norman_cob = 'Norman Cob'
    oldenburg_horse = 'Oldenburg Horse'
    pura_raza_española = 'Pura Raza Española'
    quarter_horse = 'Quarter Horse'
    shire_horse = 'Shire Horse'
    suffolk_punch = 'Suffolk Punch'
    thoroughbred = 'Thoroughbred'
    trakehner_horse = 'Trakehner Horse'
    welsh_pony = 'Welsh Pony'


class BreedOrders(Enum):
    akhal_teke = {
        'stallion': ['tail', 'mane', 'body'],
        'mare': ['mane', 'body', 'tail']
    }
    arabian_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['body', 'tail', 'mane']
    }
    brabant_horse = {
        'stallion': ['body', 'tail', 'mane'],
        'mare': ['body', 'tail', 'mane']
    }
    brumby_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    camargue_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    cleveland_bay = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    exmoor_pony = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['tail', 'body', 'mane']
    }
    finnhorse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    fjord_horse = {
        'stallion': ['body', 'tail', 'mane'],
        'mare': ['body', 'tail', 'mane']
    }
    friesian_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    haflinger_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    icelandic_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    irish_cob_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    kladruber_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    knabstrupper = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    lusitano = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['tail', 'body', 'mane']
    }
    mustang_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    namib_desert_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    noriker_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    norman_cob = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    oldenburg_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    pura_raza_española = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    quarter_horse = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['body', 'mane', 'tail']
    }
    shire_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    suffolk_punch = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    thoroughbred = {
        'stallion': ['tail', 'body', 'mane'],
        'mare': ['tail', 'body', 'mane']
    }
    trakehner_horse = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }
    welsh_pony = {
        'stallion': ['body', 'mane', 'tail'],
        'mare': ['body', 'mane', 'tail']
    }


class LayerType(Enum):
    colours = 'colours'
    colors = 'colours'
    whites = 'whites'
