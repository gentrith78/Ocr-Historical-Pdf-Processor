from dataclasses import dataclass, field

known_columns = [
    'Control',
    'Service',
    'Stay',
    'Beds',
    'Admissions',
    'Census',
    'Bassinets',
    'Births',
    'Newborn Census',
    'Total',
    'Payroll',
    'Personnel',
]

state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado",
               "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam",
               "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana",
               "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi",
               "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey",
               "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico",
               "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia",
               "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]


@dataclass
class Property:
    page:int
    star:str
    state:str
    conty:str
    city:str
    name:str
    est:int
    tel:str
    address:str
    adm:str
    facility:str
    ownership_control:str = field(default='')
    service_type:str = field(default='')
    length_stay:str = field(default='')
    beds:str = field(default='')
    admissions:str = field(default='')
    avg_daily_census:str = field(default='')
    bassinets:str = field(default='')
    births:str = field(default='')
    newborn_census:str = field(default='')
    tot_exp:str = field(default='')
    payroll:str = field(default='')
    paid_person:str = field(default='')
    intern_res_student:str = field(default='')


@dataclass
class Comparison_Instance:
    column_value: str
    column_name: str
    substract_value: int



@dataclass
class WordData:
    text:str
    TL: tuple
    TR: tuple

@dataclass
class Threshold:
    pass

